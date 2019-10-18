FROM nvidia/cuda:10.0-cudnn7-devel

WORKDIR /opt/program
ENV HOME /opt/program

ADD . /opt/program/

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get install -y python3.5 python3-pip

RUN rm /usr/bin/python3 && \
    ln -s /usr/bin/python3.5 /usr/bin/python3

ENV LD_LIBRARY_PATH /usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Don't buffer stdout and stderr
ENV PYTHONUNBUFFERED=TRUE

# Endpoint python dependency
RUN if [ -f /opt/program/requirements.txt ] ; then pip3 install --no-cache-dir -r /opt/program/requirements.txt; fi
