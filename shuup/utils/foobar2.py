def foobar(n):
    """
    A foobar function, just for testing code coverage.
    """

    j = 0
    k = 0

    for i in range(n):
        if i < 5:
            k += 1
            print(i)
        j += 1

    if j == k:
        print('hello')

    if n > 0:
        return n ** 2
    elif n < 0:
        return (100 + n) ** 2
    elif n == 0:
        return 12345
