#!/usr/bin/env python

r"""
Implementation of a tiled variant of Conway's Game of Life.

Copyright © April 2009 Paul Butler

Licensed under the zlib/libpng license.

This software is provided 'as-is', without any express or implied
warranty. In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

    1. The origin of this software must not be misrepresented; you must not
    claim that you wrote the original software. If you use this software
    in a product, an acknowledgment in the product documentation would be
    appreciated but is not required.

    2. Altered source versions must be plainly marked as such, and must not be
    misrepresented as being the original software.

    3. This notice may not be removed or altered from any source
    distribution.

See README for more information.
"""

MAX_ITERATIONS = 3000

from array import array

def flatten(gen):
    r"""
    Flatten an iterator of iterators. This function is lazy
    and evaluates the given iterators only as values are
    needed.

    >>> list(flatten([[2,3,4],[5,6,7]]))
    [2, 3, 4, 5, 6, 7]
    """
    for g in gen:
        for v in g:
            yield v

class TiledMatrix:
    def _xy_to_index(self, x, y):
        r"""
        Map an (x, y) pair to an index in
        our internal 1-dimensional array.

        Examples:
        >>> tm = TiledMatrix(4, 5)
        >>> tm._xy_to_index(3, 3)
        15
        """
        x = x % self._width
        y = y % self._height
        return (y * self._width) + x

    def __init__(self, width, height, init_array=None):
        r"""
        Construct a TiledMatrix, given width and height.

        Values are initially set to 0
        """
        self._height = height
        self._width = width
        if init_array:
            self._array = array('B', init_array)
        else:
            self._array = array('B', [0] * height * width)

    def copy(self):
        r"""
        Create and return a clone of this TiledMatrix.
        
        Examples:
        >>> tm = TiledMatrix(2, 2)
        >>> tm[1,0] = tm[0,1] = 1
        >>> om = tm.copy()
        >>> om[0,0] = 1
        >>> print om
        XX
        X.
        >>> print tm
        .X
        X.
        """
        tm = TiledMatrix(self._width, self._height, self._array)
        return tm

    def __iter__(self):
        r"""
        Iterator for values in the TiledMatrix. Goes left-to-right,
        then top-to-bottom.

        Examples:
        >>> tm = TiledMatrix(4, 4)
        >>> tm[0, 3] = 1
        >>> tm[2, 2] = 1
        >>> tm[1, 3] = 1
        >>> tm[3, 2] = 1
        >>> tm[1, 0] = 1
        >>> tm[2, 1] = 1
        >>> print tm
        .X..
        ..X.
        ..XX
        XX..
        >>> list(tm)
        [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0]
        >>> sum(tm[(1,1):(3,3)])
        2
        """
        for y in xrange(0, self._height):
            for x in xrange(0, self._width):
                yield self[x,y]

    def __getitem__(self, pair):
        r"""
        Get a value from the TiledMatrix given an (x, y) pair.

        Examples:
        >>> tm = TiledMatrix(4, 5)
        >>> tm[2, 2] = 0
        >>> tm[2, 2]
        0
        >>> tm = TiledMatrix(8, 8)
        >>> for x in xrange(3, 7):
        ...     tm[x,1] = tm[x,4] = 1
        >>> for y in xrange(2, 4):
        ...     tm[3,y] = tm[6,y] = 1
        >>> tm[4,2] = 1
        >>> print tm
        ........
        ...XXXX.
        ...XX.X.
        ...X..X.
        ...XXXX.
        ........
        ........
        ........
        >>> print tm[(3, 1) : (7, 5)]
        XXXX
        XX.X
        X..X
        XXXX
        """
        if isinstance(pair, slice):
            (startX, startY) = pair.start
            (stopX, stopY) = pair.stop
            width = stopX - startX
            height = stopY - startY
            tm = TiledMatrix(width, height, flatten(
                (self[x,y] for x in xrange(startX, stopX))
                for y in xrange(startY, stopY)
            ))
            return tm
        x, y = pair
        index = self._xy_to_index(x, y)
        return self._array[index]

    def __setitem__(self, (x, y), value):
        r"""
        Set a value in the TiledMatrix given an (x, y) pair.

        Examples:
        >>> tm = TiledMatrix(2, 2)
        >>> tm[4, 5] = 1
        >>> tm[6, 7]
        1
        """
        index = self._xy_to_index(x, y)
        self._array[index] = value

    def __repr__(self):
        r"""
        Return a string representation of the TiledMatrix.

        Examples:
        >>> tm = TiledMatrix(5, 5)
        >>> for x in xrange(0, 5):
        ...     tm[x, x] = 1
        ...     tm[x, 4-x] = 1
        >>> print tm
        X...X
        .X.X.
        ..X..
        .X.X.
        X...X
        """
        ostr = '\n'.join(
            ''.join('.' if not v else 'X'
                    for v in self._array[self._width * y :
                        self._width * (y + 1)]
            ) for y in xrange(0, self._height))
        return ostr

def lifeiter(tm):
    r"""
    Perform an iteration of Conway's Game of Life on the given
    TiledMatrix, and return the resulting TiledMatrix.

    Examples:
    >>> tm = TiledMatrix(4, 4)
    >>> tm[0, 3] = 1
    >>> tm[2, 2] = 1
    >>> tm[1, 3] = 1
    >>> tm[3, 2] = 1
    >>> tm[1, 0] = 1
    >>> tm[2, 1] = 1
    >>> print tm
    .X..
    ..X.
    ..XX
    XX..
    >>> print lifeiter(tm)
    XXX.
    .XXX
    X.XX
    XX.X
    """
    DEAD = 0
    LIVE = 1
    rules = [
        [DEAD, DEAD, DEAD, LIVE, DEAD, DEAD, DEAD, DEAD, DEAD], # DEAD
        [DEAD, DEAD, DEAD, LIVE, LIVE, DEAD, DEAD, DEAD, DEAD, DEAD]  # LIVE
    ]

    newarray = flatten(
        (rules[tm[x,y]][sum(tm[(x-1, y-1) : (x + 2, y + 2)])]
        for x in xrange(0, tm._width)) for y in xrange(0, tm._height))

    ntm = TiledMatrix(tm._width, tm._height, newarray)
    return ntm

def main():
    import sys

    if len(sys.argv) > 1:
        infile = file(sys.argv[1], 'r')
    else:
        infile = sys.stdin

    world = []
    for line in infile:
        world.append([0 if c == '.' else 1 for c in line.strip()])
    width = len(world[0])
    height = len(world)
    tm = TiledMatrix(width, height, flatten(world))
    print
    print tm
    states = {}
    for j in xrange(0, MAX_ITERATIONS):
        if sum(tm) == 0:
            print "extinct"
            return
        print
        states[str(tm._array)] = j
        tm = lifeiter(tm)
        if str(tm._array) in states:
            print "stable after %s iterations with period %s" % (states[str(tm._array)], 1 + j - states[str(tm._array)])
            return
        print tm
    print "still active after %s iterations, stopping early." % j

if __name__ == '__main__':
    main()

