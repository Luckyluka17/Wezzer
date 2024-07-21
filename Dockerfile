FROM python:3.10-slim

WORKDIR /Docker

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["waitress-serve", "--port=8080", "--threads=8", "--call", "main:init"]