all: htmlcov/index.html stft.png

.PHONY: all clean

htmlcov/index.html: test_wave_helpers.py wave_helpers.py
	py.test --cov=. --cov-report html

stft.png: main.py sample-data.wav
	python main.py sample-data.wav

clean:
	rm -rf stft.png htmlcov/
