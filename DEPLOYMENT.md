# Push to Registry & Deployment Guide

## 1. Local Push to Docker Hub

### Prerequisites
```bash
docker login
# or with environment variables:
export REGISTRY_USER=your-username
export REGISTRY_PASSWORD=your-token
```

### Push via Script
```bash
# Latest tag
./push-to-registry.sh latest

# Specific version
./push-to-registry.sh v1.0.0
```

### Push via Makefile
```bash
make push
```

### Manual Push
```bash
docker compose build actor-app-dev
docker tag actor_dev_env-actor-app-dev:latest your-username/actor-dev-env:latest
docker push your-username/actor-dev-env:latest
```

## 2. Private Registry (Self-Hosted or Harbor)

### Update .env
```bash
# .env.local
REGISTRY_URL=registry.example.com
REGISTRY_USER=your-user
REGISTRY_PASSWORD=your-token
```

### Push to Private Registry
```bash
export REGISTRY_URL=registry.example.com
export REGISTRY_USER=your-user
export REGISTRY_PASSWORD=your-token
./push-to-registry.sh latest
```

## 3. GitHub Actions CI/CD Setup

### Prerequisites
1. Fork/push to GitHub repository
2. Add secrets to GitHub repository (Settings → Secrets):
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub personal access token

### Workflow Triggers
- Push to `main` or `develop` branches
- Pull requests on `main` or `develop`
- Manual trigger via `workflow_dispatch`

### Features
- Automatic build and push on code changes
- Container test run
- Dockerfile linting (hadolint)
- Security scanning (Trivy)
- GitHub SARIF upload for vulnerability tracking

### View Results
- Go to Actions tab on GitHub
- Check build logs
- Security tab shows Trivy results

## 4. Monitoring Stack

### Start Monitoring
```bash
make monitoring-up
```

### Access
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **cAdvisor**: http://localhost:8080
- **AlertManager**: http://localhost:9093

### Metrics Collected
- Container CPU, memory, network I/O
- Healthcheck status
- Restart frequency
- Volume usage

### Configure Alerts
Edit `alerts.yml` to customize thresholds:
- Container unhealthy
- CPU > 80%
- Memory > 85%
- Frequent restarts

## 5. Deployment to Remote Server

### Option A: Pull from Registry
```bash
docker login
docker run -d \
  --name actor-dev-env \
  -v actor_audit_data:/app/.audit \
  your-username/actor-dev-env:latest
```

### Option B: Deploy with Compose from Registry
```bash
# docker-compose.yml - update image
services:
  actor-app-dev:
    image: your-username/actor-dev-env:latest
    # ... rest of config
```

Then:
```bash
docker compose up -d
```

### Option C: Docker Stack (Swarm)
```bash
docker stack deploy -c docker-compose.yml actor-dev-env
```

## 6. Continuous Deployment (CD)

### Add to Workflow for Auto-Deploy
1. SSH into production server
2. Pull latest image
3. Redeploy with compose

```yaml
- name: Deploy to production
  if: github.ref == 'refs/heads/main'
  run: |
    ssh user@prod-server << 'EOF'
    cd /opt/actor-dev-env
    docker compose pull
    docker compose up -d
    docker compose logs -f --tail 20
    EOF
```

## 7. Rollback Strategy

### Keep multiple tags
```bash
docker tag actor_dev_env-actor-app-dev:latest your-username/actor-dev-env:v1.0.0
docker tag actor_dev_env-actor-app-dev:latest your-username/actor-dev-env:stable
docker push your-username/actor-dev-env:v1.0.0
docker push your-username/actor-dev-env:stable
```

### Rollback
```bash
# Update docker-compose.yml to use previous tag
docker compose pull
docker compose up -d
```

## 8. Secrets & Security

### Never Commit
- `.env` files with credentials
- Docker credentials
- Private keys

### Use
- GitHub Secrets for CI/CD
- Environment variables for local builds
- Docker credential helpers
- Private registry authentication

### Scan Images
```bash
trivy image your-username/actor-dev-env:latest
```

## 9. Useful Commands

```bash
# List all images
docker images | grep actor-dev-env

# Check image size
docker images your-username/actor-dev-env --format "table {{.Repository}}\t{{.Size}}"

# Inspect running container
docker inspect actor_dev_env-actor-app-dev-1

# View logs with timestamps
docker compose logs --timestamps

# Check volume usage
docker system df

# Prune unused images
docker image prune -a --filter "until=720h"
```

## 10. Monitoring & Alerts

### Check Healthcheck
```bash
docker inspect actor_dev_env-actor-app-dev-1 --format='{{json .State.Health}}'
```

### Alert Webhooks
Configure in `alertmanager.yml`:
```yaml
receivers:
  - name: 'critical-alerts'
    webhook_configs:
      - url: 'http://your-webhook-endpoint'
```

### Integration Options
- Slack: Use AlertManager webhook
- PagerDuty: AlertManager integration
- Email: SMTP in AlertManager
- Custom: HTTP endpoint

