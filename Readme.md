# Python Frequency Shift Keying Analysis

Decodes a WAV file of frequency shift keying (FSK) noises to its
bitstream.

Bare-bones but cross-platform alternative to Sorcerer decoding
software. `fldigi` software does FSK but not enough raw bitstream
inspection for me.

Can be used for STANAG-4481 "NATO" radio signals. Specifically,
STANAG-4481F. The ones I received are at 50 baud, with a frequency
shift keying (FSK) or "RTTY" shift of 850Hz. Detection of the mark and
space tones (and the shift) is automatic. Allows reshaping bitstream
into various size rectangles, to allow inspection for various serial
asynchronous framings (like 5N1 or 8N1). Should work on any binary
(2-tone) FSK signal (not MFSK), but you may have to change passband
filter parameters if your mark/space tones don't match STANAG-4481.
Baud must always be set manually.

## Command line

```bash
python main.py sample-data.wav
# You will see stdout and a png will be created

python main.py signal.wav  # 10 second file
# png overwritten
```

## Within Python

```python
from wave_helpers import whole_pipeline

bitstream = whole_pipeline(infile='sample-data.wav', outfile=None)

# Now do something cool with bitstream. 
```

## Outline of approach

1. Read samples from the WAV file (22,050 values / sec).
2. Apply a short-time Fourier transform to find the most intense tone at any time point (300 values / sec).
3. Reduce the vector of tones to a vector of bits (50 values / sec).

## Requirements

- wave (Python Standard Library)
- SciPy
- Matplotlib
- NumPy
