import sys

sys.path.append(".")

from server.backend.config import config

print("Postgres User:", config.postgres_user)
