FROM python:3.12.6-slim

WORKDIR /app

COPY . .

VOLUME /data

RUN apt-get update && \
    apt-get install -y nano

RUN pip install --upgrade pip setuptools

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install waitress

EXPOSE 8080

ENV THREADS=16

CMD /bin/sh -c "python3 -u docker-init.py && waitress-serve --port=8080 --threads=${THREADS} --call main:init"