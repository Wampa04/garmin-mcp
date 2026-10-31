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

**Garmin access** uses the official
[Garmin Connect Personal API](https://developer.garmin.com/gc-developer-program/personal/personal-api/):
you create a Personal API key in Garmin Connect Web and put it in `.env`. The
server exchanges it for a 24-hour access token and renews that automatically —
no password, no MFA, no session tokens to copy around.

Built with [`fastmcp`](https://github.com/jlowin/fastmcp) and
[`httpx`](https://www.python-httpx.org/).
Requires Python 3.14.

## Tools (29)

| Area | Tools |
|------|-------|
| Activities | `list_activities`, `search_activities`, `get_activity_details`, `get_activity_workouts`, `download_activity_file`, `get_wellness_activity_summaries` |
| Sleep / recovery | `get_sleep`, `get_sleep_summaries`, `get_body_battery`, `get_hrv`, `get_hrv_summaries`, `get_spo2` |
| Heart rate / stress | `get_heart_rate`, `get_resting_heart_rate`, `get_heart_rate_zones`, `get_stress` |
| Daily | `get_daily_summary`, `get_daily_summaries`, `get_steps`, `get_floors`, `get_hydration` |
| Body / profile | `get_fitness_age`, `get_weight`, `get_weight_entries`, `get_weight_goals`, `get_nutrition_log`, `get_menstrual_cycle_summary`, `get_menstrual_cycle_day`, `get_user_settings` |

Date arguments use the format `YYYY-MM-DD` and default to today when omitted
("today" in `TZ`, default `Europe/Berlin`; override it in `.env`).
Range tools are limited by Garmin (steps/stress 28 days, sleep/Body
Battery/hydration 31 days, daily summaries 1 year).

**Not available in the Personal API:** training status, training readiness,
training load (acute/chronic), daily VO2max and personal records. Per-activity
VO2max, training effect and training load are included in the results of
`list_activities` and `search_activities`.

## Setup

### 1. Create a Garmin Personal API key

In [Garmin Connect Web](https://connect.garmin.com/app/settings/personalApiToken)
→ Settings → **Personal API Key** → *Create Key*, accept the terms and choose
an expiration (30 days to 1 year). The key is shown **only once** — copy it
into `.env` as `GARMIN_API_KEY` (step 3).

Garmin emails you about a week before the key expires; then create a new key,
update `.env` and restart the container.

> `.env` is git-ignored — never commit it.

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
- `GARMIN_API_KEY` — the Personal API key from step 1.
- `MCP_JWT_SECRET` *(optional)* — `openssl rand -hex 32`; set it so tokens
  issued to Claude survive container restarts (otherwise a restart forces a
  re-login).

### 4. Deploy on the VPS

Copy the project (including your `.env`) to the server,
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
GITHUB_CLIENT_ID=x GITHUB_CLIENT_SECRET=y ALLOWED_GITHUB_USER=you \
GARMIN_MCP_DOMAIN=localhost:8000 MCP_BASE_URL=http://localhost:8000 \
GARMIN_API_KEY=<your-key> python server.py
```

The server listens on `http://0.0.0.0:8000/mcp/`; unauthenticated requests get
a `401` with a `WWW-Authenticate` header pointing at the OAuth metadata
(`/.well-known/oauth-authorization-server`).

## Security notes

- Access requires a GitHub login **and** a match against `ALLOWED_GITHUB_USER`
  — the allowlist middleware (`auth.py`) fails closed, so anyone else is denied
  even after authenticating with GitHub. Keep `GITHUB_CLIENT_SECRET` and
  `MCP_JWT_SECRET` secret.
- Client redirect URIs are restricted (default: Claude's hosts) so a stranger
  cannot register a dynamic client pointing at an attacker-controlled callback.
  Override via `ALLOWED_CLIENT_REDIRECT_URIS` only if you use a non-Claude client.
- `GARMIN_API_KEY` grants read access to all your Garmin data until it
  expires. Keep it secret; if it leaks, delete it in Garmin Connect Web, which
  also invalidates every access token issued from it.
- The GitHub OAuth App's callback URL must exactly match
  `https://<your-domain>/auth/callback`, or the login will fail.

### Known security debt

- **Allowlist matches the mutable GitHub username** (`ALLOWED_GITHUB_USER`),
  not the immutable numeric account id. If you ever rename your GitHub account,
  someone could claim the freed username and pass the allowlist. Hardening:
  match on `claims["sub"]` in `auth.py`. Accepted for now (single-user setup,
  low likelihood). Tracked in the `KNOWN DEBT` comment in `auth.py`.
