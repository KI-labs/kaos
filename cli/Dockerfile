FROM ubuntu:18.04
ENV LANG C.UTF-8

RUN apt-get update && apt-get install -y python3.7 python3.7-dev \
                                         python3-pip libssl-dev libpq-dev git \
                                         build-essential libfontconfig1 libfontconfig1-dev

WORKDIR /app

RUN pip3 install -U tox

ADD . /app
