# Garmin Connect MCP Server

[![Build and publish image](https://github.com/Wampa04/garmin-mcp/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Wampa04/garmin-mcp/actions/workflows/docker-image.yml)

A self-hosted [MCP](https://modelcontextprotocol.io) server that exposes your
Garmin Connect data to Claude (Web & Mobile) as a Custom Connector.

It runs as a Docker container behind your existing Traefik (SSL + routing),
reachable at `https://garmin-mcp.deinedomain.de/mcp`, and is protected by a
shared bearer token. Garmin authentication uses **token-resume**: you log in
once locally (MFA handled interactively) and mount the resulting session
tokens into the container — the server never logs in with your password, which
avoids the captcha/MFA blocks Garmin applies to datacenter IPs.

Built with [`fastmcp`](https://github.com/jlowin/fastmcp) and
[`garminconnect`](https://github.com/cyberjunky/python-garminconnect).
Requires Python 3.14.

## Tools (17)

| Area | Tools |
|------|-------|
| Activities | `list_activities`, `get_activity_details`, `list_activities_by_date` |
| Sleep / recovery | `get_sleep`, `get_body_battery`, `get_hrv` |
| Training | `get_training_status`, `get_training_readiness`, `get_training_load`, `get_vo2max` |
| Heart rate / stress | `get_heart_rate`, `get_resting_heart_rate`, `get_stress` |
| Daily / records | `get_daily_summary`, `get_steps`, `get_floors`, `get_personal_records` |

Date arguments use the format `YYYY-MM-DD` and default to today when omitted.

## Setup

### 1. Generate Garmin tokens (locally, once)

On your own machine (where you can complete MFA):

```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows
# python3 -m venv .venv && source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python scripts/generate_tokens.py
```

This logs in to Garmin and writes session tokens to `./tokens/`. The tokens
auto-refresh, so this step is normally only needed once (re-run it if the
server later reports the tokens are invalid).

> `tokens/` and `.env` are git-ignored — never commit them.

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

- `MCP_BEARER_TOKEN` — the shared secret Claude must send. Generate one with
  `openssl rand -hex 32`.
- `GARMIN_MCP_DOMAIN` — the domain Traefik routes to this service.

### 3. Deploy on the VPS

Copy the project (including your `tokens/` directory and `.env`) to the server,
then:

```bash
docker compose up -d --build
```

Adjust `docker-compose.yml` to match your Traefik install:

- the external `networks:` name (often `proxy`, `web`, or `traefik`),
- the `entrypoints` and `certresolver` label values.

> **Prefer a prebuilt image?** A GitHub Actions workflow
> (`.github/workflows/docker-image.yml`) builds and publishes the image to
> GHCR on every push to `main` and on `v*` tags. To deploy without building on
> the VPS, replace `build: .` in `docker-compose.yml` with
> `image: ghcr.io/wampa04/garmin-mcp:latest` and run `docker compose up -d`.
> (Make the package public, or `docker login ghcr.io` first if it stays private.)

### 4. Add the connector in Claude

In Claude → Settings → Connectors → Add custom connector:

- **URL:** `https://<your-domain>/mcp`
- **Authentication:** Bearer token → the value of `MCP_BEARER_TOKEN`

Then ask Claude something like *"How did I sleep last night?"* to confirm it
works.

## Local development

```bash
# tokens/ must already exist (see step 1)
MCP_BEARER_TOKEN=test GARMINTOKENS=./tokens python server.py
```

The server listens on `http://0.0.0.0:8000/mcp/`. Requests without a valid
`Authorization: Bearer <MCP_BEARER_TOKEN>` header are rejected with 401.

## Security notes

- The bearer token is the only thing standing between the internet and your
  Garmin data — use a long random value and keep it secret.
- The `tokens/` directory contains live Garmin session credentials. It is
  mounted read-only into the container and must never be committed or shared.
