build-test:
	docker build . --tag kaos-cli:testing --file ./Dockerfile

# to be called locally: docker provides isolation
test-unit-docker: build-test
	docker run -it kaos-cli:testing tox

# direct pytest call: to be used by travis
test-unit:
	pip3 install tox
	tox .
