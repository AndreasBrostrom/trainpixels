#!/usr/bin/env python3
from typing import TypedDict


class ConfigType(TypedDict):
    """Configuration settings for TrainPixels"""
    track_pixel_length: int
    util_pixel_length: int
    track_pin: str
    util_pin: str
    brightness: float
    track_speed_modifier: float
    random_util_trigger_chance: float
    color_table: dict


class TrackType(TypedDict):
    """Track structure for LED animations"""
    id:  str
    name: str
    track_path: list[int]
    speed: int


class UtilsType(TypedDict):
    """Utils structure for LED utility lights"""
    id:  str
    name: str
    is_random: bool
    enabled_on_init: bool
    utils: list[dict]
