# List all markdown files
SOURCES=$(wildcard *.md)
# Convert foo.md to build/foo.html
TARGETS=$(foreach src,$(SOURCES),build/$(basename $(src)).html)

# Default rule builds all targets
all: ${TARGETS}

# Create the output directory
build:
	mkdir -p build

# For any target build/foo.html, run pandoc on foo.md
build/%.html: %.md build
	pandoc -f markdown-smart -t html $< > $@

# Delete all build artifacts
clean:
	rm -rf build

# Tell make that these targets don't correspond to real files.
.PHONY: all clean

