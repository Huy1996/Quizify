FROM python:3.10.12

WORKDIR /app
COPY app/ /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/local-auth.json 
ENV PROJECT_ID="kai-dev-424208"