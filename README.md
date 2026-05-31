# UniShield Academy

UniShield Academy is an Information Security lab project that demonstrates how API payloads can be intercepted and modified in transit, and how a middleware layer can stop that tampering.

The app has two modes:

- `app_unsecured.py` for the attack demo
- `app_secured.py` for the protected demo

The frontend lives in `Desktop/` and includes:

- `landing.html`
- `student_portal.html`
- `dashboard.html`
- `admin.html`
- `login.html`
- `signup.html`

## What you need

- Windows host with Python 3.10+
- Kali Linux VM with `mitmproxy`
- Chrome on Windows
- The `ZeroOmega` browser extension, or Windows proxy settings
- Both machines on the same network

## Project files

- `app_unsecured.py` - vulnerable Flask API for the attack demo
- `app_secured.py` - secured Flask API with auth, signing, and verification
- `database.py` - SQLite schema and seed data
- `middleware.py` - HMAC signing and verification helpers
- `config.py` - network, security, and route configuration
- `intercept_grade.py` - mitmproxy script for manual request/response tampering
- `Desktop/` - all browser pages, page CSS, page JS, and shared frontend helpers

## Dependencies

The Python dependencies are listed in `requirements.txt`:

- Flask
- flask-cors
- Werkzeug
- mitmproxy

## Quick setup

From the project root on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "from database import init_db; init_db()"
```

## Network values used in this repo

These are the values currently configured in `config.py`:

- Windows host IP: `10.5.154.161`
- Kali IP: `192.168.191.129`
- Flask API port: `5000`
- mitmproxy port: `8080`

If your VM or hotspot network differs, update `config.py` before running the demo.

## Start the frontend

The HTML pages are static, so run a simple web server from the `Desktop` folder:

```powershell
cd Desktop
python -m http.server 5500
```

Open the site in Chrome:

- `http://localhost:5500/landing.html`

For interception demos, it is often better to use the Windows Wi-Fi IP for API traffic instead of relying on `localhost`, because browsers may bypass the proxy for local addresses.

## Chrome and proxy setup

The attack demo needs Chrome traffic to go through Kali.

### Option 1 - ZeroOmega

1. Install the `ZeroOmega` extension in Chrome.
2. Create a profile named something like `KALI_Proxy`.
3. Add a proxy server:
   - Type: `HTTP`
   - Host: `192.168.191.129`
   - Port: `8080`
4. Save the profile.
5. Activate that profile.

### Option 2 - Windows proxy

1. Open Windows Settings.
2. Go to `Network & Internet > Proxy`.
3. Turn on `Use a proxy server`.
4. Set:
   - Address: `192.168.191.129`
   - Port: `8080`
5. Do not bypass local addresses if you want Chrome to proxy the lab traffic too.

## Install the mitmproxy certificate

Chrome must trust the mitmproxy certificate before HTTPS traffic can be decrypted.

### Easy way

1. Start `mitmproxy` or `mitmweb` on Kali.
2. In Chrome on Windows, visit:
   - `http://mitm.it`
3. Download the Windows certificate.
4. Install it into `Trusted Root Certification Authorities`.
5. Restart Chrome.

### Command-line alternative

If you already have the certificate file on Windows:

```powershell
certutil -addstore root mitmproxy-ca-cert.cer
```

## Phase 1 - Unsecured demo

Start the vulnerable API:

```powershell
python app_unsecured.py
```

What this mode shows:

- The API accepts plain payloads
- Kali can intercept and edit requests
- Kali can also edit responses
- The browser renders the tampered data

Open the portal:

- `http://localhost:5500/student_portal.html`
- `http://localhost:5500/dashboard.html`
- `http://localhost:5500/admin.html`

## Phase 1 demo flow

1. Open `student_portal.html`.
2. Keep the backend in `UNSECURED SYSTEM`.
3. Click fetch on a student.
4. In Kali, pause the `POST /api/student` flow.
5. Change `student_id` or the response JSON.
6. Resume the flow.
7. Show the altered result in the frontend.

You can repeat the same idea on:

- `GET /api/dashboard`
- `PUT /api/admin/users/<id>/role`
- `PUT /api/admin/policies/<id>/status`

## Phase 2 - Secured demo

Stop the unsecured server and start the secured one:

```powershell
python app_secured.py
```

What this mode adds:

- HMAC signing on outgoing browser payloads
- Server-side signature verification
- Response signing and verification
- Login and admin checks
- API-key and IP-based service controls

In secure mode:

- Tampering should fail
- Replay attempts should fail
- The frontend should reject modified signed payloads

## Secure demo flow

1. Start `app_secured.py`.
2. Sign in or sign up from `login.html` or `signup.html`.
3. Open `student_portal.html`.
4. Repeat the same Kali tampering attempt.
5. Show that the request or response is blocked.

## Useful browser state to clear

When switching between modes, clear stale frontend state in Chrome DevTools Console:

```javascript
localStorage.removeItem('API_BASE')
localStorage.removeItem('AUTH_TOKEN')
localStorage.removeItem('ACTIVE_USER_ROLE')
localStorage.removeItem('PORTAL_MODE')
location.reload()
```

## Admin account

The default admin email is:

- `security.admin@university.edu`

The admin role is assigned when you register with that email in secured mode.

## Database reset

If you want a fresh demo database:

1. Stop both Flask servers.
2. Delete `students.db`.
3. Run `python app_secured.py` or `python app_unsecured.py` again.
4. The app will recreate and reseed the database automatically.

## Troubleshooting

### `OPTIONS /api/auth/me` or `GET /api/auth/me` appears in unsecured mode

That usually means stale browser state is still pointing the portal at secure mode.

Fix:

- Clear `localStorage`
- Refresh the page
- Open the portal in `UNSECURED SYSTEM`
- Restart `app_unsecured.py`

### Student list does not load

Check these first:

- `python -m http.server 5500` is running from `Desktop/`
- Flask is running on the correct mode
- The browser is pointed at the right proxy or no proxy, depending on the demo
- `config.py` has the correct Windows and Kali IPs

### Kali only sees Google traffic

That usually means the portal request is not routed through the proxy.

Check:

- Chrome proxy profile is active
- mitmproxy is listening on `192.168.191.129:8080`
- You installed the mitmproxy CA in Chrome
- The portal is not silently falling back to a different API base

### Secure mode shows a signature mismatch

Check:

- `SECRET_KEY` matches in `config.py`
- `Desktop/app.js`
- `middleware.py`
- System clocks on Windows and Kali are in sync

## Quick command list

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "from database import init_db; init_db()"
python -m http.server 5500
python app_unsecured.py
python app_secured.py
```

```bash
mitmweb -s intercept_grade.py --listen-host 0.0.0.0 --listen-port 8080
```

## File ownership

- `Desktop/student_portal.css` and `Desktop/student_portal.js` control the student portal UI and behavior.
- `Desktop/landing.css` and `Desktop/landing.js` control the landing page.
- `Desktop/login.css` and `Desktop/login.js` control login.
- `Desktop/signup.css` and `Desktop/signup.js` control signup.
- `Desktop/dashboard.css` and `Desktop/dashboard.js` control the dashboard.
- `Desktop/admin.css` and `Desktop/admin.js` control the admin console.

## Notes for presentation

- Phase 1 demonstrates interception and tampering.
- Phase 2 demonstrates signed payload protection.
- The same user action should produce different outcomes depending on the backend mode.

