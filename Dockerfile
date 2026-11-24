FROM python:3.12-slim

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    openssl \
    curl \
    git \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости и сертификаты
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY certs/ certs/
COPY scripts/ scripts/

# Шаг 1: Загрузка актуального Intermediate CA Certum (если не скачан локально)
RUN python scripts/fetch_certum_ca.py || true

# Шаг 2: Объединение системных сертификатов и кастомного Intermediate CA в единый бандл
RUN cat /etc/ssl/certs/ca-certificates.crt certs/certum-intermediate.crt > /tmp/full-ca.crt

# Шаг 3: Строгая проверка TLS-хоста во время сборки
RUN openssl s_client \
      -connect apostila.gov.md:443 \
      -servername apostila.gov.md \
      -verify_hostname apostila.gov.md \
      -verify_return_error \
      -CAfile /tmp/full-ca.crt \
      < /dev/null

COPY . .

CMD ["python", "scripts/pipeline.py"]
