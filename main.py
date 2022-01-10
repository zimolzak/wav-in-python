import sys
import wave
from wave_helpers import pretty_hex_string, bytes2int_list, ints2dots
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np

wav_file = wave.open(sys.argv[1], 'r')  # fixme catch exception, "with"

# Free parameters
start_sample = 3080  # start of good mark/space in sample-data.wav
baud = 50  # symbol / sec
n_symbols_to_read = 2

# Calculated and derived vars
sample_rate = wav_file.getframerate()
bytes_per_sample = wav_file.getsampwidth()
samples_per_symbol = sample_rate / baud
n_samples_to_read = int(samples_per_symbol * n_symbols_to_read)

# Read from file
wav_file.setpos(start_sample)
wav_data = wav_file.readframes(n_samples_to_read)

# Make 3 objects for printing
pretty_hex_list = list(pretty_hex_string(wav_data.hex()))
int_list = list(bytes2int_list(wav_data))
dot_list = list(ints2dots(int_list))

# Do the printing
n_frames_to_plot = 15
n_bytes_to_plot = n_frames_to_plot * bytes_per_sample
char_per_byte = 2  # A byte is two hex digits '01' or '0F' etc.

print("Params:\n", wav_file.getparams())
print()
print("File duration (s) =", wav_file.getnframes() / sample_rate)
print("Frames / FSK symbol =", samples_per_symbol)
print("Bytes in %i FSK symbols =" % n_symbols_to_read, len(wav_data))
print("Seconds read =", n_samples_to_read / sample_rate)
print()
print("First %i bytes (%i samples):" % (n_bytes_to_plot, n_frames_to_plot))
print(wav_data[:n_bytes_to_plot])
print()
print(''.join(pretty_hex_list[:n_bytes_to_plot * char_per_byte]))  # pretty hex list
print()
print(int_list[:n_bytes_to_plot // bytes_per_sample])  # int list
print()
print('\n'.join(dot_list[:n_bytes_to_plot // bytes_per_sample]))  # dot list

f, t, Zxx = signal.stft(int_list, fs=sample_rate)

f_above = (f > 400)
f_filt = f[f_above]
print(f_above)
print(f_filt)
# Zxx first axis is freq, second is times
print(Zxx.shape)
Zxx_filt = np.abs(Zxx[f_above], )
zmax = np.max(Zxx_filt)

# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.stft.html
plt.pcolormesh(t, f_filt, Zxx_filt, vmin=0, vmax=zmax, shading='gouraud')
plt.title('STFT Magnitude')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
print(plt)
plt.savefig('stft.png')
#  plt.show()
# shift of 850 Hz. Mine by inspection is about 581 Hz and 1431 Hz
