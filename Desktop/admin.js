let currentHealth = null;

    async function logout() {
        if (currentHealth && currentHealth.mode === 'SECURED') {
            try {
                await UniShield.apiRequest('/api/auth/logout', { method: 'POST' });
            } catch (error) {
                // Ignore logout errors.
            }
            UniShield.clearAuthToken();
            localStorage.setItem('PORTAL_MODE', 'unsecured');
            localStorage.removeItem('ACTIVE_USER_ROLE');
            window.location.href = 'login.html';
            return;
        }
        UniShield.clearAuthToken();
        localStorage.setItem('PORTAL_MODE', 'unsecured');
        localStorage.removeItem('ACTIVE_USER_ROLE');
        window.location.href = 'landing.html';
    }

    async function requireAdminIfNeeded() {
        if (!currentHealth || currentHealth.mode === 'UNSECURED') {
            document.getElementById('role-chip').textContent = 'Role: guest (unsecured)';
            return true;
        }

        const me = await UniShield.apiRequest('/api/auth/me');
        if (!me.ok || me.data.role !== 'admin') {
            window.location.href = 'dashboard.html';
            return false;
        }

        document.getElementById('role-chip').textContent = `Role: ${me.data.role}`;
        return true;
    }

    function renderRouteList(routes) {
        const container = document.getElementById('route-list');
        container.innerHTML = '';
        routes.slice(0, 10).forEach(route => {
            const row = document.createElement('div');
            row.className = 'route-row compact';
            row.innerHTML = `
                <div>
                    <div class="row-title">${UniShield.escapeHtml(route.path)}</div>
                    <div class="row-subtitle">${UniShield.escapeHtml(route.purpose)}</div>
                </div>
                <span class="badge">${route.method}</span>
                <span class="badge">${route.visibility}</span>
            `;
            container.appendChild(row);
        });
    }

    async function loadUsers() {
        const result = await UniShield.apiRequest('/api/admin/users');
        const container = document.getElementById('user-list');
        container.innerHTML = '';

        if (!result.ok) {
            container.innerHTML = `<div class="warning">${UniShield.escapeHtml(result.data.error || 'Could not load users')}</div>`;
            return;
        }

        const users = result.data.users || [];
        document.getElementById('metric-users').textContent = UniShield.formatNumber(users.length);
        document.getElementById('metric-admins').textContent = UniShield.formatNumber(users.filter(user => user.role === 'admin').length);
        document.getElementById('hero-users').textContent = UniShield.formatNumber(users.length);
        document.getElementById('hero-admins').textContent = UniShield.formatNumber(users.filter(user => user.role === 'admin').length);

        users.forEach(user => {
            const row = document.createElement('div');
            row.className = 'table-row compact';
            row.innerHTML = `
                <div>
                    <div class="row-title">${UniShield.escapeHtml(user.full_name)}</div>
                    <div class="row-subtitle">${UniShield.escapeHtml(user.email)} · ${UniShield.escapeHtml(user.created_at || '')}</div>
                </div>
                <div class="select-wrap">
                    <select data-user="${user.id}">
                        ${['student', 'faculty', 'registrar', 'admin'].map(role => `<option value="${role}" ${user.role === role ? 'selected' : ''}>${role}</option>`).join('')}
                    </select>
                </div>
                <button class="button secondary" type="button" onclick="updateUserRole(${user.id})">Update</button>
            `;
            container.appendChild(row);
        });
    }

    async function updateUserRole(userId) {
        const select = document.querySelector(`select[data-user="${userId}"]`);
        const result = await UniShield.apiRequest(`/api/admin/users/${userId}/role`, {
            method: 'PUT',
            body: { role: select.value }
        });
        if (!result.ok) {
            alert(result.data.error || 'Role update failed.');
            return;
        }
        await loadUsers();
    }

    async function loadPolicies() {
        const result = await UniShield.apiRequest('/api/admin/policies');
        const container = document.getElementById('policy-list');
        container.innerHTML = '';

        if (!result.ok) {
            container.innerHTML = `<div class="warning">${UniShield.escapeHtml(result.data.error || 'Could not load policies')}</div>`;
            return;
        }

        const policies = result.data.policies || [];
        document.getElementById('metric-policies').textContent = UniShield.formatNumber(policies.length);
        document.getElementById('hero-policies').textContent = UniShield.formatNumber(policies.length);

        policies.forEach(policy => {
            const row = document.createElement('div');
            row.className = 'policy-row';
            row.innerHTML = `
                <div>
                    <div class="row-title">${UniShield.escapeHtml(policy.name)}</div>
                    <div class="row-subtitle">${UniShield.escapeHtml(policy.details)}</div>
                </div>
                <span class="status ${String(policy.status || '').toLowerCase()}">${UniShield.escapeHtml(policy.status)}</span>
                <button class="button secondary" type="button" onclick="togglePolicy(${policy.id}, '${policy.status}')">${policy.status === 'ENABLED' ? 'Disable' : 'Enable'}</button>
            `;
            container.appendChild(row);
        });
    }

    async function togglePolicy(policyId, status) {
        const result = await UniShield.apiRequest(`/api/admin/policies/${policyId}/status`, {
            method: 'PUT',
            body: { status: status === 'ENABLED' ? 'DISABLED' : 'ENABLED' }
        });
        if (!result.ok) {
            alert(result.data.error || 'Policy update failed.');
            return;
        }
        await loadPolicies();
    }

    async function loadRoutes() {
        const result = await UniShield.apiRequest('/api/routes');
        if (!result.ok) {
            document.getElementById('route-list').innerHTML = `<div class="warning">${UniShield.escapeHtml(result.data.error || 'Could not load routes')}</div>`;
            return;
        }
        const routes = result.data.routes || [];
        document.getElementById('metric-routes').textContent = UniShield.formatNumber(routes.length);
        renderRouteList(routes);
    }

    async function loadAdminConsole() {
        currentHealth = await UniShield.resolveApiBase(true, 'secured');
        if (!currentHealth) {
            document.getElementById('admin-story').innerHTML = '<div class="warning">API not reachable. Start the Flask backend.</div>';
            return;
        }
        document.getElementById('mode-chip').textContent = `Mode: ${currentHealth.mode}`;

        const canContinue = await requireAdminIfNeeded();
        if (!canContinue) {
            return;
        }

        await loadUsers();
        await loadPolicies();
        await loadRoutes();
    }

    window.addEventListener('DOMContentLoaded', loadAdminConsole);
