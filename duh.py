import sys
import wave
from wave_helpers import pretty_hex_string, bytes2int_list, ints2dots

wav_file = wave.open(sys.argv[1], 'r')  # fixme catch exception, "with"

baud = 50  # symbol / sec
frame_rate = wav_file.getframerate()
frames_per_symbol = frame_rate / baud
n_symbols = 2
symbols = wav_file.readframes(int(frames_per_symbol * n_symbols))

# Make 3 objects for printing
pretty_hex_list = list(pretty_hex_string(symbols.hex()))
int_list = list(bytes2int_list(symbols))
dot_list = list(ints2dots(int_list))

# Do the printing

n_bytes = 16
byte_per_sample = wav_file.getsampwidth()
n_frames = n_bytes / byte_per_sample
char_per_byte = 2  # A byte is two hex digits '01' or '0F' etc.

print("Params:\n", wav_file.getparams())
print()
print("Seconds =", wav_file.getnframes() / frame_rate)
print("Frames / FSK symbol =", frames_per_symbol)
print("Bytes in %i FSK symbols =" % n_symbols, len(symbols))
print()
print("First %i bytes (%i frames):" % (n_bytes, n_frames))
print(symbols[:n_bytes])
print(''.join(pretty_hex_list[:n_bytes * char_per_byte]))
print(int_list[:n_bytes // byte_per_sample])
print()
print('\n'.join(dot_list[:n_bytes // byte_per_sample]))
