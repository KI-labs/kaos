build-test:
	# tag 'testing' so that it does not interfere
	# with the image produced by 'build-local'
	docker build . --tag kaos-backend:testing --file ./Dockerfile

run-local: build-test
	docker run -it -p 127.0.0.1:8080:8080/tcp kaos-backend:testing

# to be called locally: docker provides isolation
test-unit-docker: build-test
	docker run -it kaos-backend:testing tox

# direct pytest call: to be used by travis
test-unit:
	pip3 install tox
	tox .
	rm -r kaos_backend.egg-info
