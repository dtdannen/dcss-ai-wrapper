"""
Trains a PPO agent on DCSSGymEnv (stage 1: explore floor 1).

Follows the same setup conventions as run_random_episode.py: single import of
DCSSGymEnv, constructed with radius=3. Requires a running DCSS webtiles server
(the Docker container) before starting - this connects to a real, live game.
"""

import os
import traceback

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

from dcss.rl.dcss_gym_env import DCSSGymEnv


# --- Ablation toggle --------------------------------------------------------
# False = hand the raw env to PPO exactly as PPO_2 through PPO_6 did.
FIX_OBS_NORMALIZATION = True
# ----------------------------------------------------------------------------


# --- Training config ---
# FIXED-MAP VARIANCE TEST. Every prior run has shown cells-explored per episode drifting
# down across its own thirds, but the noise floor has always been large enough to make
# that ambiguous: two runs with an IDENTICAL reward function once differed ~80% at the
# same step, purely from map-to-map luck.
#
# So this run removes map variance entirely (USE_FIXED_SEED=True in dcss_gym_env.py -
# same seed, same character, same floor every episode) and asks one question:
#
#     with map luck eliminated, does the within-run decline survive?
#
# Yes  -> the drift is a real optimisation problem (policy converging on a worse
#         strategy) and the next move is entropy regularisation, not more observation.
# No   -> we have been chasing noise across PPO_4 through the frontier run, and every
#         "decline" reported so far needs re-reading.
#
# Everything else is held identical to the frontier run: all twelve flags as-is,
# frontier features ON, cap 2000, gamma 0.999, config A rewards.
#
# Caveats when reading the result:
#  - 50k / 2000 = ~25 episodes, so ~8 per third. Thin, but the dominant noise source is
#    gone, which is the whole point of fixing the seed.
#  - Fixed map means a FINITE ceiling on cells reachable per episode. If the agent ever
#    approaches full-floor coverage, cells/step flattens for a benign reason - check the
#    absolute cells/ep against the floor size before calling a plateau a decline.
#  - Not comparable to unseeded runs on absolute cells/step; this seed reveals 141 cells
#    at spawn and a random walk finds nothing new for its first ~100 steps.
TOTAL_TIMESTEPS = 50000   # ~1 h plus ~25 x 11s seeded restarts
N_STEPS = 2048  # PPO's standard rollout length per update
CHECKPOINT_FREQ = 2000  # save a checkpoint every ~2000 steps, frequent given the longer run

MODELS_DIR = os.path.join("models", "ppo_dcss")
CHECKPOINT_DIR = os.path.join(MODELS_DIR, "checkpoints")
FINAL_MODEL_PATH = os.path.join(MODELS_DIR, "ppo_dcss_final")

# --- Resume ------------------------------------------------------------------
# Set both to continue a run that stopped early. TOTAL_TIMESTEPS stays the TOTAL
# target across the whole training history, not the number of additional steps -
# SB3 adds the loaded model's num_timesteps when reset_num_timesteps=False, so the
# remaining budget is computed below.
#
# RESUME_VECNORMALIZE must be the checkpoint's PAIRED .pkl. Resuming the policy
# without its running mean/var re-scales every observation wrongly - no error, just a
# silently worse agent, which is why CheckpointCallback(save_vecnormalize=True)
# writes them side by side.
#
# Set to None for a fresh run.
# MUST be None while FIX_FRONTIER_OBSERVATION is on: it widens the observation from
# 238 to 244, so every artifact from PPO_7/PPO_8 is incompatible. The saved policy's
# input layer is 238 wide, and VecNormalize.load would restore an obs_rms of shape
# (238,) into a 244-dim env. Both fail at startup. This run starts from step 0.
RESUME_FROM = None
RESUME_VECNORMALIZE = None
# ------------------------------------------------------------------------------


