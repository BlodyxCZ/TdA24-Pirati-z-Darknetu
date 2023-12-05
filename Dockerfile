FROM python:3.12.0-bookworm
WORKDIR /app
ARG verze
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT python main.py $port
EXPOSE 80

# Databáze
#FROM surrealdb/surrealdb:latest
#WORKDIR /db
#COPY . .
#ENTRYPOINT surreal start --log trace file:database.db