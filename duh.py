import sys
import wave

filestr = sys.argv[1]  # fixme catch exception, "with"
wavfile = wave.open(filestr, 'r')

baud = 50
frate = wavfile.getframerate()
frames_per_symbol = frate / baud

print("params", wavfile.getparams())
print()

five = wavfile.readframes(5)
fivemore = wavfile.readframes(5)
print(five)
print(five.hex())
print(fivemore.hex())
print()

print("seconds", wavfile.getnframes() / frate)
print("frames / symb =", frames_per_symbol)
wavfile.rewind()
two_symbols = wavfile.readframes(int(frames_per_symbol * 2))
print("bytes in 2 symb", len(two_symbols))
print()

hstring = two_symbols.hex()


def pretty_hstring(hs):  # fixme params for 2 and 16 magic nums
    """Input a string and add spaces and newlines every so often."""
    bytes_space = 2  # fixme make a function arg
    bytes_newline = 16
    cs = bytes_space * 2  # chars per space
    cn = bytes_newline * 2  # chars per newline
    for n, c in enumerate(hs):
        # every 16 bytes add a newline
        # fixme insert code here
        if n % cn == cn - 1:
            yield (c + "\n")
        elif n % cs == cs - 1:
            # Every 4 char (2 bytes), add a space.
            yield (c + " ")  # fixme should we yield 2 things?
        else:
            yield c


plist = list(pretty_hstring(hstring))


# print(''.join(plist))

# >>> list(b'ABC')
# [65, 66, 67]

def bytes2intlist(blist):
    for n, b in enumerate(blist):
        if n % 2 == 0:
            continue
        else:
            yield (256 * blist[n - 1] + blist[n])


intlist = list(bytes2intlist(two_symbols))


# print(intlist)

def ints2dots(L):
    max_int = 256 * 255 + 255  # 65535
    max_spaces = 75
    for x in L:
        n_spaces = int(x / max_int * max_spaces)
        yield ('.' * n_spaces + 'X')


dotlist = list(ints2dots(intlist))
print('\n'.join(dotlist))
