import sys
import time
from platforms import *

class Timer(object):
    """定时器类"""
    end_time: float

    def __init__(self, interval: float):
        self.end_time = time.perf_counter() + interval

    def timeout(self) -> bool:
        return time.perf_counter() >= self.end_time

def throw(msg: str):
    raise Exception(msg)

def timetosecond(time_str: str) -> int:
    strs = time_str.split(':')
    second = int(strs[-1])
    minute = int(strs[-2]) if len(strs) > 1 else 0
    hour = int(strs[-3]) if len(strs) > 2 else 0
    return second + minute * 60 + hour * 3600

def secondtotime(second: int) -> str:
    minute = int(second / 60)
    second %= 60
    hour = int(minute / 60)
    minute %= 60
    return "%02d:%02d:%02d" % (hour, minute, second)

def ispacked() -> bool:
    return hasattr(sys, "frozen")
