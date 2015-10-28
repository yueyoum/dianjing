SHELL = /bin/bash

.PHONY: protobuf
protobuf:
	cd protobuf && git pull
	./compile-protobuf.py

.PHONY: ext
ext:
	cd c_src && git pull
	cp c_src/formula.c extension/
	source env/bin/activate && cd extension && python setup.py install

.PHONY: compile
compile:
	source env/bin/activate && cd extension && python setup.py install

.PHONY: restart
restart:
	./restart.sh

.PHONY: test
test:
	nosetests -w tests


