
all:
	python setup.py sdist
.PHONY: all

clean:
	rm -rf dist palette.egg-info
	find palette -name \*.py[co] -exec rm '{}' ';'
.PHONY: clean
