FROM python:3.12.6-slim

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y nano

RUN pip install --upgrade pip setuptools

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install waitress

RUN echo 'api: "api.open-meteo.com"\n\
server_description: ""\n\
# Pour remplir les paramètres ci-dessous, veuillez consulter https://docs.proxyscrape.com/\n\
use_proxies: true\n\
proxy_country_code: "all"\n\
proxy_max_timeout: 50' > config.yml

EXPOSE 8080

ENV THREADS=16

CMD /bin/sh -c "waitress-serve --port=8080 --threads=${THREADS} --call main:init"