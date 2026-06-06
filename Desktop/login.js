async function login() {
        const notice = document.getElementById('notice');
        const error = document.getElementById('error');
        notice.classList.add('hidden');
        error.classList.add('hidden');
        error.textContent = '';

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const button = document.getElementById('loginBtn');

        const health = await UniShield.resolveApiBase(true);
        if (!health) {
            notice.textContent = 'API not reachable. Start the secured Flask server first.';
            notice.classList.remove('hidden');
            return;
        }
        if (health.mode === 'UNSECURED') {
            notice.textContent = 'Login is only available in secured mode. Start app_secured.py to continue.';
            notice.classList.remove('hidden');
            button.disabled = true;
            return;
        }

        if (!email || !password) {
            error.textContent = 'Please enter both email and password.';
            error.classList.remove('hidden');
            return;
        }

        try {
            button.disabled = true;
            button.textContent = 'Signing in...';
            const result = await UniShield.apiRequest('/api/auth/login', {
                method: 'POST',
                body: { email, password }
            });

            if (!result.ok) {
                throw new Error(result.data.error || `HTTP ${result.status}`);
            }

            UniShield.setAuthToken(result.data.auth_token || '');
            localStorage.setItem('PORTAL_MODE', 'secured');
            localStorage.setItem('ACTIVE_USER_ROLE', result.data.role || '');
            window.location.href = 'dashboard.html';
        } catch (err) {
            error.textContent = err.message || 'Login failed.';
            error.classList.remove('hidden');
        } finally {
            button.disabled = false;
            button.textContent = 'Sign In';
        }
    }

    window.addEventListener('DOMContentLoaded', async () => {
        const health = await UniShield.resolveApiBase(true);
        const notice = document.getElementById('notice');
        if (!health) {
            notice.textContent = 'API not reachable yet. Please start the secured server.';
            notice.classList.remove('hidden');
            return;
        }
        if (health.mode === 'UNSECURED') {
            notice.textContent = 'This page is disabled in unsecured mode because login is part of the secured management workflow.';
            notice.classList.remove('hidden');
            document.getElementById('loginBtn').disabled = true;
        }
    });
