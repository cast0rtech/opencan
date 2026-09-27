# ==========================================
# STAGE 1: Compilación de Frontend (Vite)
# ==========================================
FROM --platform=$BUILDPLATFORM node:20-bookworm-slim AS frontend-builder
WORKDIR /build

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ==========================================
# STAGE 2: Preparación del Entorno Python
# ==========================================
FROM python:3.11-slim-bookworm AS backend-builder
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# STAGE 3: Runtime Final No Privilegiado
# ==========================================
FROM python:3.11-slim-bookworm AS runtime

LABEL maintainer="SolarHub DevOps Team"
LABEL org.opencontainers.image.title="SolarHub EMS Edge"
LABEL org.opencontainers.image.licenses="MIT"

# Dependencias mínimas de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario y grupo de servicio
RUN groupadd -g 10001 edgegroup && \
    useradd -u 10001 -g edgegroup -s /bin/bash -m edgeuser

WORKDIR /app

# Copiar entorno virtual Python y artefactos estáticos
COPY --from=backend-builder /app/venv /app/venv
COPY --from=frontend-builder /build/dist /app/static
COPY backend/app /app/app
COPY config.yaml /app/config.yaml

# Copiar configuraciones de Nginx y Supervisord
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Crear carpetas de datos y asignar permisos de ejecución al usuario no root
RUN mkdir -p /app/data /tmp/client_temp /var/log/nginx /var/lib/nginx && \
    chown -R edgeuser:edgegroup /app /tmp /var/log/nginx /var/lib/nginx /etc/nginx

ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER edgeuser

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://127.0.0.1:8080/api/v1/status || exit 1

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
