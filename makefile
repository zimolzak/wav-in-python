all: htmlcov/index.html plot_main.png

.PHONY: all clean

htmlcov/index.html: wave_helpers.py printing.py test_wave_helpers.py test_printing.py
	py.test --cov=. --cov-report html

plot_main.png: main.py sample-data.wav wave_helpers.py printing.py
	python main.py sample-data.wav > output.txt

clean:
	rm -rf plot_main.png plot_default.png output.txt htmlcov/
