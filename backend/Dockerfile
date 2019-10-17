FROM python:3.7.4-slim-stretch

ENV LANG C.UTF-8

RUN apt-get update && apt-get install -y libssl-dev libpq-dev git gunicorn \
                                         build-essential libfontconfig1 libfontconfig1-dev

ADD backend/requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

ADD model/ /lib/model
RUN pip3 install /lib/model

ADD backend/ /app/src

WORKDIR /app/src

RUN pip3 install -U tox

ENV PORT 8080

# FIXME – timeout is a temporary workaround
CMD ["gunicorn", "kaos_backend.app:app", "--log-level=DEBUG", "--config=kaos_backend/config.py", "--timeout=3600"]
