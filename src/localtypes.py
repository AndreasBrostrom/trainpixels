#!/usr/bin/env python3
from typing import TypedDict

class ConfigType(TypedDict):
    """Configuration settings for TrainPixels"""
    track_speed_modifier: float
    num_pixels: int
    led_pin_name: str
    brightness: float
    random_event_chance: float
    next_track_wait: int
    color_table: dict
    
    
class TrackType(TypedDict):
    """Track structure for LED animations"""
    id:  str
    name: str
    track_path: list[int]
    speed: int
    
class EventType(TypedDict):
    """Event structure for LED events"""
    id:  str
    name: str
    is_random: bool
    enabled_on_init: bool
    events: list[dict]