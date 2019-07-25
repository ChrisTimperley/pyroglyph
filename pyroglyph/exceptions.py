# -*- coding: utf-8 -*-
__all__ = ('__version__', 'PyroglyphException', 'AlreadyStarted',
           'AlreadyTerminated')


class PyroglyphException(Exception):
    """Base class used by all Pyroglyph exceptions."""


class AlreadyStarted(PyroglyphException):
    """The render loop has already been started."""


class AlreadyTerminated(PyroglyphException):
    """The render loop has already been terminated."""
