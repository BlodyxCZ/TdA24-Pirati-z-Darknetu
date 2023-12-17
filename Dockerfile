FROM python:3.12.0-bookworm
WORKDIR /app
ARG verze
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT [ "python", "src/main.py" ]
EXPOSE 80

# Databáze
#FROM surrealdb/surrealdb:latest
#WORKDIR /db
#COPY . .
#ENTRYPOINT surreal start --log trace file:database.db