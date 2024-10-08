FROM python:3.13-slim

WORKDIR /app

COPY . /

RUN pip install --upgrade pip && \
    pip install google-api-python-client requests

CMD python update.py
