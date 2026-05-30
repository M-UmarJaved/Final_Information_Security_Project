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

## Phase 1 — Unsecured demo (MITM-friendly)

Start the vulnerable API:

```powershell
python app_unsecured.py
```

Open the UI:
- `http://localhost:5500/landing.html`
- `http://localhost:5500/student_portal.html`
- `http://localhost:5500/dashboard.html`
- `http://localhost:5500/admin.html`

Start the manual interception proxy in Kali (example):

```bash
mitmweb -s intercept_grade.py --listen-host 0.0.0.0 --listen-port 8080
```

When you click a fetch action in the portal the request will be visible in `mitmweb` where you can pause and edit the JSON payload/response.

## Phase 2 — Secured demo (HMAC integrity)

Start the secured API instead:

```powershell
python app_secured.py
```

In secured mode, the browser signs payloads and the server signs JSON responses. The UI verifies the signature before rendering, so tampering is detected and blocked.

## Notes
- `SECRET_KEY` in `config.py` and `Desktop/app.js` must match.
- `app_unsecured.py` is intentionally open for the attack demo.
- `app_secured.py` adds payload verification, response signing, rate limiting, and role-based controls.

## Detailed run & troubleshooting

- Prerequisites: Python 3.10+ (project used 3.11+), `mitmproxy` on Kali for interception, both machines on same LAN or VM host-only network.

- Recommended network addresses: update `WINDOWS_IP` and `KALI_IP` in `config.py` to match your environment.

- Serve the frontend from the `Desktop` folder (static files):

```powershell
cd Desktop
.\.\..\.venv\Scripts\python.exe -m http.server 5500
```

- Important: many browsers **bypass the proxy for `localhost`**. For mitmproxy to intercept requests, open the UI using the Windows LAN IP rather than `localhost` and set the app API base accordingly:

```js
// in browser console
localStorage.setItem('API_BASE','http://<WINDOWS_IP>:5000');
location.reload();
```

- Start `mitmweb` on Kali so it listens externally:

```bash
mitmweb -s intercept_grade.py --listen-host 0.0.0.0 --listen-port 8080
```

- Configure Windows browser proxy to point to `<KALI_IP>:8080` and **disable** any setting that bypasses local addresses. In Windows Proxy settings uncheck "Don’t use the proxy server for local (intranet) addresses".

- Quick connectivity checks (from Kali):

```bash
curl http://<WINDOWS_IP>:5000/api/health
```

- If you see `403` or `Signature mismatch` when using secured mode, check these:
	- `SECRET_KEY` mismatch between `config.py` and client JS (`Desktop/app.js` or inlined shims).
	- JSON canonicalization differences: use the compact sorted JSON format. The repo already uses canonicalization, but if you edited client/server code re-align them.
	- Clock skew: signatures include a short timestamp window (default ±30s); ensure guest VM clocks are in sync.

- Windows firewall: allow inbound TCP on port `5000` for demo (or enable rule for Python).

## Files of interest

- `app_unsecured.py` — vulnerable API used for Phase 1.
- `app_secured.py` — HMAC verification and signed responses (Phase 2).
- `middleware.py` — signing & verification helpers (canonical JSON + HMAC-SHA256).
- `Desktop/app.js` — browser helper that signs requests and verifies signed responses.
- `intercept_grade.py` — mitmproxy script used in the lab to modify `student_id` fields.

If you want, I can also add a small `run_demo.ps1` that starts the static server and either unsecured or secured API for the Windows host.
