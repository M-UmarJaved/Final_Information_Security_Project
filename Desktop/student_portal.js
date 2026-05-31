// ── CONFIG: mode-aware API targets ──
    const API_BASE_SECURED = 'http://127.0.0.1:5000';
    const API_BASE_UNSECURED = 'http://192.168.191.1:5000';
    const SECRET_KEY = 'infosec-hmac-secret-2024';   // Must match config.py
    let securedMode = false;

    function getApiBaseForMode(secured) {
        return secured ? API_BASE_SECURED : API_BASE_UNSECURED;
    }

    function getAuthHeadersForMode(secured) {
        const headers = { 'Content-Type': 'application/json' };
        const authToken = localStorage.getItem('AUTH_TOKEN');
        if (secured && authToken) {
            headers['X-Auth-Token'] = authToken;
            headers['Authorization'] = `Bearer ${authToken}`;
        }
        return headers;
    }

    async function probeHealth(base) {
        try {
            const response = await fetch(`${base}/api/health`, {
                method: 'GET',
                credentials: 'include',
                cache: 'no-store'
            });
            if (!response.ok) {
                return null;
            }
            return await response.json();
        } catch (error) {
            return null;
        }
    }

    async function detectBackendMode() {
        const storedMode = localStorage.getItem('PORTAL_MODE');
        const unsecuredHealth = await probeHealth(API_BASE_UNSECURED);
        const securedHealth = await probeHealth(API_BASE_SECURED);

        if (storedMode === 'secured' && securedHealth && securedHealth.mode === 'SECURED') {
            return { secured: true, health: securedHealth };
        }

        if (unsecuredHealth && unsecuredHealth.mode === 'UNSECURED') {
            return { secured: false, health: unsecuredHealth };
        }

        if (securedHealth && securedHealth.mode === 'SECURED') {
            return { secured: true, health: securedHealth };
        }

        if (storedMode === 'secured' && securedHealth) {
            return { secured: true, health: securedHealth };
        }

        return unsecuredHealth
            ? { secured: false, health: unsecuredHealth }
            : securedHealth
                ? { secured: true, health: securedHealth }
                : null;
    }

    async function logout() {
        if (!securedMode) {
            localStorage.removeItem('AUTH_TOKEN');
            localStorage.setItem('PORTAL_MODE', 'unsecured');
            window.location.href = 'login.html';
            return;
        }
        try {
            await fetch(`${getApiBaseForMode(securedMode)}/api/auth/logout`, {
                method: 'POST',
                headers: getAuthHeadersForMode(securedMode),
                credentials: 'include'
            });
        } catch (error) {
            // Ignore logout transport failures; clear local state anyway.
        }
        localStorage.removeItem('AUTH_TOKEN');
        localStorage.setItem('PORTAL_MODE', 'unsecured');
        window.location.href = 'login.html';
    }

    async function requireAuth() {
        try {
            const response = await fetch(`${getApiBaseForMode(securedMode)}/api/auth/me`, {
                method: 'GET',
                headers: getAuthHeadersForMode(securedMode),
                credentials: 'include'
            });
            const me = await response.json().catch(() => ({}));
            if (response.ok) {
                document.getElementById('role-badge').textContent = `Role: ${me.role || '--'}`;
                return true;
            }
        } catch (error) {
            // Fall through to redirect.
        }
        window.location.href = 'login.html';
        return false;
    }

    function log(msg) {
        const el = document.getElementById('log');
        const time = new Date().toLocaleTimeString('en-US', { hour12: false });
        el.textContent += '\n[' + time + '] ' + msg;
        el.scrollTop = el.scrollHeight;
    }

    function setMode(secured) {
        securedMode = secured;
        localStorage.setItem('PORTAL_MODE', secured ? 'secured' : 'unsecured');
        
        const label = document.getElementById('mode-label');
        const indicator = document.getElementById('mode-status-indicator');
        
        if (secured) {
            label.textContent = 'SECURED SYSTEM';
            indicator.className = 'mode-status secured-mode';
            log('--> [SYSTEM] Switched to SECURED API – HMAC payload signing active.');
        } else {
            label.textContent = 'UNSECURED SYSTEM';
            indicator.className = 'mode-status unsecured-mode';
            log('--> [SYSTEM] Switched to UNSECURED API – No payload protection.');
        }
    }

    // HMAC-SHA256 signing using Web Crypto API
    async function signPayload(payload) {
        const withTimestamp = { ...payload, timestamp: Math.floor(Date.now() / 1000) };
        const sorted = JSON.stringify(withTimestamp, Object.keys(withTimestamp).sort());
        const key = await crypto.subtle.importKey(
            'raw',
            new TextEncoder().encode(SECRET_KEY),
            { name: 'HMAC', hash: 'SHA-256' },
            false,
            ['sign']
        );
        const signatureBuffer = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(sorted));
        const hex = Array.from(new Uint8Array(signatureBuffer))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
        return { ...withTimestamp, signature: hex };
    }

    async function fetchGrade() {
        const studentId = document.getElementById('studentSelect').value;
        const resultEl = document.getElementById('result');
        const emptyEl = document.getElementById('resultEmpty');
        resultEl.style.display = 'none';
        emptyEl.style.display = 'block';
        
        if (!studentId) {
            log('[ERROR] Please select a target account ID.');
            return;
        }
        
        log(`\n--- INITIATING REQUEST FOR ID: ${studentId} ---`);
        log(`[INFO] Transport mode: ${securedMode ? 'SECURED (Cryptographic Signature)' : 'UNSECURED (Raw Payload)'}`);

        let payload = { student_id: studentId };
        if (securedMode) {
            payload = await signPayload(payload);
            log('[CRYPTO] Payload signed using HMAC-SHA256');
            log('[CRYPTO] Signature generated: ' + payload.signature.substring(0,24) + '...');
        }
        
        log(`[NETWORK] Sending POST ${getApiBaseForMode(securedMode)}/api/student`);

        try {
            const response = await fetch(`${getApiBaseForMode(securedMode)}/api/student`, {
                method: 'POST',
                headers: getAuthHeadersForMode(securedMode),
                credentials: 'include',
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            log(`[RESPONSE] Status: HTTP ${response.status}`);
            log('[RESPONSE] Body: ' + JSON.stringify(data));

            if (response.status === 403) {
                resultEl.className = 'result blocked';
                resultEl.style.display = 'block';
                emptyEl.style.display = 'none';
                resultEl.innerHTML = `
                    <div class="result-header">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
                        ATTACK BLOCKED
                    </div>
                    <div class="result-body">
                        <div class="field"><span class="label">Detection</span><span class="val" style="color:var(--danger)">Signature Mismatch</span></div>
                        <div class="field"><span class="label">Reason</span><span class="val" style="color:var(--danger)">${data.reason}</span></div>
                        <div class="field"><span class="label">Status Code</span><span class="val" style="color:var(--danger)">403 FORBIDDEN</span></div>
                    </div>
                `;
            } else if (response.ok) {
                const gradeClass = data.grade.startsWith('A') ? 'grade-A' : data.grade === 'F' ? 'grade-F' : 'grade-B';
                const isAttack = (data.student_id !== studentId);
                
                const warningHTML = isAttack 
                    ? `<div class="warning-banner">
                         <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
                         BOLA Attack Successful! Retrived ID: ${data.student_id} instead of yours.
                       </div>` 
                    : '';

                resultEl.className = 'result success';
                resultEl.style.display = 'block';
                emptyEl.style.display = 'none';
                resultEl.innerHTML = `
                    <div class="result-header">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                        Student Record Details
                    </div>
                    <div class="result-body">
                        ${warningHTML}
                        <div class="field"><span class="label">Student ID</span><span class="val">${data.student_id}</span></div>
                        <div class="field"><span class="label">Name</span><span class="val">${data.name}</span></div>
                        <div class="field"><span class="label">Course</span><span class="val">${data.course}</span></div>
                        <div class="field"><span class="label">Current Grade</span><span class="val ${gradeClass}">${data.grade}</span></div>
                        <div class="field"><span class="label">Marks</span><span class="val">${data.marks}/100</span></div>
                        <div class="field"><span class="label">GPA</span><span class="val">${data.gpa}/4.0</span></div>
                        ${data.security ? `<div class="field"><span class="label">Security Info</span><span class="val" style="color:var(--success)">${data.security}</span></div>` : ''}
                    </div>
                `;
            }
        } catch(err) {
            log('[CRITICAL] Network Error: ' + err.message);
            log('[DEBUG] Verify if the target API servers are running.');
            emptyEl.style.display = 'block';
        }
    }

    async function loadStudents() {
        const select = document.getElementById('studentSelect');
        log('[INIT] Fetching available target IDs from database...');
        try {
            const response = await fetch(`${getApiBaseForMode(securedMode)}/api/students`, {
                headers: getAuthHeadersForMode(securedMode),
                credentials: 'include'
            });
            const data = await response.json();
            
            if (!response.ok || !data.students) {
                throw new Error('Invalid response structure received.');
            }

            select.innerHTML = '';
            data.students.forEach((student, index) => {
                const option = document.createElement('option');
                option.value = student.id;
                const suffix = index === 0 ? ' (Your Authentication ID)' : ' (External Target)';
                option.textContent = `${student.id} — ${student.name} ${suffix}`;
                select.appendChild(option);
            });
            log(`[INIT] Successfully loaded ${data.students.length} target records.`);
        } catch (err) {
            select.innerHTML = '<option value="" disabled selected>System failed to load directory</option>';
            log('[ERROR] Failed to load directory: ' + err.message);
        }
    }

    window.addEventListener('DOMContentLoaded', async () => {
        const detected = await detectBackendMode();
        if (detected) {
            setMode(detected.secured);
            if (detected.secured) {
                const ok = await requireAuth();
                if (!ok) return;
            } else {
                document.getElementById('role-badge').textContent = 'Role: Guest (Unverified)';
            }
        } else {
            setMode(false);
            document.getElementById('role-badge').textContent = 'Role: Guest (Unverified)';
        }
        loadStudents();
    });
