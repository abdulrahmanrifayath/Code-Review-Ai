# ReviewAI Enterprise Production Deployment Guide

This document provides a comprehensive operational guide for building, configuring, deploying, and maintaining **ReviewAI** in a secure, high-availability production environment.

---

## Architecture Overview

ReviewAI operates as a containerized microservice architecture orchestrated via **Docker Compose**:

- **NGINX Reverse Proxy**: Terminates SSL/TLS (HTTPS), enforces HSTS & Security Headers, applies Rate Limiting, proxies WebSockets, and balances traffic to frontend and backend containers.
- **Frontend Container**: NGINX Alpine serving pre-compiled React Vite Single-Page Application (SPA).
- **Backend Container**: Scaled FastAPI server powered by Gunicorn (`uvicorn.workers.UvicornWorker`) providing REST & WebSocket APIs.
- **Worker Container**: Redis background queue worker (`python -m app.workers.run_worker --worker-type all`) executing asynchronous webhook, AI analysis, static analysis, report generation, and notification tasks.
- **PostgreSQL 16 Database**: Persistent relational database storing users, repositories, pull requests, analysis findings, reports, and notifications.
- **Redis 7 Cache & Broker**: Persistent AOF Redis instance serving as task broker, session cache, and retry queue store.

---

## Production Prerequisites

1. **Host Server Specs**:
   - Ubuntu 22.04 LTS / Debian 12 / RHEL 9 (Minimum: 4 vCPU, 8 GB RAM, 50 GB SSD).
   - Docker Engine v24.0+ and Docker Compose v2.20+.
   - Domain name (e.g. `reviewai.yourdomain.com`) pointing to host server IP via DNS `A` record.
   - Open Ports: `80` (HTTP), `443` (HTTPS), `22` (SSH).

2. **Required Production Secrets**:
   - GitHub OAuth App Client ID & Secret
   - GitHub Webhook HMAC Secret
   - OpenAI API Key (`sk-proj-...`)
   - Strong PostgreSQL password & JWT `SECRET_KEY` (min 64 chars)

---

## Step 1: Environment & Secrets Setup

1. Clone repository to `/opt/reviewai` on production server:
   ```bash
   git clone https://github.com/abdulrahmanrifayath/Code-Review-Ai.git /opt/reviewai
   cd /opt/reviewai
   ```

2. Copy production environment template:
   ```bash
   cp .env.production.example .env
   ```

3. Configure secrets in `.env`:
   ```env
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   SECRET_KEY=generate-a-secure-random-64-character-key
   POSTGRES_USER=reviewai
   POSTGRES_PASSWORD=your_secure_postgres_password
   POSTGRES_DB=reviewai_db
   REDIS_PASSWORD=your_secure_redis_password
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   GITHUB_WEBHOOK_SECRET=your_github_webhook_secret
   OPENAI_API_KEY=sk-proj-your-openai-api-key
   ```

---

## Step 2: Provision HTTPS & Let's Encrypt SSL

Automate SSL certificate provisioning with Certbot using the included initialization script:

```bash
chmod +x scripts/init-letsencrypt.sh
./scripts/init-letsencrypt.sh reviewai.yourdomain.com admin@yourdomain.com
```

This script:
1. Generates a temporary dummy certificate to allow NGINX to boot cleanly.
2. Boots NGINX and executes Certbot's Webroot ACME challenge.
3. Obtains production Let's Encrypt TLS v1.2/v1.3 certificates.
4. Reloads NGINX with HTTPS enabled.

---

## Step 3: Run Database Migrations

Run Alembic database migrations using the automated migration script:

```bash
chmod +x scripts/migrate.sh
./scripts/migrate.sh
```

---

## Step 4: Docker Compose Orchestration

Start all production services in detached mode:

```bash
docker compose -f docker-compose.prod.yml up -d
```

Verify running containers:
```bash
docker compose -f docker-compose.prod.yml ps
```

Container List:
- `reviewai_db_prod` (healthy)
- `reviewai_redis_prod` (healthy)
- `reviewai_backend_prod` (healthy)
- `reviewai_worker_prod` (running)
- `reviewai_frontend_prod` (running)
- `reviewai_nginx_prod` (running)

---

## Step 5: Continuous Deployment (GitHub Actions)

Add the following environment secrets in your GitHub Repository settings (**Settings -> Secrets and variables -> Actions**):

- `PROD_SERVER_IP`: IP address of production server.
- `PROD_SERVER_USER`: SSH user (e.g. `ubuntu` or `root`).
- `PROD_SSH_PRIVATE_KEY`: Private SSH key for server authentication.

On every push to `main`, `.github/workflows/deploy.yml` will automatically:
1. Run backend ruff linter and engine unit tests.
2. Run frontend TypeScript type checking and ESLint build.
3. Build and push production Docker images to GitHub Container Registry (`ghcr.io`).
4. SSH into production server, pull latest images, run `alembic upgrade head`, and execute zero-downtime container updates.

---

## Monitoring, Metrics & Logs

### Structured JSON Logging
Production logs are formatted in structured JSON emitted to stdout/stderr:

```bash
docker compose -f docker-compose.prod.yml logs -f --tail 100 backend
```

### Prometheus Metrics Endpoint
Scrape production performance metrics at `/api/v1/metrics`:

```bash
curl -f https://reviewai.yourdomain.com/api/v1/metrics
```

Exposed metrics:
- `http_requests_total`: Total HTTP requests handled.
- `http_errors_total`: 5xx error counter.
- `http_request_duration_seconds_avg`: Request duration gauge.

### Production Health Check
Query health status:
```bash
curl -f https://reviewai.yourdomain.com/api/v1/health
```

---

## Backups & Maintenance

### PostgreSQL Database Backup Cron
Add a daily cron job to backup PostgreSQL:

```bash
0 2 * * * docker exec reviewai_db_prod pg_dump -U reviewai reviewai_db | gzip > /backups/db_$(date +\%F).sql.gz
```
