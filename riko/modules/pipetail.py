# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
"""
riko.modules.pipetail
~~~~~~~~~~~~~~~~~~
Provides functions for truncating a stream to the last N items.

Contrast this with the Truncate module, which limits the output to the first N
items.

Examples:
    basic usage::

        >>> from riko.modules.pipetail import pipe
        >>> items = ({'x': x} for x in range(5))
        >>> next(pipe(items, conf={'count': 2}))
        {u'x': 3}

Attributes:
    OPTS (dict): The default pipe options
    DEFAULTS (dict): The default parser options
"""
from __future__ import (
    absolute_import, division, print_function, unicode_literals)

from collections import deque

from builtins import *

from . import operator
from riko.lib.log import Logger

OPTS = {}
logger = Logger(__name__).logger


def parser(stream, objconf, tuples, **kwargs):
    """ Parses the pipe content

    Args:
        stream (Iter[dict]): The source. Note: this shares the `tuples`
            iterator, so consuming it will consume `tuples` as well.

        objconf (obj): the item independent configuration (an Objectify
            instance).

        tuples (Iter[(dict, obj)]): Iterable of tuples of (item, objconf)
            `item` is an element in the source stream and `objconf` is the item
            configuration (an Objectify instance). Note: this shares the
            `stream` iterator, so consuming it will consume `stream` as well.

        kwargs (dict): Keyword arguments.

    Returns:
        List(dict): The output stream

    Examples:
        >>> from riko.lib.utils import Objectify
        >>> from itertools import repeat
        >>>
        >>> kwargs = {'count': 2}
        >>> objconf = Objectify(kwargs)
        >>> stream = ({'x': x} for x in range(5))
        >>> tuples = zip(stream, repeat(objconf))
        >>> parser(stream, objconf, tuples, **kwargs)[0]
        {u'x': 3}
    """
    return deque(stream, int(objconf.count))


@operator(async=True, **OPTS)
def asyncPipe(*args, **kwargs):
    """An aggregator that asynchronously truncates a stream to the last N items.

    Args:
        items (Iter[dict]): The source.
        kwargs (dict): The keyword arguments passed to the wrapper

    Kwargs:
        conf (dict): The pipe configuration. Must contain the key 'count'.

            count (int): desired stream length

    Returns:
        Deferred: twisted.internet.defer.Deferred truncated stream

    Examples:
        >>> from twisted.internet.task import react
        >>> from riko.twisted import utils as tu
        >>>
        >>> def run(reactor):
        ...     callback = lambda x: print(next(x))
        ...     items = ({'x': x} for x in range(5))
        ...     d = asyncPipe(items, conf={'count': 2})
        ...     return d.addCallbacks(callback, logger.error)
        >>>
        >>> try:
        ...     react(run, _reactor=tu.FakeReactor())
        ... except SystemExit:
        ...     pass
        ...
        {u'x': 3}
    """
    return parser(*args, **kwargs)


@operator(**OPTS)
def pipe(*args, **kwargs):
    """An operator that truncates a stream to the last N items.

    Args:
        items (Iter[dict]): The source.
        kwargs (dict): The keyword arguments passed to the wrapper

    Kwargs:
        conf (dict): The pipe configuration. Must contain the key 'count'.

            count (int): desired streamstream length

    Yields:
        dict: an item

    Examples:
        >>> items = [{'x': x} for x in range(5)]
        >>> next(pipe(items, conf={'count': 2}))
        {u'x': 3}
    """
    return parser(*args, **kwargs)