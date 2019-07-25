# -*- coding: utf-8 -*-
__all__ = ('__version__', 'PyroglyphError', 'AlreadyStartedError',
           'AlreadyTerminatedError', 'NotStartedError')


class PyroglyphError(Exception):
    """Base class used by all Pyroglyph errors."""


class NotStartedError(PyroglyphError):
    """The render loop has not yet been started."""


class AlreadyStartedError(PyroglyphError):
    """The render loop has already been started."""


class AlreadyTerminatedError(PyroglyphError):
    """The render loop has already been terminated."""
