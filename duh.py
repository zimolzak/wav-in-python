import sys
import wave
from wave_helpers import pretty_hex_string, bytes2int_list, ints2dots

wav_file = wave.open(sys.argv[1], 'r')  # fixme catch exception, "with"

baud = 50
frame_rate = wav_file.getframerate()
frames_per_symbol = frame_rate / baud

print("params:\n", wav_file.getparams())
print()

five = wav_file.readframes(5)
print("1st 5 frames raw:", five)
print("seconds =", wav_file.getnframes() / frame_rate)
print("frames / symbol =", frames_per_symbol)

wav_file.rewind()
two_symbols = wav_file.readframes(int(frames_per_symbol * 2))
print("bytes in 2 symbols =", len(two_symbols))
print()

# Make several objects for printing

pretty_hex_list = list(pretty_hex_string(two_symbols.hex()))
int_list = list(bytes2int_list(two_symbols))
dot_list = list(ints2dots(int_list))

n_bytes = 16
print("first %i bytes:\n" % n_bytes)
print(''.join(pretty_hex_list[:n_bytes * 2]))
print(int_list[:n_bytes // 2])
print()
print('\n'.join(dot_list[:n_bytes // 2]))
