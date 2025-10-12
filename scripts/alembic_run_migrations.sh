#!/bin/bash
docker compose run --rm api alembic upgrade head
