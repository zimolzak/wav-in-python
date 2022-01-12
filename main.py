import sys
from wave_helpers import whole_pipeline

if __name__ == '__main__':
    whole_pipeline(sys.argv[1], 'plot_main.png')  # throwaway return value
