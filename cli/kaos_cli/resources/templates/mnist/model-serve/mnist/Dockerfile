FROM ubuntu:16.04

MAINTAINER kaos <kaos@ki-labs.com>

# install python + nginx for inference
RUN apt-get -y update && \
    apt-get install -y --no-install-recommends \
    apt-utils \
    python3 \
    python3-pip \
    python3-setuptools \
    nginx \
    net-tools \
    curl \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# upgrade pip and remove cache
RUN pip3 install --upgrade pip

# copy source files to /opt/program
WORKDIR /opt/program
COPY . /opt/program/

# FYI -> serve is run as an executable in kaos!
RUN chmod +x serve

# set some environment variables
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"
ENV PYTHONENCODING=utf-8
ENV LANG=C.UTF-8

# ensure dependencies are handled
RUN if [ -f /opt/program/web-requirements.txt ] ; then pip3 install --no-cache-dir -r /opt/program/web-requirements.txt; fi
RUN if [ -f /opt/program/requirements.txt ] ; then pip3 install --no-cache-dir -r /opt/program/requirements.txt; fi
