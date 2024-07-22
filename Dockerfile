FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y nano && \
    pip install --no-cache-dir -r requirements.txt

RUN echo 'api: "api.open-meteo.com"\n\
server_description: ""\n\
# Pour remplir les paramètres ci-dessous, veuillez consulter https://docs.proxyscrape.com/\n\
proxy_country_code: "all"\n\
proxy_max_timeout: 50' > config.yml

EXPOSE 8080

CMD ["waitress-serve", "--port=8080", "--threads=8", "--call", "main:init"]
