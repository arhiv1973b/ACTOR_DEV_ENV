# Security Architecture: Docker Socket Handling & Risk Tiering

## Overview
To eliminate the `CRITICAL` vulnerability of unmonitored host `docker.sock` exposure while supporting container management capabilities (such as MCP Docker tools), we implement a **tier-based risk management model**:

1. **Main `docker-compose.yml`** — **Zero-Burden / Secure by Default**: Completely free of host socket mounts and unprivileged escalations (`security_opt: [no-new-privileges:true]`, `cap_drop: [ALL]`).
2. **`docker-compose.with-docker.yml`** — **Explicit Risk Override**: Allows direct host `docker.sock` mounting when full control is required, marked with explicit security labels (`security.risk=docker.sock-host-control`, `security.accepted=true`).
3. **`docker-compose.proxy.yml`** — **Secure Socket Proxy (Recommended)**: Routes requests through `tecnativa/docker-socket-proxy` with strict API endpoint whitelisting (containers/images allowed, exec/volumes/networks restricted), preventing full host breakout.

## Usage Guide

- **Standard / Secure Mode (Default):**
  ```bash
  docker compose up -d
  ```

- **Direct Host Socket Mode (Explicit Accepted Risk):**
  ```bash
  docker compose -f docker-compose.yml -f docker-compose.with-docker.yml up -d
  ```

- **Secure Proxy Mode (Recommended for Production):**
  ```bash
  docker compose -f docker-compose.yml -f docker-compose.proxy.yml up -d
  ```

## Evidence Preservation
Original configurations are preserved as `*.legacy` files for L1 compliance audits.
