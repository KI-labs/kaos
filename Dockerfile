# base alpine/python image
FROM python:3.7-alpine
MAINTAINER kaos <kaos@ki-labs.com>
WORKDIR /kaos

# required ENVs
ENV KAOS_HOME /kaos
ENV LANG C.UTF-8

# add kaos
ADD . /kaos/

# ensure KAOS_HOME is properly "read"
RUN mkdir -p /kaos/.git && echo "KI-labs/kaos.git" > /kaos/.git/config

# install kaos python modules
RUN cd /kaos/model/ && python3 setup.py install
RUN cd /kaos/cli/ && python3 setup.py install

# install kaos system requirements
RUN apk add --update --no-cache curl bash jq coreutils graphviz tree nano gzip ttf-freefont

# default entrypoint
ENTRYPOINT ["kaos"]
