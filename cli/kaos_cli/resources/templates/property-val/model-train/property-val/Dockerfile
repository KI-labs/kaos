FROM python:3.7

WORKDIR /opt/program
COPY . /opt/program/

# FYI -> train is run as an executable in kaos!
RUN chmod +x train

# Don't buffer stdout and stderr
ENV PYTHONUNBUFFERED=TRUE


# Endpoint python dependency
RUN if [ -f /opt/program/requirements.txt ] ; then pip3 install --no-cache-dir -r /opt/program/requirements.txt; fi
