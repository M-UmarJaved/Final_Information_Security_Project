let currentHealth = null;

    async function logout() {
        if (currentHealth && currentHealth.mode === 'SECURED') {
            try {
                await UniShield.apiRequest('/api/auth/logout', { method: 'POST' });
            } catch (error) {
                // Ignore logout issues.
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

    async function requireSessionIfNeeded() {
        if (!currentHealth || currentHealth.mode === 'UNSECURED') {
            document.getElementById('role-chip').textContent = 'Role: guest (unsecured)';
            return true;
        }

        const me = await UniShield.apiRequest('/api/auth/me');
        if (!me.ok) {
            window.location.href = 'login.html';
            return false;
        }

        document.getElementById('role-chip').textContent = `Role: ${me.data.role || 'user'}`;
        return true;
    }

    function renderBarList(containerId, items, labelKey, valueKey, formatter = value => value, badgeLabel = '') {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        if (!items || items.length === 0) {
            container.innerHTML = '<div class="mini-note">No data available.</div>';
            return;
        }

        const maxValue = Math.max(...items.map(item => Number(item[valueKey] || 0)), 1);
        items.forEach(item => {
            const row = document.createElement('div');
            row.className = 'timeline-item';
            const value = Number(item[valueKey] || 0);
            const percent = Math.min((value / maxValue) * 100, 100);
            row.innerHTML = `
                <strong>${UniShield.escapeHtml(item[labelKey] || 'Item')}</strong>
                <span class="muted">${UniShield.escapeHtml(formatter(value))} ${badgeLabel}</span>
                <div class="progress"><span style="width:${percent}%"></span></div>
            `;
            container.appendChild(row);
        });
    }

    function renderLogs(items) {
        const container = document.getElementById('log-list');
        container.innerHTML = '';
        if (!items || items.length === 0) {
            container.innerHTML = '<div class="mini-note">No API requests logged yet.</div>';
            return;
        }

        items.forEach(item => {
            const row = document.createElement('div');
            row.className = 'log-row stack';
            row.innerHTML = `
                <div class="row-title">${UniShield.escapeHtml(item.endpoint)} · ${UniShield.escapeHtml(item.method)}</div>
                <div class="row-subtitle">Status ${UniShield.escapeHtml(item.status)} · Student ${UniShield.escapeHtml(item.student_id || '--')} · ${UniShield.escapeHtml(item.client_ip || '--')}</div>
                <div class="row-subtitle">${UniShield.escapeHtml(item.created_at || '')}</div>
            `;
            container.appendChild(row);
        });
    }

    function renderPolicies(items) {
        const container = document.getElementById('policy-list');
        container.innerHTML = '';
        if (!items || items.length === 0) {
            container.innerHTML = '<div class="mini-note">No policies available.</div>';
            return;
        }

        items.forEach(item => {
            const row = document.createElement('div');
            row.className = 'policy-row';
            const statusClass = String(item.status || '').toLowerCase();
            row.innerHTML = `
                <div>
                    <div class="row-title">${UniShield.escapeHtml(item.name)}</div>
                    <div class="row-subtitle">${UniShield.escapeHtml(item.details)}</div>
                </div>
                <span class="status ${statusClass}">${UniShield.escapeHtml(item.status)}</span>
            `;
            container.appendChild(row);
        });
    }

    function renderAnnouncements(items) {
        const container = document.getElementById('announcement-list');
        container.innerHTML = '';
        if (!items || items.length === 0) {
            container.innerHTML = '<div class="mini-note">No announcements.</div>';
            return;
        }

        items.forEach(item => {
            const row = document.createElement('div');
            row.className = 'timeline-item';
            row.innerHTML = `
                <strong>${UniShield.escapeHtml(item.title)}</strong>
                <span class="muted">${UniShield.escapeHtml(item.audience)} · ${UniShield.escapeHtml(item.priority)}</span>
                <span class="muted">${UniShield.escapeHtml(item.body)}</span>
            `;
            container.appendChild(row);
        });
    }

    async function loadDashboard() {
        currentHealth = await UniShield.resolveApiBase(true, 'secured');
        if (!currentHealth) {
            document.getElementById('security-snapshot').innerHTML = '<div class="warning">API not reachable. Start the Flask backend.</div>';
            return;
        }

        document.getElementById('mode-chip').textContent = `Mode: ${currentHealth.mode}`;
        const canContinue = await requireSessionIfNeeded();
        if (!canContinue) {
            return;
        }

        const dashboard = await UniShield.apiRequest('/api/dashboard');
        if (!dashboard.ok) {
            document.getElementById('security-snapshot').innerHTML = `<div class="warning">${UniShield.escapeHtml(dashboard.data.error || 'Failed to load dashboard')}</div>`;
            return;
        }

        const data = dashboard.data;
        document.getElementById('metric-students').textContent = UniShield.formatNumber(data.total_students);
        document.getElementById('metric-faculty').textContent = UniShield.formatNumber(data.total_faculty);
        document.getElementById('metric-courses').textContent = UniShield.formatNumber(data.total_courses);
        document.getElementById('metric-gpa').textContent = Number(data.avg_gpa || 0).toFixed(2);
        document.getElementById('metric-attendance').textContent = UniShield.formatPercent(data.avg_attendance || 0);
        document.getElementById('metric-fees').textContent = UniShield.formatPercent(data.fee_collection_rate || 0);
        document.getElementById('metric-requests').textContent = UniShield.formatNumber(data.total_requests);
        document.getElementById('metric-policies').textContent = UniShield.formatNumber((data.security_policies || []).length);
        document.getElementById('hero-students').textContent = UniShield.formatNumber(data.total_students);
        document.getElementById('hero-gpa').textContent = Number(data.avg_gpa || 0).toFixed(2);
        document.getElementById('hero-fees').textContent = UniShield.formatPercent(data.fee_collection_rate || 0);
        document.getElementById('request-chip').textContent = `Requests: ${UniShield.formatNumber(data.total_requests)}`;

        renderBarList('grade-chart', data.grade_distribution, 'grade', 'count', value => `${value} student(s)`);
        renderBarList('department-chart', data.department_breakdown, 'department', 'count', value => `${value} course(s)`);
        renderBarList('fee-chart', data.fee_status_breakdown, 'status', 'count', value => `${value} account(s)`);
        renderBarList('student-health', data.student_health.slice(0, 6), 'name', 'attendance_percentage', value => `${Number(value).toFixed(2)}% attendance`);
        renderLogs(data.recent_logs);
        renderPolicies(data.security_policies);
        renderAnnouncements(data.announcements);

        const snapshot = document.getElementById('security-snapshot');
        snapshot.innerHTML = `
            <div class="timeline-item">
                <strong>Mode</strong>
                <span class="muted">${UniShield.escapeHtml(currentHealth.mode)}</span>
            </div>
            <div class="timeline-item">
                <strong>Route catalog</strong>
                <span class="muted">${UniShield.formatNumber((data.route_catalog || []).length)} routes ready for discovery and demo.</span>
            </div>
            <div class="timeline-item">
                <strong>Collection rate</strong>
                <span class="muted">${UniShield.formatPercent(data.fee_collection_rate || 0)} of total term fees collected.</span>
            </div>
        `;
    }

    window.addEventListener('DOMContentLoaded', loadDashboard);