if __name__ == "__main__":
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    if FIX_OBS_NORMALIZATION:
        # Monitor has to be applied by hand here. SB3 only adds it inside _wrap_env's
        # `if not isinstance(env, VecEnv)` branch, so handing PPO a VecEnv skips it and
        # ep_rew_mean / ep_len_mean vanish from the logs - the metrics every run is
        # judged on. Monitor sits INSIDE VecNormalize so it records raw rewards and
        # ep_rew_mean stays comparable with PPO_2/4/5/6.
        env = Monitor(DCSSGymEnv(radius=3))
        env = DummyVecEnv([lambda: env])
        # norm_obs is the point: game_time reached ~17,000 in PPO_4 while status bits
        # are 0/1, so two clock features dominated the first layer. norm_reward stays
        # False on purpose - every config A break-even (NEW_CELL_REWARD vs
        # STEP_PENALTY vs DEATH_PENALTY) is stated in absolute reward units and
        # normalising the reward would silently invalidate all of it.
        if RESUME_VECNORMALIZE:
            # Continue the running statistics rather than restarting them from zero,
            # which would re-scale observations against a fresh, tiny sample.
            env = VecNormalize.load(RESUME_VECNORMALIZE, env)
            env.training = True
            env.norm_reward = False
            print("Resumed VecNormalize statistics from {} (count={:.0f})".format(
                RESUME_VECNORMALIZE, float(env.obs_rms.count)))
        else:
            env = VecNormalize(env, norm_obs=True, norm_reward=False, clip_obs=10.0)
    else:
        env = DCSSGymEnv(radius=3)

    checkpoint_callback = CheckpointCallback(
        save_freq=CHECKPOINT_FREQ,
        save_path=CHECKPOINT_DIR,
        name_prefix="ppo_dcss",
        # Without this the running mean/var is lost and any later evaluation
        # normalises with the wrong statistics - silently, just performing worse.
        save_vecnormalize=FIX_OBS_NORMALIZATION,
    )

    if RESUME_FROM:
        model = PPO.load(RESUME_FROM, env=env, device="cuda",
                         tensorboard_log="./tb_logs/")
        already = model.num_timesteps
        remaining = max(0, TOTAL_TIMESTEPS - already)
        print("Resumed policy from {} at {:,} steps; {:,} remaining to reach {:,}".format(
            RESUME_FROM, already, remaining, TOTAL_TIMESTEPS))
        if remaining == 0:
            raise SystemExit("Nothing to do: checkpoint is already at TOTAL_TIMESTEPS")
    else:
        model = PPO(
            policy="MlpPolicy",
            env=env,
            device="cuda",
            n_steps=N_STEPS,
            # Retained from PPO_5 (not this run's variable). SB3's default 0.99 gives an
            # effective horizon of 1/(1-gamma) = ~100 steps; 0.999 widens it to ~1000, so
            # a new cell found several hundred steps from now still carries weight.
            gamma=0.999,
            verbose=1,
            tensorboard_log="./tb_logs/",
        )
        remaining = TOTAL_TIMESTEPS

    try:
        # reset_num_timesteps=False keeps the step counter (and so the checkpoint
        # filenames and TensorBoard x-axis) continuous across the resume.
        model.learn(total_timesteps=remaining, callback=checkpoint_callback,
                    reset_num_timesteps=not bool(RESUME_FROM))
    except Exception:
        print("=" * 80)
        print("TRAINING CRASHED - full traceback below")
        print("=" * 80)
        traceback.print_exc()
        raise
    finally:
        # In a finally block so a crash no longer discards the run. PPO_7 died at 88k
        # and these two saves sat after the re-raise, so ppo_dcss_final.zip was left as
        # a stale artifact from two runs earlier and vecnormalize.pkl was never written
        # at all. Only the per-checkpoint copies survived.
        #
        # Each save is guarded separately: a failure here must never mask the real
        # exception on its way up.
        try:
            model.save(FINAL_MODEL_PATH)
            print("Final model saved to {} at {:,} steps".format(
                FINAL_MODEL_PATH, model.num_timesteps))
        except Exception:
            print("WARNING - could not save final model")
            traceback.print_exc()
        if FIX_OBS_NORMALIZATION:
            # The running statistics are part of the trained artifact. Load the policy
            # without them and every observation is scaled wrongly - no error, just a
            # worse agent.
            try:
                vecnorm_path = os.path.join(MODELS_DIR, "vecnormalize.pkl")
                env.save(vecnorm_path)
                print("VecNormalize statistics saved to {}".format(vecnorm_path))
            except Exception:
                print("WARNING - could not save VecNormalize statistics")
                traceback.print_exc()

    print("Training complete.")
