FROM python:3.9-bookworm

WORKDIR /flask-app

COPY requirements/base.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY Enginy/ .

ENV FLASK_SECRET_KEY="your-secret-key"

CMD ["flask", "run", "--host=0.0.0.0"]