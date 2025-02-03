from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList

import gymnasium as gym
import os

from environments import CastlevaniaPyBoyEnv

# from stable_baselines3.common.monitor import Monitor
# from callbacks import VideoRecorderCallback

if __name__ == "__main__":

    rom_file = "Castlevania - The Adventure (Europe).gb"

    ticks_per_step = 16
    n_envs = 8
    render_mode = "rgb_array"  # "human" or "rgb_array"

    model_name = "castlevania"
    train_steps = 2_000_000
    save_freq = 10_000
    # eval_freq = 1_000

    # load_model = "models/castlevania_2000000_steps"

    hyperparams = {
        "n_steps": 2048,
        "batch_size": 512,
        "gamma": 0.997,
        "ent_coef": 0.01,
        # "learning_rate": 3e-5,
        # "gae_lambda": 0.98,
    }

    tensorlog_dir = "tensorlogs/"
    os.makedirs(tensorlog_dir, exist_ok=True)

    # logs_dir = "logs/"
    # os.makedirs(logs_dir, exist_ok=True)

    save_path = "models/"
    os.makedirs(save_path, exist_ok=True)

    gym.register(
        id="CastlevaniaPyBoyEnv-v0",
        entry_point=CastlevaniaPyBoyEnv,
    )

    env = make_vec_env(
        "CastlevaniaPyBoyEnv-v0",
        n_envs=n_envs,
        env_kwargs=dict(ticks_per_step=ticks_per_step, rom_file=rom_file, render_mode=render_mode),
    )

    # eval_env = Monitor(
    #     gym.make("CastlevaniaPyBoyEnv-v0", ticks_per_step=ticks_per_step, rom_file=rom_file, render_mode=render_mode),
    #     logs_dir,
    # )
    # stop_train_callback = StopTrainingOnNoModelImprovement(max_no_improvement_evals=5, min_evals=10, verbose=1)
    # eval_callback = EvalCallback(
    #     eval_env,
    #     eval_freq=eval_freq,
    #     callback_after_eval=stop_train_callback,
    #     verbose=1,
    #     best_model_save_path=save_path,
    # )

    # render_env = gym.make("CastlevaniaPyBoyEnv-v0", ticks_per_step=ticks_per_step, rom_file=rom_file)
    # video_recorder = VideoRecorderCallback(
    #     render_env,
    #     render_freq=500,
    # )

    checkpoint_callback = CheckpointCallback(
        save_freq=save_freq,
        save_path=save_path,
        name_prefix=model_name,
        save_replay_buffer=True,
        save_vecnormalize=True,
    )

    callbacks = CallbackList([checkpoint_callback])

    model = PPO(
        "MultiInputPolicy", env, verbose=1, tensorboard_log=f"{tensorlog_dir}{model_name}_tensorlog", **hyperparams
    )
    # print(model.policy)

    # model = PPO.load(
    #     load_model,
    #     env,
    #     verbose=1,
    #     tensorboard_log=f"{tensorlog_dir}{model_name}_tensorlog",
    #     print_system_info=True,
    #     **hyperparams,
    # )
    # model.rollout_buffer.buffer_size = hyperparams["n_steps"]
    # model.rollout_buffer.n_envs = n_envs
    # model.rollout_buffer.reset()

    model.learn(total_timesteps=train_steps, progress_bar=True, callback=callbacks)
    model.save(f"{save_path}{model_name}_{train_steps}_steps")

    env.close()
