from singleton import Singleton
from typing import Optional
from pathlib import Path

class State(Singleton):
    def __init__(self):
        self.begin()
        self.temp_dir:Optional[Path] = None

    def begin(self):
        self.interrupted = False
        self.need_restart = False

    def restart(self):
        self.need_restart = True

    def interrupt(self):
        self.interrupted = True

state = State.get_instance()