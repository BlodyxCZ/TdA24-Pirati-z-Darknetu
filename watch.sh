#!/bin/bash
docker compose up --build -d
docker compose watch
docker compose down