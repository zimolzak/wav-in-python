from typing import Generator


def pretty_hex_string(hs: str) -> Generator[str, None, None]:
    """Prepare hexadecimal text for easier reading.
    "abcdefgh" -> ['a', 'b', 'c', 'd ', 'e', 'f', 'g', 'h ']
    Note the spaces. Often you do ''.join(list()) to get this:
    'abcd efgh '

    :param hs: Any string. Usually hexadecimal letters/numbers.
    :return: Yield a stream of chars with spaces and newlines added every so often.
    """
    bytes_space = 2  # fixme make these into function args
    bytes_newline = 16
    cs = bytes_space * 2  # chars per space (4)
    cn = bytes_newline * 2  # chars per newline (32)
    for n, c in enumerate(hs):
        # every 16 bytes add a newline
        if n % cn == cn - 1:
            yield c + "\n"
        elif n % cs == cs - 1:
            # Every 4 char (2 bytes), add a space.
            yield c + " "  # fixme should we yield 2 things?
        else:
            yield c


def ints2dots(ints: list, max_int: int = 65535, max_spaces: int = 75) -> Generator[str, None, None]:
    """Prepare a text bar graph of numeric data. Usually a few values of WAV file samples. If they look a bit like a
    sine wave, we probably decoded them properly.

    list(ints2dots([1000,2000,4000]))  ->
    ['.X', '..X', '....X']

    :param max_spaces:
    :param max_int:
    :param ints: List of numbers. Negative means no
    """
    for x in ints:
        n_spaces = int(x / max_int * max_spaces)
        yield '.' * n_spaces + 'X'
