import sys
from wave_helpers import whole_pipeline

if __name__ == '__main__':
    whole_pipeline(infile=sys.argv[1], outfile='plot_main.png', n_symbols_to_read=None)  # throwaway return value
