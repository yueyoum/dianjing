SHELL = /bin/bash

.PHONY: protobuf
protobuf:
	cd protobuf && git pull
	./compile-protobuf.py

.PHONY: restart
restart:
	./restart.sh

.PHONY: test
test:
	nosetests -w tests


