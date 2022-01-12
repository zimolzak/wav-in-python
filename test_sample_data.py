from wave_helpers import whole_pipeline


def test_main():
    whole_pipeline(infile='sample-data.wav', outfile='plot_default.png', n_symbols_to_read=100)
    # throwaway return value
    # Quit at 100 symbols = 2 sec, so effectively read the whole of sample-data.wav, which is only 1 sec.
    # fixme - very basic, no asserts at all, just needs to run without error.
