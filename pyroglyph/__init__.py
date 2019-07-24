# -*- coding: utf-8 -*-
__all__ = ('__version__', 'Block', 'Window')

from typing import Optional, Sequence, List, Union, Callable
from timeit import default_timer as timer
import abc
import time

import attr
import blessed

from . import exceptions

ConcreteTitle = str
DynamicTitle = Callable[[], ConcreteTitle]
Title = Union[ConcreteTitle, DynamicTitle]


def title(t: Title) -> DynamicTitle:
    """Ensures that a given title is implemented as a dynamic title."""
    if isinstance(t, str):
        return lambda: t
    elif callable(t) and isinstance(t(), str):
        return t
    else:
        raise ValueError("expected str or callable.")


@attr.s
class Block:
    title: Title = attr.ib(converter=title)
    contents: Sequence[str] = attr.ib()

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
            title = self.title()
            header = t.bold(title.ljust(iw))
            header = f"{left}{header}{right}"
            lines.append(header)

        lines += [f'{left}{l: <{iw}}{right}' for l in self.contents]
        if border_bottom:
            lines.append(rule)

        return lines


@attr.s
class Window:
    """Provides an interactive terminal-based user interface."""
    title: str = attr.ib()
    blocks_left: Sequence[Block] = attr.ib()
    blocks_right: Sequence[Block] = attr.ib()
    terminal: blessed.Terminal = attr.ib(factory=blessed.Terminal)
    refresh_rate: int = attr.ib(default=60)
    width: int = attr.ib(default=120)

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

    def run(self) -> None:
        refresh_interval: float = 1 / self.refresh_rate
        t = self.terminal
        with t.fullscreen(), t.hidden_cursor():
            while True:
                frame_start: float = timer()

                # fill and swap the buffers
                updated = '\n'.join(self._render())
                print(self.terminal.clear(), end='')
                print(updated, end='')

                frame_end: float = timer()
                wait = max(0.0, refresh_interval - frame_end - frame_start)
                time.sleep(wait)
