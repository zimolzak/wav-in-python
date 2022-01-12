all: htmlcov/index.html plot_main.png

.PHONY: all clean

htmlcov/index.html: test_wave_helpers.py wave_helpers.py printing.py test_sample_data.py
	py.test --cov=. --cov-report html

plot_main.png: main.py sample-data.wav wave_helpers.py printing.py
	python main.py sample-data.wav > output.txt

clean:
	rm -rf plot_main.png plot_default.png output.txt htmlcov/
