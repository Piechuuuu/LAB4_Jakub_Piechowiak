FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# (opcjonalnie) zależności systemowe; zwykle wystarcza
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# produkcyjnie: gunicorn
CMD gunicorn -w 2 -b 0.0.0.0:${PORT:-5000} app:app