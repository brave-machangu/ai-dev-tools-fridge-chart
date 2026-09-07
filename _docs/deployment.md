# Running this for real

The MVP is set up for a laptop. To run it for an actual household, set these
and schedule the reminders.

## Environment

| Variable | What it does |
| --- | --- |
| `DJANGO_SECRET_KEY` | Signing key. Generate a fresh one; the fallback in `settings.py` is public. |
| `DJANGO_DEBUG` | `false` in production. Turns on HTTPS redirects, secure cookies and HSTS. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames, e.g. `chores.example.com`. |
| `POSTGRES_DB` | Set to switch from SQLite to PostgreSQL. See below. |
| `POSTGRES_USER` `POSTGRES_PASSWORD` `POSTGRES_HOST` `POSTGRES_PORT` | Connection details; host defaults to `localhost`, port to `5432`. |
| `EMAIL_HOST` | Set to send reminders over SMTP instead of printing them. |
| `EMAIL_PORT` `EMAIL_HOST_USER` `EMAIL_HOST_PASSWORD` `EMAIL_USE_TLS` | SMTP details; port defaults to `587`, TLS on. |
| `DEFAULT_FROM_EMAIL` | The address reminders come from. |

Generate a key with:

```
uv run python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

Check the result before serving anything:

```
uv run python manage.py check --deploy
```

## PostgreSQL

Install the driver and point the app at a database:

```
uv sync --extra postgres
POSTGRES_DB=chores POSTGRES_USER=chores POSTGRES_PASSWORD=... uv run python manage.py migrate
```

Without `POSTGRES_DB` the app uses SQLite, which is fine for development.

## Scheduling the reminders

`send_reminders` decides for itself whether anything is due, and prints nothing
on the five quiet days, so run it once a day and leave it alone.

Linux or macOS, via `crontab -e`:

```
0 17 * * * cd /srv/chores && /usr/local/bin/uv run python manage.py send_reminders
```

Windows, as a daily scheduled task:

```
schtasks /create /tn "Chore reminders" /sc daily /st 17:00 ^
  /tr "cmd /c cd /d C:\path\to\chores && uv run python manage.py send_reminders"
```

Check it works before trusting it, by forcing a day:

```
uv run python manage.py send_reminders --date 2026-09-11   # a Friday
uv run python manage.py send_reminders --date 2026-09-13   # a Sunday
```
