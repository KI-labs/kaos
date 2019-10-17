FROM ubuntu:18.04

MAINTAINER kaos <kaos@ki-labs.com>

ARG PROVIDER

ENV LANG C.UTF-8

RUN apt update
RUN apt-get update && apt-get install -y python3.7 python3.7-dev \
                                         python3-pip libssl-dev libpq-dev git \
                                         build-essential libfontconfig1 libfontconfig1-dev

# install docker
RUN apt-get install -y apt-transport-https ca-certificates curl software-properties-common
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
RUN apt-get update && apt-get install -y docker-ce

RUN echo "$PROVIDER"

# install gcloud
RUN if [ "$PROVIDER" = "GCP" ] ; then \
        echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list ; \
        curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - ; \
        apt-get update && apt-get install -y google-cloud-sdk ; \
    elif [ "$PROVIDER" = "AWS" ] ; then \
        pip3 install awscli; \
        echo "export PATH=~/.local/bin:$PATH" >> ~/.bashrc; \
    fi \
