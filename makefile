htmlcov/index.html: test_wave_helpers.py wave_helpers.py
	py.test --cov=. --cov-report html
