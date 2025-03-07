SOURCES=$(wildcard src/*)

# Default rule builds all targets
all: build/index.html

# Create the output directory
build:
	mkdir -p build

# For any target build/foo.html, run pandoc on foo.md
build/%.html: ${SOURCES} build.sh build
	bash build.sh > $@

# Delete all build artifacts
clean:
	rm -rf build

# Tell make that these targets don't correspond to real files.
.PHONY: all clean

