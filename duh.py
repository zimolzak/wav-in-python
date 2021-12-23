import sys
import wave

wav_file = wave.open(sys.argv[1], 'r')  # fixme catch exception, "with"

baud = 50
frame_rate = wav_file.getframerate()
frames_per_symbol = frame_rate / baud

print("params", wav_file.getparams())
print()

five = wav_file.readframes(5)
five_more = wav_file.readframes(5)
print(five)
print(five.hex())
print(five_more.hex())
print()

print("seconds", wav_file.getnframes() / frame_rate)
print("frames / symbol =", frames_per_symbol)
wav_file.rewind()
two_symbols = wav_file.readframes(int(frames_per_symbol * 2))
print("bytes in 2 symbols", len(two_symbols))
print()

hex_string = two_symbols.hex()


def pretty_hex_string(hs):  # fixme params for 2 and 16 magic nums
    """Input a string and add spaces and newlines every so often."""
    bytes_space = 2  # fixme make a function arg
    bytes_newline = 16
    cs = bytes_space * 2  # chars per space
    cn = bytes_newline * 2  # chars per newline
    for n, c in enumerate(hs):
        # every 16 bytes add a newline
        # fixme insert code here
        if n % cn == cn - 1:
            yield c + "\n"
        elif n % cs == cs - 1:
            # Every 4 char (2 bytes), add a space.
            yield c + " "  # fixme should we yield 2 things?
        else:
            yield c


plist = list(pretty_hex_string(hex_string))


def bytes2int_list(byte_list):
    for n, b in enumerate(byte_list):
        if n % 2 == 0:
            continue
        else:
            yield 256 * byte_list[n - 1] + byte_list[n]
            # indexing or list() on a 'bytes' obj auto-converts to 'int'


int_list = list(bytes2int_list(two_symbols))


def ints2dots(ints):
    max_int = 256 * 255 + 255  # 65535
    max_spaces = 75
    for x in ints:
        n_spaces = int(x / max_int * max_spaces)
        yield '.' * n_spaces + 'X'


dot_list = list(ints2dots(int_list))


n_bytes = 16

print(''.join(plist[:n_bytes * 2]))
print(int_list[:n_bytes // 2])
print('\n'.join(dot_list[:n_bytes // 2]))
