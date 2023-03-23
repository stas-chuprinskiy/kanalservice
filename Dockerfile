FROM python:3.10-slim

WORKDIR /script
COPY config.py creds.json db.py exceptions.py requirements.txt script.py ./
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
