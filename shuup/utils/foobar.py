def foobar(n):
    """
    A foobar function, just for testing code coverage.

    >>> foobar(0)
    12345

    >>> foobar(1)
    0
    1
    """

    j = 0
    k = 0

    for i in range(n):
        if i < 5:
            k += 1
            print(i)
        j += 1

    if j != k:
        print('larger than 5')


    if bytes == str:
        # This will be ran only on Python 2, testing that...
        assert 3 / 2 == 1
    else:
        assert 3 / 2 == 1.5

    if n > 0:
        return n ** 2
    elif n < 0:
        return (100 + n) ** 2
    elif n == 0:
        return 12345
