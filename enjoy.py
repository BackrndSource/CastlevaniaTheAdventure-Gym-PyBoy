from stable_baselines3 import PPO
import gymnasium as gym
import imageio
import sys
import os

from environments import CastlevaniaPyBoyEnv
from subprocess import call


def print_info(info, reward, total_reward):
    sys.stdout.write("\r")
    sys.stdout.write(f"x: {info['pos_x']} ")
    sys.stdout.write(f"y: {info['pos_y']}\033[K\n")
    sys.stdout.write(f"\rroom: {info['current_room']}\033[K\n")
    sys.stdout.write(f"\rcharacter_state: {info['character_state']}\033[K\n")
    sys.stdout.write(f"\rLast reward: {reward}\033[K\n")
    sys.stdout.write(f"\rTotal reward: {total_reward}\033[K")
    sys.stdout.write("\033[F" * 4)
    sys.stdout.flush()


if __name__ == "__main__":

    model_path = "models/castlevania_2000000_steps"
    ticks_per_step = 16
    rom_file = "Castlevania - The Adventure (Europe).gb"

    games = 16

    gym.register(
        id="CastlevaniaPyBoyEnv-v0",
        entry_point=CastlevaniaPyBoyEnv,
    )

    env = gym.make(
        "CastlevaniaPyBoyEnv-v0",
        ticks_per_step=ticks_per_step,
        rom_file=rom_file,
        emulation_speed=0,
        render_mode="human",  # or "human_all_frames"
    )

    model = PPO.load(model_path, env, verbose=1)

    # logs_dir = "logs/"
    # os.makedirs(logs_dir, exist_ok=True)

    game = 0

    os.system("cls")

    while game < games:
        observation, info = env.reset()

        images = []
        images_game_area = []

        step = 0
        episode_over = False
        total_reward = 0

        while not episode_over:
            action, _ = model.predict(observation)
            observation, reward, terminated, truncated, info = env.step(action)
            episode_over = terminated or truncated

            # images.append(env.render())
            # screens.append(info["screens"])
            # images_game_area.append(info["normalized_game_area"])

            step += step
            total_reward += float(reward)

            print_info(info, reward, total_reward)

        print(f"\r[FINISH] Total reward: {total_reward}")
        # imageio.mimsave(f"{logs_dir}render_{game}.gif", images, fps=8)
        # imageio.mimsave(f"{logs_dir}render_{game}.gif", images_game_area, fps=8)
        # imageio.mimsave(f"{logs_dir}render_{game}.gif", screens, fps=8)
        game += 1

    env.close()
