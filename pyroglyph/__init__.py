# -*- coding: utf-8 -*-
__all__ = ('__version__', 'Block')

from typing import Optional, Sequence, List

import attr
import blessed


@attr.s
class Block:
    title: Optional[str] = attr.ib()
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
            header = t.bold(self.title.ljust(iw))
            header = f"{left}{header}{right}"
            lines.append(header)

        lines += [f'{left}{l: <{iw}}{right}' for l in self.contents]
        if border_bottom:
            lines.append(rule)

        return lines
