FROM python:3.12.2-bookworm
WORKDIR /app
ARG verze
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT [ "python", "src/main.py" ]
EXPOSE 80