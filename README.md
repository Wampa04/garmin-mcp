# Garmin Connect MCP Server

[![Build and publish image](https://github.com/Wampa04/garmin-mcp/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Wampa04/garmin-mcp/actions/workflows/docker-image.yml)

A self-hosted [MCP](https://modelcontextprotocol.io) server that exposes your
Garmin Connect data to Claude (Web & Mobile) as a Custom Connector.

It runs as a Docker container behind your existing Traefik (SSL + routing),
reachable at `https://garmin-mcp.deinedomain.de/mcp`.

**Access protection: GitHub OAuth.** Claude runs a standard OAuth 2.1 flow
(dynamic client registration + PKCE) against the server, which proxies to
GitHub for the actual login. You paste only the URL into Claude and sign in
with GitHub — there is no token or client secret to enter in Claude. A
middleware then restricts access to a **single GitHub user** (`ALLOWED_GITHUB_USER`),
so even though anyone could log in with GitHub, only you can reach the data.

**Garmin authentication** uses **token-resume**: you log in once locally (MFA
handled interactively) and mount the resulting session tokens into the
container — the server never logs in with your password, which avoids the
captcha/MFA blocks Garmin applies to datacenter IPs.

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

### 2. Create a GitHub OAuth App

GitHub → Settings → Developer settings → **OAuth Apps** → New OAuth App:

- **Homepage URL:** `https://<your-domain>`
- **Authorization callback URL:** `https://<your-domain>/auth/callback`

Generate a client secret and note the Client ID.

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` — from the OAuth App above.
- `ALLOWED_GITHUB_USER` — your GitHub username; only this account may connect.
- `GARMIN_MCP_DOMAIN` — the domain Traefik routes to this service.
- `MCP_JWT_SECRET` *(optional)* — `openssl rand -hex 32`; set it so tokens
  issued to Claude survive container restarts (otherwise a restart forces a
  re-login).

### 4. Deploy on the VPS

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

### 5. Add the connector in Claude

In Claude → Settings → Connectors → Add custom connector:

- **Name:** anything, e.g. `Garmin`
- **Remote MCP Server URL:** `https://<your-domain>/mcp`
- Leave the OAuth Client ID / Secret fields **empty** — the server supports
  dynamic client registration, so Claude registers itself automatically.

On clicking *Add / Connect*, a GitHub login + consent screen opens. After you
authorize, ask Claude something like *"How did I sleep last night?"* to
confirm it works. (Anyone who is not `ALLOWED_GITHUB_USER` is denied here.)

## Local development

OAuth needs the public HTTPS callback, so the full flow only works once
deployed. To smoke-test wiring locally you can still boot the server with
placeholder credentials:

```bash
# tokens/ must already exist (see step 1)
GITHUB_CLIENT_ID=x GITHUB_CLIENT_SECRET=y ALLOWED_GITHUB_USER=you \
GARMIN_MCP_DOMAIN=localhost:8000 MCP_BASE_URL=http://localhost:8000 \
GARMINTOKENS=./tokens python server.py
```

The server listens on `http://0.0.0.0:8000/mcp/`; unauthenticated requests get
a `401` with a `WWW-Authenticate` header pointing at the OAuth metadata
(`/.well-known/oauth-authorization-server`).

## Security notes

- Access requires a GitHub login **and** a match against `ALLOWED_GITHUB_USER`
  — the allowlist middleware (`auth.py`) fails closed, so anyone else is denied
  even after authenticating with GitHub. Keep `GITHUB_CLIENT_SECRET` and
  `MCP_JWT_SECRET` secret.
- The `tokens/` directory contains live Garmin session credentials. It is
  mounted read-only into the container and must never be committed or shared.
- The GitHub OAuth App's callback URL must exactly match
  `https://<your-domain>/auth/callback`, or the login will fail.
