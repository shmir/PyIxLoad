
.PHONY: build
build:
	rm -rf dist/*
	python setup.py bdist_wheel

upload:
	make build
	twine upload --repository-url http://localhost:8036 --user pypiadmin --password pypiadmin dist/*
