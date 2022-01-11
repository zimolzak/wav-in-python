import sys
import wave
from wave_helpers import pretty_hex_string, bytes2int_list, ints2dots, freqs2bits
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np

wav_file = wave.open(sys.argv[1], 'r')  # fixme catch exception, "with"

# Free parameters
start_sample = 3080  # start of good mark/space in sample-data.wav
baud = 50  # symbol / sec
n_symbols_to_read = 50
seg_per_symbol = 3  # for STFT / FFT

# Calculated and derived vars
sample_rate = wav_file.getframerate()
bytes_per_sample = wav_file.getsampwidth()
samples_per_symbol = sample_rate / baud
n_samples_to_read = int(samples_per_symbol * n_symbols_to_read)

# Read from file
wav_file.setpos(start_sample)
wav_data = wav_file.readframes(n_samples_to_read)
n_samples_actually_read = len(wav_data) / bytes_per_sample
n_symbols_actually_read = n_samples_actually_read / sample_rate * baud

# Make 3 objects for printing
pretty_hex_list = list(pretty_hex_string(wav_data.hex()))
int_list = list(bytes2int_list(wav_data))
dot_list = list(ints2dots(int_list))

# Do the printing
n_frames_to_plot = 15
n_bytes_to_plot = n_frames_to_plot * bytes_per_sample
char_per_byte = 2  # That means hex chars. 1 B = 2 hex digits '01' or '0F' etc.

print("Params:\n", wav_file.getparams())
print()
print("File duration (s) =", wav_file.getnframes() / sample_rate)
print("Samples / FSK symbol =", samples_per_symbol)
print("Bytes in %f FSK symbols =" % n_symbols_actually_read, len(wav_data))
print("Seconds read =", n_samples_actually_read / sample_rate)
print()
print("First %i bytes (%i samples):" % (n_bytes_to_plot, n_frames_to_plot))
print(wav_data[:n_bytes_to_plot])
print()
print(''.join(pretty_hex_list[:n_bytes_to_plot * char_per_byte]))  # pretty hex list
print()
print(int_list[:n_bytes_to_plot // bytes_per_sample])  # int list
print()
print('\n'.join(dot_list[:n_bytes_to_plot // bytes_per_sample]))  # dot list

# Short time Fourier transform

print("\n\n# Fourier decoding of FSK\n")

f, t, Zxx = signal.stft(int_list, fs=sample_rate, nperseg=int(samples_per_symbol / seg_per_symbol))
# Zxx first axis is freq, second is times
# fixme - it is possible I don't understand the "nperseg" parameter.
print("Zxx (FFT result) shape, frequencies X time points:", Zxx.shape)

selected_indices = ((400 < f) * (f < 2000))
f_filtered = f[selected_indices]
print("FFT frequencies in pass band:", f_filtered)

Zxx_filtered = np.abs(Zxx[selected_indices], )
z_max = np.max(Zxx_filtered)  # global max just used for plot scale
max_freq_indices = Zxx_filtered.argmax(0)

# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.stft.html
plt.pcolormesh(t, f_filtered, Zxx_filtered, vmin=0, vmax=z_max, shading='gouraud')
plt.title('STFT Magnitude')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.savefig('stft.png')
#  plt.show()
# shift of 850 Hz. Mine by inspection is about 581 Hz and 1431 Hz
# one symbol is about 450 - 470 samples by inspection
# calculated at 441 samples/symbol
# 11.62 cycles in a low freq symbol, 28.62 in high freq.

print("\nFrequency bin values over time:")
print("One FFT segment MAYBE = %f ms = %i samples NOT REALLY" %
      (1000 / (baud * seg_per_symbol), samples_per_symbol / seg_per_symbol))
print(max_freq_indices)
print("\nBitstream:")
calculated_seg_per_symbol = len(max_freq_indices) / n_symbols_actually_read
print("Using %i segments / %i symbols = %f seg/sym" %
      (len(max_freq_indices), n_symbols_actually_read, calculated_seg_per_symbol))
bitstream = freqs2bits(max_freq_indices, calculated_seg_per_symbol)
print(bitstream)
print()

for cols in range(5, 12):
    # 5N1 = 7
    # 8N1 = 10
    if cols == 7:
        print("5N1")
    if cols == 10:
        print("8N1")
    N = len(bitstream)
    n_padding = cols - (N % cols)
    padding = [0] * n_padding
    bitstream_padded = np.append(bitstream, padding)
    rows = len(bitstream_padded) // cols
    print(np.reshape(bitstream_padded, (rows, cols)))
    print()
