from enum import Enum


class WorkerState(Enum):
    INIT = 'INIT'
    RUNNING = 'RUNNING'
    STOP = 'STOP'
