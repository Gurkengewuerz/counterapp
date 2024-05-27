# Nutze ein leichtgewichtiges Python-Image basierend auf Alpine
FROM python:3.12-alpine

# Setze Umgebungsvariablen
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installiere Abhängigkeiten
RUN apk update && apk add --no-cache \
    build-base \
    gcc \
    musl-dev \
    linux-headers \
    sqlite-dev

# Erstelle und wechsle in das Verzeichnis der Anwendung
WORKDIR /app

# Kopiere requirements.txt und installiere Python-Abhängigkeiten
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest der Anwendung
COPY . /app/

# Exponiere den Port, auf dem die Anwendung läuft
EXPOSE 5000

# Führe die Anwendung aus
CMD ["python", "app.py"]
