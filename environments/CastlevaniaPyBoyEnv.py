from environments import PyBoyEnv
from enum import Enum
from gymnasium import spaces
import numpy as np

ADDR_HEALTH = 0xC519
ADDR_CURRENT_ROOM = 0xC412
ADDR_POS_X = 0xC42B
ADDR_POS_X_2 = 0xC42C
ADDR_POS_Y = 0xC300
ADDR_CHARACTER_STATE = 0xC502

MAX_HEALTH = 10
MAX_WHIPE_LEVEL = 2
MAX_LEVEL_SCORE = 99999


class CastlevaniaPyBoyEnv(PyBoyEnv):

    rom_file = "Castlevania - The Adventure (Europe).gb"
    game_area_dimensions = (0, 0, 20, 16)
    follow_scrolling = True
    game_area_mapping = [x for x in range(384)]

    class Actions(Enum):
        IDLE = 0
        JUMP = 1
        JUMP_RIGHT = 2
        JUMP_LEFT = 3
        MOVE_RIGHT = 4
        MOVE_LEFT = 5
        ATTACK = 6
        CROUCH_ATTACK = 7
        CROUCH = 8

    def _start_game(self):
        self.pyboy.game_wrapper.start_game()
        self.pyboy.tick(80, False)
        # self.pyboy.memory[ADDR_HEALTH] = 1

    def _reset_game(self):
        self.pyboy.game_wrapper.reset_game()
        self.pyboy.tick(80, False)
        # self.pyboy.memory[ADDR_HEALTH] = 1

    def _init_observation_space(self):
        self.observation_space = spaces.Dict(
            {
                "screens": spaces.Box(low=0, high=255, shape=self.screens_shape, dtype=np.uint8),
                "actions": spaces.MultiDiscrete([len(self.Actions)] * self.frame_stacks),
                "health": spaces.Discrete(MAX_HEALTH + 1),
                "whipe_level": spaces.Discrete(MAX_WHIPE_LEVEL + 1),
                "invincible_timer": spaces.Discrete(256),
                "current_room": spaces.Discrete(256),
                # "stage": spaces.Discrete(256),
            }
        )

    def _get_observation(self):
        return {
            "screens": self.recent_screens,
            "actions": self.recent_actions,
            "health": self.pyboy.game_wrapper.health,
            "whipe_level": self.pyboy.game_wrapper.whipe_level,
            "invincible_timer": self.pyboy.game_wrapper.invincible_timer,
            "current_room": self.pyboy.memory[ADDR_CURRENT_ROOM],
            # "stage": self.pyboy.memory[ADDR_STAGE],
        }

    def _get_info(self):
        return {
            "health": self.pyboy.game_wrapper.health,
            "score": self.pyboy.game_wrapper.level_score,
            "whipe_level": self.pyboy.game_wrapper.whipe_level,
            "invincible_timer": self.pyboy.game_wrapper.invincible_timer,
            "time_left": self.pyboy.game_wrapper.time_left,
            "current_room": self.pyboy.memory[ADDR_CURRENT_ROOM],
            "pos_x": self.pyboy.memory[ADDR_POS_X] + self.pyboy.memory[ADDR_POS_X_2] * 255,
            "pos_y": self.pyboy.memory[ADDR_POS_Y],
            "character_state": self.pyboy.memory[ADDR_CHARACTER_STATE],
            "normalized_game_area": self._get_normalized_game_area(),
            "screens": self.recent_screens,
            # "stage": self.pyboy.memory[ADDR_STAGE],
        }

    def _calculate_reward(self):
        if self._game_over():
            return 0

        reward = 0

        # Score
        reward += (self._info["score"] - self._previous_info["score"]) // 2

        # Time
        # reward += self._previous_info["time_left"] - self._info["time_left"]

        # Room forward
        if self._info["current_room"] > self._previous_info["current_room"]:
            reward += self._info["current_room"] * 50

        # Room backward
        if self._info["current_room"] < self._previous_info["current_room"]:
            reward -= (self._previous_info["current_room"]) * 50

        # First room, reward when walking to the right.
        if self._info["current_room"] == 0:
            if self._info["pos_x"] > self._previous_info["pos_x"]:
                reward += 1
            if self._info["pos_x"] < self._previous_info["pos_x"]:
                reward -= 1

        # Second room, reward when walking to the left.
        if self._info["current_room"] == 1:
            if self._info["pos_x"] > self._previous_info["pos_x"]:
                reward -= 1
            if self._info["pos_x"] < self._previous_info["pos_x"]:
                reward += 1

        # Whipe level
        if self._info["whipe_level"] > self._previous_info["whipe_level"]:
            reward += (10 * self._info["whipe_level"]) * 2

        # Invincible
        if self._info["invincible_timer"] > self._previous_info["invincible_timer"]:
            reward += 20

        # Health
        reward += (self._info["health"] - self._previous_info["health"]) * 20

        return reward

    def _apply_action(self, action):
        if action == self.Actions.IDLE.value:
            pass
        elif action == self.Actions.JUMP.value:
            self.pyboy.button("a", max(self.ticks_per_step - 1, 1))
        elif action == self.Actions.JUMP_RIGHT.value:
            self.pyboy.button("a", max(self.ticks_per_step - 1, 1))
            self.pyboy.button("right", self.ticks_per_step)
        elif action == self.Actions.JUMP_LEFT.value:
            self.pyboy.button("a", max(self.ticks_per_step - 1, 1))
            self.pyboy.button("left", self.ticks_per_step)
        elif action == self.Actions.MOVE_RIGHT.value:
            self.pyboy.button("right", self.ticks_per_step)
        elif action == self.Actions.MOVE_LEFT.value:
            self.pyboy.button("left", self.ticks_per_step)
        elif action == self.Actions.ATTACK.value:
            self.pyboy.button("b", max(self.ticks_per_step - 1, 1))
        elif action == self.Actions.CROUCH_ATTACK.value:
            self.pyboy.button("b", max(self.ticks_per_step - 1, 1))
            self.pyboy.button("down", self.ticks_per_step)
        elif action == self.Actions.CROUCH.value:
            self.pyboy.button("b", max(self.ticks_per_step - 1, 1))
            self.pyboy.button("down", self.ticks_per_step)
