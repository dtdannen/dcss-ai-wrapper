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

from dcss.rl.dcss_gym_env import DCSSGymEnv


# --- Training config ---
# Long learning run. The 20k-step run validated the pipeline end-to-end (deepcopy
# fix held, ep_rew_mean appeared, clean start-to-finish) but only produced 4
# completed episodes - not enough to tell whether the policy is actually learning.
# This run is 5x longer specifically to accumulate enough completed episodes
# (~30-50 expected) for ep_rew_mean to be a trustworthy trend. Expected runtime
# ~1.5-2 hours, based on the 20k run's ~22min.
TOTAL_TIMESTEPS = 100000  # long learning run
N_STEPS = 2048  # PPO's standard rollout length per update
CHECKPOINT_FREQ = 2000  # save a checkpoint every ~2000 steps, frequent given the longer run

MODELS_DIR = os.path.join("models", "ppo_dcss")
CHECKPOINT_DIR = os.path.join(MODELS_DIR, "checkpoints")
FINAL_MODEL_PATH = os.path.join(MODELS_DIR, "ppo_dcss_final")


if __name__ == "__main__":
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    env = DCSSGymEnv(radius=3)

    checkpoint_callback = CheckpointCallback(
        save_freq=CHECKPOINT_FREQ,
        save_path=CHECKPOINT_DIR,
        name_prefix="ppo_dcss",
    )

    model = PPO(
        policy="MlpPolicy",
        env=env,
        device="cuda",
        n_steps=N_STEPS,
        verbose=1,
        tensorboard_log="./tb_logs/",
    )

    try:
        model.learn(total_timesteps=TOTAL_TIMESTEPS, callback=checkpoint_callback)
    except Exception:
        print("=" * 80)
        print("TRAINING CRASHED - full traceback below")
        print("=" * 80)
        traceback.print_exc()
        raise

    model.save(FINAL_MODEL_PATH)
    print("Training complete. Final model saved to {}".format(FINAL_MODEL_PATH))
