#FROM python:3.11-slim
FROM public.ecr.aws/docker/library/python:3.12-slim


WORKDIR /code

COPY pyproject.toml  poetry.lock ./

RUN python -m pip install poetry
RUN poetry self add poetry-plugin-export
RUN poetry export --output=requirements.txt
RUN python -m pip install -r requirements.txt
