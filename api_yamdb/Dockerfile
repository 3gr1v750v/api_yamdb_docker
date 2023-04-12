FROM python:3.7-slim

RUN apt-get update && apt-get install -y \
    && pip install --upgrade pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0:8000", "api_yamdb.wsgi:application"]
