include pylint.mk

all: pylint sdist
.PHONY: all

sdist:
	python setup.py sdist
.PHONY: sdist

pylint:
	$(PYLINT) palette
.PHONY: pylint

doc:
	make -C doc html
.PHONY: doc

clean:
	rm -rf dist palette.egg-info
	find palette -name \*.py[co] -exec rm '{}' ';'
	make -C doc clean
.PHONY: clean
