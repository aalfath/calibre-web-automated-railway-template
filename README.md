[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new/template/calibre-web-automa-1?utm_medium=integration&utm_source=button&utm_campaign=calibre-web-automated)

# Calibre-Web Automated on Railway

A one-click Railway template for [Calibre-Web Automated](https://github.com/crocodilestick/Calibre-Web-Automated) (CWA): a self-hosted ebook library with a web reader, automatic import, format conversion, metadata and cover fetching, OPDS, Kobo and KOReader sync and send-to-Kindle.

| | |
|---|---|
| App | Calibre-Web Automated **v4.0.8** (bundles Calibre 9.1) |
| Image | `crocodilestick/calibre-web-automated:v4.0.8@sha256:5e00373854247750cc3e4479b492ae09293ff5e06ed10177f226634d97888679` |
| Services | one: **Calibre-Web Automated** (public, port 8083, health check `/health`) |
| Volume | `/config`: settings (`app.db`, `cwa.db`), the Calibre library and the ingest folder |
| Memory | about 160 MB idle, up to about 450 MB while converting a book; fits Railway's 0.5 GB Free plan for normal use. Give it 1 GB or more for big PDF or comic conversions |

## After you deploy

1. Open the service's public URL.
2. Sign in as **`admin`** with the password in the service's **Variables** tab (`ADMIN_PASSWORD`).
3. Open **Admin → Edit users → admin**, set your email, and change the password if you like. A restart never overwrites a password you changed in the app.
4. Add books: use **Upload** in the web UI, or put files in the ingest folder. CWA converts them (EPUB by default), fetches metadata and adds them to the library. Settings live under **Admin → CWA Settings**.

Calibre-Web allows 3 sign-in attempts per minute; wait a minute after a wrong password.

## Variables

| Variable | Default | Notes |
|---|---|---|
| `ADMIN_PASSWORD` | `Cw-${{secret(24)}}-7` | First password of the `admin` account, generated per deploy. Used only while the account still has upstream's default password (`admin123`). The `Cw-`/`-7` wrapper meets Calibre-Web's password rules (upper, lower, digit, special character) |
| `PORT` | `8083` | The port CWA listens on and the domain targets. Leave it as it is |

Optional, not in the template (add them in the Variables tab if you need them): `TZ` (time zone, default UTC), `HARDCOVER_TOKEN` (Hardcover as a metadata source), `TRUSTED_PROXY_COUNT`, `CWA_WATCH_MODE=poll`. Mail (send-to-Kindle), OAuth/OIDC and LDAP are set up in the app's admin pages.

## What the wrapper changes

Everything else is the upstream image as is.

- **One volume.** Railway gives a service one volume, mounted at `/config`. `railway-entrypoint.sh` keeps the library and the ingest folder at `/config/calibre-library` and `/config/cwa-book-ingest`, linked to the paths CWA expects (`/calibre-library`, `/cwa-book-ingest`). All data survives redeploys and restarts.
- **No default password.** An s6 startup step (`railway-setup`) runs after CWA's own setup and before the web app. It replaces the `admin123` password with `ADMIN_PASSWORD`. It also replaces the session-signing key that upstream ships inside its template `app.db`, the same on every install, with a random one. If the admin password would stay `admin123`, the container exits with an error instead of starting.
- **Restarts on failure.** `S6_BEHAVIOUR_IF_STAGE2_FAILS=2` makes a failed startup step stop the container with a non-zero exit code, so Railway's `ON_FAILURE` restart policy restarts it.
- **Faster first boot.** Calibre's command-line tools are installed at build time instead of at every container start.

## Updates

This template builds from this repository. When a new CWA release is out, we bump the pinned image (tag and digest) in the `Dockerfile` and add an entry to [`CHANGELOG.md`](CHANGELOG.md). Railway then shows an "update available" notice on your project, and you choose when to apply it. Read the changelog first: breaking changes are listed at the top of each entry. Your `/config` volume and its library are kept.

## Local test

```sh
docker build -t cwa-railway .
docker run -d -p 8083:8083 -e ADMIN_PASSWORD='Cw-ChangeMe123-7' -v cwa-config:/config cwa-railway
curl http://localhost:8083/health
```

Licence: the wrapper files are MIT. Calibre-Web Automated is GPL-3.0.
