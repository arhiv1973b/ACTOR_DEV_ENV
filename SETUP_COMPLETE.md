# Actor Dev Env - Complete Security & DevOps Setup

## What Was Implemented

### 1. **Image Optimization & Registry Push**
- ✅ `.dockerignore`: Excludes 274MB of unnecessary files (PDFs, cache, media)
- ✅ `push-to-registry.sh`: Automates build, tag, push to Docker Hub or private registry
- ✅ `Makefile`: Convenient commands (`make build`, `make push`, `make run`)

### 2. **Monitoring Stack (docker-compose.monitoring.yml)**
- ✅ **Prometheus**: Scrapes metrics from cAdvisor every 15s
- ✅ **Grafana**: Dashboards with provisioned datasource (http://localhost:3000)
- ✅ **cAdvisor**: Collects container CPU, memory, network, disk metrics
- ✅ **AlertManager**: Routes alerts to webhooks/integrations

### 3. **Alerting Rules (alerts.yml)**
- ✅ Container unhealthy (critical)
- ✅ CPU > 80% (warning)
- ✅ Memory > 85% (warning)
- ✅ Frequent restarts (warning)
- ✅ Missing audit data (critical)

### 4. **CI/CD Pipeline (.github/workflows/build-and-deploy.yml)**
- ✅ Automatic build on push to main/develop
- ✅ Docker Buildx with layer caching (faster rebuilds)
- ✅ Container smoke test (verify events.json creation)
- ✅ Dockerfile linting (hadolint)
- ✅ Security scanning (Trivy) with GitHub SARIF upload
- ✅ Automatic push to Docker Hub on main branch

### 5. **Healthcheck**
- ✅ Verifies `/app/.audit/events.json` exists every 30s
- ✅ Restart policy: on-failure:3 (restart up to 3 times)
- ✅ Status visible in `docker compose ps`

### 6. **Log Rotation**
- ✅ app-dev: 50MB max-size, 5 files max (json-file driver)
- ✅ actor-audit: 100MB max-size, 3 files max
- ✅ Prevents disk space exhaustion

---

## Quick Commands

```bash
# Start application
make run

# Start monitoring
make monitoring-up

# Push to registry
make push

# Check health
make health

# View logs
make logs

# Stop all
make stop

# Full cleanup
make clean
```

---

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Grafana | http://localhost:3000 | Dashboards (admin/admin) |
| Prometheus | http://localhost:9090 | Metrics/Alerts |
| cAdvisor | http://localhost:8080 | Container stats |
| AlertManager | http://localhost:9093 | Alert routing |
| App | N/A | Runs telemetry service |

---

## GitHub Actions Setup

1. **Create secrets** in GitHub (Settings → Secrets):
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your access token

2. **Push to main**:
   ```bash
   git add .
   git commit -m "feat: add monitoring and CI/CD"
   git push origin main
   ```

3. **Watch workflow**:
   - Go to Actions tab
   - See build → test → security-scan → push

4. **Automatic push on success**:
   - Image tagged with branch, commit SHA, timestamp
   - Available at: `docker.io/your-username/actor-dev-env:latest`

---

## Monitoring Workflow

1. **Container runs** → generates telemetry events
2. **cAdvisor collects** metrics every 15s
3. **Prometheus scrapes** cAdvisor metrics
4. **Grafana displays** dashboard
5. **AlertManager triggers** rules if thresholds exceeded
6. **Webhook notified** (webhook, email, Slack, etc.)

---

## Security Features

- ✅ Non-root user (UID 65532)
- ✅ Dropped all Linux capabilities (cap_drop: ALL)
- ✅ Read-only filesystem for audit volume
- ✅ Resource limits (CPU, memory)
- ✅ No privileged mode
- ✅ Trivy vulnerability scanning in CI/CD
- ✅ Hadolint Dockerfile linting
- ✅ SARIF security report upload to GitHub

---

## Volume & Data Persistence

```
actor_dev_env_audit_data (/var/lib/docker/volumes/actor_dev_env_audit_data/_data)
  └── events.json (telemetry events)

prometheus_data (/var/lib/docker/volumes/actor_dev_env_prometheus_data/_data)
  └── time-series metrics (30-day retention)

grafana_data (/var/lib/docker/volumes/actor_dev_env_grafana_data/_data)
  └── dashboards, users, settings
```

---

## Deployment Scenarios

### Local Development
```bash
make run
make monitoring-up
```

### Remote Server (Pull from Registry)
```bash
docker login
docker compose pull
docker compose up -d
```

### Production (Docker Swarm)
```bash
docker stack deploy -c docker-compose.yml actor-dev-env
docker stack deploy -c docker-compose.monitoring.yml monitoring
```

### Kubernetes (convert with Kompose)
```bash
kompose convert -f docker-compose.yml
kubectl apply -f .
```

---

## Performance Metrics

| Component | CPU Limit | Memory Limit | Purpose |
|-----------|-----------|--------------|---------|
| app-dev | 1.0 | 512M | Telemetry generation |
| audit | 1.0 | 1G | Grype scanning |
| prometheus | 0.5 | 512M | Metrics storage |
| grafana | 0.5 | 256M | Dashboards |
| cadvisor | 0.5 | 256M | Container stats |
| alertmanager | 0.25 | 128M | Alert routing |

**Total**: ~3.75 CPUs, 2.664GB RAM at peak

---

## Files Created

```
H:\ACTOR_DEV_ENV\
├── .dockerignore                              # Build optimization
├── docker-compose.monitoring.yml             # Prometheus/Grafana/cAdvisor/AlertManager
├── prometheus.yml                             # Scrape config, alert rules
├── alerts.yml                                 # Alert definitions
├── alertmanager.yml                           # Alert routing & receivers
├── push-to-registry.sh                        # Registry push automation
├── Makefile                                   # Command shortcuts
├── DEPLOYMENT.md                              # Complete deployment guide
├── QUICK_START.md                             # Quick reference
├── .github/workflows/
│   └── build-and-deploy.yml                   # GitHub Actions CI/CD
└── grafana/provisioning/
    ├── datasources/prometheus.yml             # Auto-config Prometheus source
    └── dashboards/dashboards.yml              # Auto-load dashboards
```

---

## Next Steps

1. **Push to GitHub** (if using GitHub Actions):
   ```bash
   git add .
   git commit -m "Add monitoring, CI/CD, and registry push"
   git push
   ```

2. **Configure GitHub Secrets**:
   - DOCKER_USERNAME
   - DOCKER_PASSWORD

3. **Test locally**:
   ```bash
   make build
   make run
   make monitoring-up
   ```

4. **View dashboards**: http://localhost:3000

5. **Check alerts**: http://localhost:9093

6. **Push to registry**:
   ```bash
   export DOCKER_USERNAME=your-username
   export DOCKER_PASSWORD=your-token
   make push
   ```

---

## Troubleshooting

### High memory usage
- Check `docker stats`
- Reduce `memory:` limits in compose files
- Enable memory swappiness

### Alerts not firing
- Check `docker compose -f docker-compose.monitoring.yml logs prometheus`
- Verify AlertManager config: `curl http://localhost:9093/api/v1/alerts`
- Check Prometheus rules: `curl http://localhost:9090/api/v1/rules`

### Container keeps restarting
- Run `docker compose logs`
- Check healthcheck: `docker inspect actor_dev_env-actor-app-dev-1 --format='{{json .State.Health}}'`
- Verify volume permissions

### Registry push fails
- Check credentials: `docker login`
- Verify image name: `docker images | grep actor`
- Try manual push: `docker push your-username/actor-dev-env:latest`

---

## Support & Documentation

- **Docker Compose**: https://docs.docker.com/compose/
- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/grafana/
- **GitHub Actions**: https://docs.github.com/en/actions

