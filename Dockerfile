FROM python:3.11

WORKDIR /app

RUN pip install poetry==1.7.1

COPY pyproject.toml ./

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --without dev

COPY . .

ENV FLASK_APP=Enginy/app.py
ENV PYTHONPATH=/app
ENV FLASK_SECRET_KEY="your-secret-key"

CMD ["flask", "run", "--host=0.0.0.0"]