from dataclasses import dataclass
from enum import Enum


class Lane(Enum):
    """Lane positions: 0 = rightmost, 1 = middle, 2 = leftmost"""
    RIGHT = 0
    MIDDLE = 1
    LEFT = 2


@dataclass
class Car:
    """Represents a car on the highway"""
    position: float  # Position along the highway
    speed: float  # Current speed
    lane: Lane  # Current lane
    max_speed: float  # Maximum speed this car can achieve
    follows_bad_practice: bool  # Whether this car doesn't use rightmost lane

    def __init__(self, position: float, speed: float, lane: Lane,
                 max_speed: float, follows_bad_practice: bool = False):
        self.position = position
        self.speed = speed
        self.lane = lane
        self.max_speed = max_speed
        self.follows_bad_practice = follows_bad_practice