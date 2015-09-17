def batch(iterable, count):
    """
    Iterate batches of items from the given iterable.

    >>> [tuple(x) for x in batch([1, 2, 3, 4, 5, 6, 7], 3)]
    [(1, 2, 3), (4, 5, 6), (7,)]

    :param iterable: An iterable
    :type iterable: Iterable[Any]
    :param count: Number of items per batch, must be > 0
    :type count: int
    :return: Iterable of iterables
    :rtype: Iterable[Iterable[Any]]
    """
    return _Batcher(iterable, count)


class _Batcher(object):
    def __init__(self, iterable, batch_size):
        assert batch_size > 0
        self.batch_size = batch_size
        self.iterator = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        self.next_val = next(self.iterator)  # Exit on StopIteration
        return self._iterate_batch()

    def _iterate_batch(self):
        for dummy in range(self.batch_size - 1):
            yield self.next_val
            self.next_val = next(self.iterator)  # Exit on StopIteration
        yield self.next_val
