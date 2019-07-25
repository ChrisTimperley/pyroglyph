# -*- coding: utf-8 -*-
__all__ = ('__version__', 'Block', 'Window')

from typing import Optional, Sequence, List, Union, Callable, Tuple
from timeit import default_timer as timer
import abc
import time
import threading

import attr
import blessed

from . import exceptions

Title = Union[str, Callable[[], str]]
Contents = Union[Sequence[str], Callable[[], Sequence[str]]]


class Block(abc.ABC):
    @property
    @abc.abstractmethod
    def title(self) -> str:
        """The current title of the block."""
        ...

    @property
    @abc.abstractmethod
    def contents(self) -> Sequence[str]:
        """The current contents of the block as a sequence of lines."""
        ...

    def render(self,
               t: blessed.Terminal,
               *,
               width: int = 80,
               border_top: bool = True,
               border_bottom: bool = True,
               border_left: bool = True,
               border_right: bool = True
               ) -> List[str]:
        """Renders the contents of the block to a list of lines."""
        lines: List[str] = []

        rule = width * '.'
        left = ': ' if border_left else ' '
        right = ' :' if border_right else ' '
        iw = width - len(left) - len(right)

        if border_top:
            lines.append(rule)

        if self.title:
            header = t.bold(self.title.ljust(iw))
            header = f"{left}{header}{right}"
            lines.append(header)

        lines += [f'{left}{l: <{iw}}{right}' for l in self.contents]
        if border_bottom:
            lines.append(rule)

        return lines


class BasicBlock(Block):
    """Uses a provided title and contents to form a block."""
    def __init__(self, title: Title, contents: Contents) -> None:
        self.__title: Title = title
        self.__contents: Contents = contents

    @property
    def title(self) -> str:
        if callable(self.__title):
            return self.__title()
        return self.__title

    @property
    def contents(self) -> Sequence[str]:
        if callable(self.__contents):
            return self.__contents()
        return self.__contents

@attr.s
class Window:
    """Provides an interactive terminal-based user interface."""
    title: str = attr.ib()
    blocks_left: Sequence[Block] = attr.ib()
    blocks_right: Sequence[Block] = attr.ib()
    terminal: blessed.Terminal = attr.ib(factory=blessed.Terminal)
    refresh_rate: int = attr.ib(default=60)
    width: int = attr.ib(default=120)

    def __attrs_post_init__(self) -> None:
        self.__has_started = False
        self.__terminated = threading.Event()
        self.__thread_loop = threading.Thread(target=self._spin, daemon=True)

    @property
    def has_started(self) -> bool:
        """Checks whether the render loop has been started."""
        return self.__has_started

    @property
    def has_terminated(self) -> bool:
        """Checks whether the render loop has been terminated."""
        return self.__terminated.is_set()

    @property
    def is_running(self) -> bool:
        """Checks whether the render loop is active."""
        return self.__thread_loop.is_alive()

    def open(self) -> None:
        """Starts the render loop for this window.

        Raises
        ------
        AlreadyStartedError
            if the render loop for this window has already been started.
        """
        if self.__has_started:
            raise exceptions.AlreadyStartedError

        self.__has_started = True
        self.__thread_loop.start()

    def close(self) -> None:
        """Terminates the render loop for this window.

        Raises
        ------
        NotStartedError
            if the render loop for this window has not been started.
        AlreadyTerminatedError
            if the render loop for this window has already been terminated.
        """
        if not self.has_started:
            raise exceptions.NotStartedError
        if self.__terminated.is_set():
            raise exceptions.AlreadyTerminatedError

        self.__terminated.set()
        self.__thread_loop.join()

    def __enter__(self) -> 'Window':
        self.open()
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        self.close()

    def _render_header(self) -> List[str]:
        t = self.terminal
        header = t.bold(t.center(self.title, width=self.width, fillchar='='))
        return [header]

    def _render(self) -> List[str]:
        t = self.terminal
        lines = self._render_header()

        # determine block width
        width_left = self.width // 2
        width_right = width_left

        # draw left blocks
        lines_left: List[str] = []
        for b in self.blocks_left[:1]:
            lines_left += b.render(t, width=width_left)
        for b in self.blocks_left[1:]:
            lines_left += b.render(t, width=width_left, border_top=False)

        # draw right blocks
        lines_right: List[str] = []
        for b in self.blocks_right[:1]:
            lines_right += b.render(t, width=width_right, border_left=False)
        for b in self.blocks_right[1:]:
            lines_right += b.render(t, width=width_right, border_top=False, border_left=False)  # noqa

        # ensure each column has the same number of lines by padding
        height_left = len(lines_left)
        height_right = len(lines_right)
        height = max(height_left, height_right)
        height_diff = abs(height_left - height_right)
        if height_left > height_right:
            padding = ' ' * width_right
            lines_right += [padding for i in range(height_diff)]
        elif height_right > height_left:
            padding = ' ' * (width_left - 1) + ':'
            lines_left += [padding for i in range(height_diff)]

        # compose the two columns into a single list of lines
        lines += [lines_left[i] + lines_right[i] for i in range(height)]

        return lines

    def _spin(self) -> None:
        """Continually redraws the window and blocks until terminated."""
        refresh_interval: float = 1 / self.refresh_rate
        t = self.terminal
        with t.fullscreen(), t.hidden_cursor():
            while not self.__terminated.is_set():
                frame_start: float = timer()

                # fill and swap the buffers
                updated = '\n'.join(self._render())
                print(self.terminal.clear(), end='')
                print(updated, end='')

                frame_end: float = timer()
                frame_duration: float = frame_end - frame_start
                wait = max(0.0, refresh_interval - frame_duration)
                time.sleep(wait)
