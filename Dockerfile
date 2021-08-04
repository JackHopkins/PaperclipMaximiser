FROM python:3.8-slim

RUN pip install --no-cache-dir fastapi uvicorn

COPY main.py /

CMD uvicorn --host 0.0.0.0 --port 8080 main:app