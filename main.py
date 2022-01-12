import sys
import wave
from wave_helpers import Fourier, Bitstream, WaveData

with wave.open(sys.argv[1], 'r') as wav_file:
    W = WaveData(wav_file, start_sample=0, n_symbols_to_read=750, baud=50)
    W.print_wav_file_basics(n_samples_to_plot=15)

# Short time Fourier transform
F = Fourier(W, seg_per_symbol=3)
F.apply_passband(400, 2000)
F.print_summary()
F.save_plot('stft.png')

# shift of 850 Hz. Mine by inspection is about 581 Hz and 1431 Hz
# one symbol is about 450 - 470 samples by inspection
# calculated at 441 samples/symbol
# 11.62 cycles in a low freq symbol, 28.62 in high freq.

# Translate FFT data to FSK bitstream
B = Bitstream(F)
B.print_summary()
B.print_shapes(5, 12)

# fixme - make an 8N1 and 5N1 decoder on B.stream
