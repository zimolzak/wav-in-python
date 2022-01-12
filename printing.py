from typing import Generator


def pretty_hex_string(hs: str, bytes_space: int = 2, bytes_newline: int = 16) -> Generator[str, None, None]:
    """Prepare hexadecimal text for easier reading.
    "abcdefgh" -> ['a', 'b', 'c', 'd ', 'e', 'f', 'g', 'h ']
    Note the spaces. Often you do ''.join(list()) to get this:
    'abcd efgh '

    :param hs: Any string. Usually hexadecimal letters/numbers.
    :param bytes_newline: How many bytes until insert newline
    :param bytes_space: How many bytes until insert space
    :return: Yield a stream of chars with spaces and newlines added every so often.
    """
    characters_per_space = bytes_space * 2  # chars per space (4)
    characters_per_newline = bytes_newline * 2  # chars per newline (32)
    for n, c in enumerate(hs):
        # every 16 bytes add a newline
        if n % characters_per_newline == characters_per_newline - 1:
            yield c + "\n"
        elif n % characters_per_space == characters_per_space - 1:
            # Every 4 char (2 bytes), add a space.
            yield c + " "
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
