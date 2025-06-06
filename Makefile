.PHONY: install clean reinstall help run

install:
	pip install --editable .

clean:
	rm -rf dist build *.egg-info

reinstall: clean install

help:
	airtable-export --help
