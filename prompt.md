If your friend pulls this repo onto his laptop, these are the only things he should usually change:

config.py: update WINDOWS_IP and KALI_IP to match his own network, and update LMS_ALLOWED_IPS to include the IPs he will use.
Desktop/app.js: update the default API candidate IP if his backend is on a different machine/network.
Desktop/student_portal.js: update API_BASE_UNSECURED if he is not using the same Windows host IP.
If he changes security values, keep these matched on both sides:
SECRET_KEY in config.py
SECRET_KEY in app.js
LMS_API_KEY in config.py
LMS_API_KEY in app.js
If he wants a different admin account, update ADMIN_EMAILS in config.py.
What he usually does not need to change:

The HTML/CSS files if he keeps the same folder structure.
The SQLite database; it is created automatically.
The secured API 127.0.0.1 setting if he is running everything on one laptop.
The cache-busting versions, unless he edits the JS/CSS and wants to force reload in the browser.
If he wants the Kali MITM demo on his own network, he must also:

Set his Windows host IP and Kali IP correctly in config.py.
Run the proxy on Kali with:

mitmweb -s intercept_grade.py --listen-host 0.0.0.0 --listen-port 8080


Open the frontend using the Windows LAN IP, not localhost.
Set the browser proxy to his Kali IP and port 8080.
Small Copilot prompt he can use:

Update this project so it runs on my laptop network. Replace all hardcoded lab IPs in config.py, Desktop/app.js, and Desktop/student_portal.js with my own Windows and Kali IPs. Keep SECRET_KEY and LMS_API_KEY consistent between backend and frontend. Make sure unsecured mode uses the correct backend base URL and that the browser does not rely on stale cached values. Also update any README or guide examples that still mention old IPs.

If you want, I can also give you a shorter “clone-and-run” handoff checklist for your friend.

GPT-5.4 mini • 0.3x