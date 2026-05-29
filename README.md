# UniShield Academy — InfoSec Lab

This project demonstrates a school management system protected by an API payload integrity middleware.

## What it shows
- A polished school management UI: landing, student portal, dashboard, admin console, login, and signup.
- A realistic backend with students, courses, faculty, attendance, fees, announcements, routes, logs, and policies.
- A Kali MITM demo that can pause requests and responses so you can inspect or edit JSON by hand.
- A secured mode where requests and responses are signed and tampering is detected.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "from database import init_db; init_db()"
```

## Phase 1 — Unsecured demo

Start the vulnerable API:

```powershell
python app_unsecured.py
```

Open the UI:
- `http://localhost:5500/landing.html`
- `http://localhost:5500/student_portal.html`
- `http://localhost:5500/dashboard.html`
- `http://localhost:5500/admin.html`

Use ZeroOmega in Chrome with:
- host: `192.168.191.129`
- port: `8080`

Then start the manual interception proxy in Kali:

```bash
mitmweb -s intercept_grade.py --listen-host 0.0.0.0 --listen-port 8080
```

Now when you click a fetch action in the portal:
- the request pauses in Kali,
- you edit the JSON in `mitmweb`,
- press `a` to resume,
- then the response can also be paused and edited the same way.

## Phase 2 — Secured demo

Start the secured API instead:

```powershell
python app_secured.py
```

In secured mode, the browser signs payloads and the server signs JSON responses. The UI verifies the signature before rendering, so the same MITM edit flow gets blocked.

## Notes
- `SECRET_KEY` in `config.py` and `Desktop/app.js` must match.
- `app_unsecured.py` is intentionally open for the attack demo.
- `app_secured.py` adds payload verification, response signing, rate limiting, and role-based controls.
