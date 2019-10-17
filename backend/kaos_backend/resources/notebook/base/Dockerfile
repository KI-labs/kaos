FROM python:3.7

WORKDIR /opt/program
ENV HOME /opt/program

ADD . /opt/program/
RUN ls -la

# Endpoint python dependency
RUN if [ -f /opt/program/requirements.txt ] ; then pip3 install --no-cache-dir -r /opt/program/requirements.txt; fi
