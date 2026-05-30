window.UniShield = (() => {
    const DEFAULT_API_CANDIDATES = ['http://192.168.191.1:5000', 'http://localhost:5000'];
    const SECRET_KEY = 'infosec-hmac-secret-2024';
    const LMS_API_KEY = 'unishield-lms-key-2026';
    const state = {
        apiBase: localStorage.getItem('API_BASE') || DEFAULT_API_CANDIDATES[0],
        apiHealth: null,
        authToken: localStorage.getItem('AUTH_TOKEN') || ''
    };

    function clone(value) {
        return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
    }

    function sortValue(value) {
        if (Array.isArray(value)) {
            return value.map(sortValue);
        }
        if (value && typeof value === 'object' && value.constructor === Object) {
            return Object.keys(value).sort().reduce((accumulator, key) => {
                accumulator[key] = sortValue(value[key]);
                return accumulator;
            }, {});
        }
        return value;
    }

    function canonicalJson(value) {
        return JSON.stringify(sortValue(value));
    }

    async function hmacHex(message) {
        const key = await crypto.subtle.importKey(
            'raw',
            new TextEncoder().encode(SECRET_KEY),
            { name: 'HMAC', hash: 'SHA-256' },
            false,
            ['sign']
        );
        const signatureBuffer = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(message));
        return Array.from(new Uint8Array(signatureBuffer))
            .map(byte => byte.toString(16).padStart(2, '0'))
            .join('');
    }

    async function signPayload(payload) {
        const payloadCopy = clone(payload) || {};
        payloadCopy.timestamp = Math.floor(Date.now() / 1000);
        payloadCopy.signature = await hmacHex(canonicalJson(payloadCopy));
        return payloadCopy;
    }

    async function verifySignedPayload(payload) {
        if (!payload || typeof payload !== 'object') {
            return { ok: false, reason: 'Invalid response payload' };
        }
        if (!('signature' in payload) || !('timestamp' in payload)) {
            return { ok: true, payload };
        }
        if (typeof payload.signature !== 'string') {
            return { ok: false, reason: 'Invalid signature format' };
        }
        const payloadToVerify = clone(payload);
        const receivedSignature = payloadToVerify.signature;
        delete payloadToVerify.signature;

        const expectedSignature = await hmacHex(canonicalJson(payloadToVerify));
        if (receivedSignature !== expectedSignature) {
            return { ok: false, reason: 'Signature mismatch – payload was tampered!' };
        }

        const timestamp = Number(payloadToVerify.timestamp);
        if (!Number.isFinite(timestamp) || Math.abs((Date.now() / 1000) - timestamp) > 30) {
            return { ok: false, reason: 'Request expired – possible replay attack' };
        }

        return { ok: true, payload: payloadToVerify };
    }

    async function probeApi(base) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 1200);
        try {
            const response = await fetch(`${base}/api/health`, { signal: controller.signal });
            if (!response.ok) {
                return null;
            }
            return await response.json();
        } catch (error) {
            return null;
        } finally {
            clearTimeout(timeout);
        }
    }

    async function resolveApiBase(forceRefresh = false) {
        if (!forceRefresh && state.apiHealth) {
            return state.apiHealth;
        }

        const savedBase = localStorage.getItem('API_BASE');
        const candidates = savedBase
            ? [savedBase, ...DEFAULT_API_CANDIDATES.filter(base => base !== savedBase)]
            : DEFAULT_API_CANDIDATES;

        const probes = [];
        for (const base of candidates) {
            const health = await probeApi(base);
            if (health) {
                probes.push({ base, health });
            }
        }

        if (!probes.length) {
            return null;
        }

        const secureLocalProbe = probes.find(item => (
            item.health
            && item.health.mode === 'SECURED'
            && item.base.includes('localhost')
        ));
        const secureProbe = probes.find(item => item.health && item.health.mode === 'SECURED');
        const unsecuredLocalProbe = probes.find(item => (
            item.health
            && item.health.mode === 'UNSECURED'
            && item.base.includes('localhost')
        ));
        const unsecuredProbe = probes.find(item => item.health && item.health.mode === 'UNSECURED');
        const chosen = secureLocalProbe || secureProbe || unsecuredLocalProbe || unsecuredProbe || probes[0];

        state.apiBase = chosen.base;
        state.apiHealth = chosen.health;
        localStorage.setItem('API_BASE', chosen.base);
        return chosen.health;
    }

    function getApiBase() {
        return state.apiBase;
    }

    function getApiHealth() {
        return state.apiHealth;
    }

    function isSecureMode() {
        return Boolean(state.apiHealth && state.apiHealth.mode === 'SECURED');
    }

    function buildHeaders(includeJson = false) {
        const headers = {};
        if (includeJson) {
            headers['Content-Type'] = 'application/json';
        }
        if (isSecureMode()) {
            headers['X-API-Key'] = LMS_API_KEY;
            if (state.authToken) {
                headers['X-Auth-Token'] = state.authToken;
                headers['Authorization'] = `Bearer ${state.authToken}`;
            }
        }
        return headers;
    }

    async function apiRequest(path, options = {}) {
        await resolveApiBase();
        const method = (options.method || 'GET').toUpperCase();
        const headers = { ...buildHeaders(options.body !== undefined && options.body !== null), ...(options.headers || {}) };
        let requestBody = options.body;

        if (requestBody !== undefined && requestBody !== null && typeof requestBody === 'object' && !(requestBody instanceof FormData)) {
            if (isSecureMode() && method !== 'GET') {
                requestBody = JSON.stringify(await signPayload(requestBody));
            } else {
                requestBody = JSON.stringify(requestBody);
            }
        }

        const response = await fetch(`${state.apiBase}${path}`, {
            method,
            headers,
            credentials: options.credentials || 'include',
            body: requestBody
        });

        const rawText = await response.text();
        let data = rawText;

        if (options.expectJson !== false) {
            try {
                data = rawText ? JSON.parse(rawText) : {};
            } catch (error) {
                data = { error: 'Invalid JSON response', raw: rawText };
            }

            if (isSecureMode() && path !== '/api/health' && data && typeof data === 'object') {
                if ('signature' in data && 'timestamp' in data) {
                    const verification = await verifySignedPayload(data);
                    if (verification.ok) {
                        data = verification.payload;
                    }
                }
            }
        }

        return {
            ok: response.ok,
            status: response.status,
            data,
            response
        };
    }

    function stripSecurityFields(payload) {
        if (!payload || typeof payload !== 'object') {
            return payload;
        }
        const clonePayload = { ...payload };
        delete clonePayload.signature;
        delete clonePayload.timestamp;
        return clonePayload;
    }

    function formatCurrency(value) {
        const numericValue = Number(value || 0);
        return new Intl.NumberFormat('en-PK', {
            style: 'currency',
            currency: 'PKR',
            maximumFractionDigits: 0
        }).format(numericValue);
    }

    function formatPercent(value) {
        const numericValue = Number(value || 0);
        return `${numericValue.toFixed(2)}%`;
    }

    function formatNumber(value) {
        return new Intl.NumberFormat('en-PK').format(Number(value || 0));
    }

    function escapeHtml(value) {
        return String(value ?? '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#39;');
    }

    function setAuthToken(token) {
        state.authToken = token || '';
        if (state.authToken) {
            localStorage.setItem('AUTH_TOKEN', state.authToken);
        } else {
            localStorage.removeItem('AUTH_TOKEN');
        }
    }

    function clearAuthToken() {
        setAuthToken('');
    }

    return {
        apiRequest,
        buildHeaders,
        canonicalJson,
        formatCurrency,
        formatNumber,
        formatPercent,
        getApiBase,
        getApiHealth,
        isSecureMode,
        resolveApiBase,
        setAuthToken,
        clearAuthToken,
        signPayload,
        escapeHtml,
        stripSecurityFields,
        verifySignedPayload
    };
})();

window.logout = window.logout || (async () => {
    try {
        await window.UniShield.apiRequest('/api/auth/logout', { method: 'POST' });
    } catch (error) {
        // Public pages may not have an active session.
    }
    window.UniShield.clearAuthToken();
    localStorage.setItem('PORTAL_MODE', 'unsecured');
    localStorage.removeItem('ACTIVE_USER_ROLE');
    window.location.href = 'login.html';
});
