from typing import Any
from enum import Enum
from pyboy import PyBoy
from pyboy.api.constants import TILES_CGB
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from skimage.transform import downscale_local_mean
from collections import deque


class PyBoyEnv(gym.Env):

    metadata: dict[str, Any] = {"render_modes": ["human", "human_all_frames", "rgb_array"]}  # TODO: Render modes

    game_area_dimensions = (0, 0, 20, 16)
    follow_scrolling = True
    game_area_mapping = [x for x in range(TILES_CGB)]

    class Actions(Enum):
        A = 0
        B = 1
        LEFT = 2
        RIGHT = 3
        UP = 4
        DOWN = 5
        START = 6
        SELECT = 7
        IDLE = 8

    def __init__(
        self, rom_file="", emulation_speed=0, ticks_per_step=16, render_mode="rgb_array", window="SDL2", frame_stacks=3
    ):
        super().__init__()
        self.rom_file = rom_file
        self.ticks_per_step = ticks_per_step
        self.render_mode = render_mode
        self.window = "null" if self.render_mode in ["rgb_array"] else window

        self.frame_stacks = frame_stacks
        self.screens_shape = (72, 80, self.frame_stacks)

        self._init_pyboy()
        self.pyboy.set_emulation_speed(emulation_speed)

        self._init_action_space()
        self._init_observation_space()

        self._start_game()

    def _init_pyboy(self):
        self.pyboy = PyBoy(self.rom_file, window=self.window)
        self.pyboy.game_area_dimensions(*self.game_area_dimensions, self.follow_scrolling)
        self.pyboy.game_area_mapping(self.game_area_mapping)

    def _init_action_space(self):
        self.action_space = spaces.Discrete(len(self.Actions))

    def _init_observation_space(self):
        self.observation_space = spaces.Dict(
            {
                "screens": spaces.Box(low=0, high=255, shape=self.screens_shape, dtype=np.uint8),
                "actions": spaces.MultiDiscrete([len(self.Actions)] * self.frame_stacks, dtype=np.uint8),
            }
        )

    def _start_game(self):
        """
        Start the game for the first time when initializating the environment.
        Must call `pyboy.game_wrapper.start_game()` to allow the use of `pyboy.game_wrapper.reset_game()`
        """
        self.pyboy.game_wrapper.start_game()

    def _reset_game(self):
        """Reset the game"""
        self.pyboy.game_wrapper.reset_game()

    def reset(self, **kwargs):
        self._reset_game()

        self.recent_screens = np.zeros(self.screens_shape, dtype=np.uint8)
        self.recent_actions = np.zeros((self.frame_stacks,), dtype=np.uint8)

        self._previous_info = {}
        self._info = self._get_info()

        return self._get_observation(), self._info

    def step(self, action):
        self._apply_action(action)

        if self.render_mode == "human_all_frames":
            for _ in range(self.ticks_per_step):
                self.pyboy.tick()
        else:
            self.pyboy.tick(self.ticks_per_step, self.render_mode == "human")

        self._update_info()
        self._update_recent_screens()
        self._update_recent_actions(action)

        observation = self._get_observation()
        reward = self._calculate_reward()
        terminated = self._game_over()
        truncated = self._is_truncated()

        return observation, reward, terminated, truncated, self._info

    def _apply_action(self, action):
        """Apply the action"""
        if action == self.Actions.IDLE.value:
            pass
        elif action == self.Actions.A.value:
            self.pyboy.button("a", self.ticks_per_step)
        elif action == self.Actions.B.value:
            self.pyboy.button("b", self.ticks_per_step)
        elif action == self.Actions.LEFT.value:
            self.pyboy.button("left", self.ticks_per_step)
        elif action == self.Actions.RIGHT.value:
            self.pyboy.button("right", self.ticks_per_step)
        elif action == self.Actions.UP.value:
            self.pyboy.button("up", self.ticks_per_step)
        elif action == self.Actions.DOWN.value:
            self.pyboy.button("down", self.ticks_per_step)
        elif action == self.Actions.START.value:
            self.pyboy.button("start", self.ticks_per_step)
        elif action == self.Actions.SELECT.value:
            self.pyboy.button("select", self.ticks_per_step)

    def _update_info(self):
        self._previous_info = self._info
        self._info = self._get_info()

    def _update_recent_screens(self):
        self.recent_screens = np.roll(self.recent_screens, 1, axis=2)
        self.recent_screens[:, :, 0] = self.render(reduce_res=True, rgb=False)[:, :, 0]

    def _update_recent_actions(self, action):
        self.recent_actions = np.roll(self.recent_actions, 1)
        self.recent_actions[0] = action

    def _get_observation(self):
        """
        Returns the observation. Usually the "game area".

        If you overrides this method (for example to use data from RAM memory in your observation) be sure to set an appropiate "self.observation_space".
        """
        return {
            "screens": self.recent_screens,
            "actions": self.recent_actions,
        }

    def _get_info(self):
        """Returns additional information about the game state."""
        return {"normalized_game_area": self._get_normalized_game_area()}

    def _game_over(self):
        return self.pyboy.game_wrapper.game_over()

    def _is_truncated(self):
        return False

    def _calculate_reward(self):
        """Calculate the reward"""
        return NotImplementedError

    def _get_normalized_game_area(self):
        game_area = self.pyboy.game_area().astype("float64")
        game_area *= 255.0 / np.max(self.game_area_mapping)
        return game_area.astype("uint8")

    def render(self, reduce_res=False, rgb=True):
        game_pixels_render = self.pyboy.screen.ndarray[:, :, 0 : 3 if rgb else 1]  # (144, 160, 1) h, w, c
        if reduce_res:
            game_pixels_render = downscale_local_mean(game_pixels_render, (2, 2, 1)).astype(np.uint8)  # (72, 80, 1)
        return game_pixels_render

    def close(self):
        self.pyboy.stop()
