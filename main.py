import sys
import wave
from wave_helpers import pretty_hex_string, bytes2int_list, ints2dots

wav_file = wave.open(sys.argv[1], 'r')  # fixme catch exception, "with"

# Free parameters
first_sample = 3080  # start of good mark/space in sample-data.wav
baud = 50  # symbol / sec
n_symbols_to_read = 2

# Calculated and derived vars
sample_rate = wav_file.getframerate()
bytes_per_sample = wav_file.getsampwidth()
samples_per_symbol = sample_rate / baud
n_samples_to_read = int(samples_per_symbol * n_symbols_to_read)

# Read from file
wav_file.setpos(first_sample)
symbols = wav_file.readframes(n_samples_to_read)

# Make 3 objects for printing
pretty_hex_list = list(pretty_hex_string(symbols.hex()))
int_list = list(bytes2int_list(symbols))
dot_list = list(ints2dots(int_list))

# Do the printing
n_frames_to_plot = 15
n_bytes_to_plot = n_frames_to_plot * bytes_per_sample
char_per_byte = 2  # A byte is two hex digits '01' or '0F' etc.

print("Params:\n", wav_file.getparams())
print()
print("File duration (s) =", wav_file.getnframes() / sample_rate)
print("Frames / FSK symbol =", samples_per_symbol)
print("Bytes in %i FSK symbols =" % n_symbols_to_read, len(symbols))
print()
print("First %i bytes (%i samples):" % (n_bytes_to_plot, n_frames_to_plot))
print(symbols[:n_bytes_to_plot])
print()
print(''.join(pretty_hex_list[:n_bytes_to_plot * char_per_byte]))
print()
print(int_list[:n_bytes_to_plot // bytes_per_sample])
print()
print('\n'.join(dot_list[:n_bytes_to_plot // bytes_per_sample]))
