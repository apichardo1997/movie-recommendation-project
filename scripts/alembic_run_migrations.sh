#!/bin/bash
docker compose run --rm backend alembic upgrade head
