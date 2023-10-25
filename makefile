# Makefile

.PHONY: install

install:
	# Use the command-line argument as an argument for your command
	conda install $(PACKAGE) -c conda-forge

run:
	python src/axidoc/main.py

test:
	pytest
