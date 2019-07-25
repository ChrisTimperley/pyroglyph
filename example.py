# -*- coding: utf-8 -*-
from typing import List, Union, Tuple
from timeit import default_timer as timer
import datetime
import time

import pyroglyph

TIME_START = timer()


def duration_tuple(secs: Union[int, float]) -> Tuple[int, int, int, int]:
    secs = int(secs)
    days, secs = divmod(secs, 86400)
    hours, secs = divmod(secs, 3600)
    mins, secs = divmod(secs, 60)
    return (secs, mins, hours, days)


def duration_str(secs: Union[int, float]) -> str:
    secs, mins, hours, days = duration_tuple(secs)
    return f'{days:2d} d {hours:2d} h {mins:2d} m {secs:2d} s'


def contents() -> List[str]:
    time_now = timer()
    time_running = time_now - TIME_START
    line_time = f'Running Time: {duration_str(time_running)}'
    line_candidates = 'Num. Candidates: ???'
    line_executions = 'Num. Executions: ???'
    return [line_time, line_candidates, line_executions]


title = lambda: f'Cool [{datetime.datetime.now()}]'
block_resources = pyroglyph.BasicBlock(title, contents)

with pyroglyph.Window('Darjeeling', [block_resources], []):
    time.sleep(10)
