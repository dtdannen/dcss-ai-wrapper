"""
Runs one episode of DCSSGymEnv with random actions, to confirm the env works
end-to-end (connects, resets, steps, computes rewards, detects episode end)
before any real training.
"""

from dcss.rl.dcss_gym_env import DCSSGymEnv


if __name__ == "__main__":
    env = DCSSGymEnv(radius=3)

    obs, info = env.reset()
    print("Reset OK. observation shape={}, info={}".format(obs.shape, info))

    total_reward = 0.0
    steps = 0
    terminated = False
    truncated = False

    while not terminated and not truncated:
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        steps += 1
        print("step={} action={} reward={:.3f} terminated={} info={}".format(
            steps, action, reward, terminated, info))

    print("Episode ended after {} steps. total_reward={:.3f}".format(steps, total_reward))
