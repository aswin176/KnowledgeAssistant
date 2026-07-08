# Deployment Guide

## Docker Production

```bash
cp backend/.env.example .env.production
# Edit production values

docker compose -f docker-compose.prod.yml up -d
docker exec eutridats-ollama ollama pull qwen3
```

## Railway

1. Create a new project on [Railway](https://railway.app)
2. Add services: Neo4j (plugin), Redis, and deploy from GitHub
3. Set environment variables from `.env.production`
4. Deploy backend and frontend as separate services

```toml
# railway.toml
[build]
builder = "dockerfile"
dockerfilePath = "backend/Dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
```

## Render

1. Create a Web Service for the backend
2. Set build command: `pip install poetry && poetry install && poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add Neo4j via [Neo4j Aura Free Tier](https://neo4j.com/cloud/aura-free/)
4. Deploy frontend as a Static Site with `npm run build`

## Coolify

1. Add your Git repository in Coolify
2. Select Docker Compose deployment
3. Use `docker-compose.prod.yml`
4. Configure environment variables in Coolify UI
5. Enable auto-deploy on push

## VPS (Ubuntu)

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Clone and deploy
git clone <repo> /opt/eutridats
cd /opt/eutridats
cp backend/.env.example .env.production
# Edit .env.production with production values

docker compose -f docker-compose.prod.yml up -d

# Setup reverse proxy with Caddy
apt install caddy
cat > /etc/caddy/Caddyfile << 'EOF'
yourdomain.com {
    reverse_proxy localhost:3000
}

api.yourdomain.com {
    reverse_proxy localhost:8000
}
EOF
systemctl restart caddy
```

## Environment Variables (Production)

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | App secret key |
| `JWT_SECRET_KEY` | Yes | JWT signing key |
| `NEO4J_URI` | Yes | Neo4j connection URI |
| `NEO4J_PASSWORD` | Yes | Neo4j password |
| `OLLAMA_BASE_URL` | Yes | Ollama API URL |
| `ADMIN_PASSWORD` | Yes | Admin login password |
| `CORS_ORIGINS` | Yes | Allowed frontend origins |
| `TELEGRAM_BOT_TOKEN` | No | Telegram bot token |

## Health Monitoring

```bash
curl https://api.yourdomain.com/api/v1/health
```

Expected response:

```json
{
  "status": "healthy",
  "neo4j": true,
  "llm": true,
  "version": "0.1.0"
}
```

## Backup

Neo4j data is persisted in Docker volumes. Back up regularly:

```bash
docker exec eutridats-neo4j neo4j-admin database dump neo4j --to-path=/backups
docker cp eutridats-neo4j:/backups ./backups
```
