FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false

RUN poetry install --without dev --no-root

COPY . .

ENV FLASK_APP=enginy/app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]
