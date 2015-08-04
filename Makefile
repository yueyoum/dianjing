SHELL = /bin/bash

.PHONY: submodule
submodule:
	git submodule foreach git pull
	./compile-protobuf.py


.PHONY: restart
restart:
	./restart.sh


.PHONY: test
test:
	nosetests -w tests


