include pylint.mk

DEVELOPER = developer.palette-software.com
PEM := ~/.ssh/PaletteStandardKeyPair2014-02-16.pem

PKGNAME := palette
VERSION := $(shell python -c 'import $(PKGNAME); print $(PKGNAME).__version__')
SDIST := $(PKGNAME)-$(VERSION).tar.gz

all: pylint sdist
.PHONY: all

###

sdist:
	python setup.py sdist
.PHONY: sdist

pylint:
	$(PYLINT) palette
.PHONY: pylint

doc:
	make -C doc html
.PHONY: doc

docs: doc
.PHONY: docs

###

clean:
	rm -rf build dist palette.egg-info
	find palette -name \*.py[co] -exec rm '{}' ';'
	make -C doc clean
.PHONY: clean

###

publish_doc: doc
	scp -r -i $(PEM) doc/_build/html/* ubuntu@$(DEVELOPER):/var/www/html
.PHONY: publish_doc

publish_docs: publish_doc
.PHONY: publish_docs

###

S3URL := s3://downloads.palette-software.com/sdk

s3-clean:
	aws s3 rm $(S3URL)/$(SDIST)
.PHONY: s3-clean

s3-publish: all
	aws s3 cp dist/$(SDIST) $(S3URL)/$(SDIST)
.PHONY: s3-publish

version:
	@echo $(VERSION)
.PHONY: version
