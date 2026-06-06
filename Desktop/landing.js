async function renderLanding() {
        const status = document.getElementById('system-status');
        const timeline = document.getElementById('timeline');
        const moduleGrid = document.getElementById('module-grid');

        const health = await UniShield.resolveApiBase(true);
        if (!health) {
            status.innerHTML = 'API not reachable. Start <strong>app_unsecured.py</strong> or <strong>app_secured.py</strong>.';
            timeline.innerHTML = `
                <div class="timeline-item"><strong>Backend offline</strong><span class="muted">The UI is ready, but the Flask API is not running yet.</span></div>
            `;
            document.getElementById('metric-mode').textContent = '--';
            document.getElementById('metric-routes').textContent = '--';
            document.getElementById('metric-modules').textContent = '--';
            return;
        }

        const modulesResponse = await UniShield.apiRequest('/api/modules', { credentials: 'include' });
        const routesResponse = await UniShield.apiRequest('/api/routes', { credentials: 'include' });
        const routes = routesResponse.ok ? routesResponse.data.routes || [] : [];
        const modules = modulesResponse.ok ? modulesResponse.data.modules || [] : [];

        status.innerHTML = `API online in <strong>${health.mode}</strong> mode.`;
        document.getElementById('hero-mode').textContent = health.mode;
        document.getElementById('metric-mode').textContent = health.mode;
        document.getElementById('hero-routes').textContent = routesResponse.ok ? `${routes.length}` : '--';
        document.getElementById('hero-modules').textContent = modulesResponse.ok ? `${modules.length}` : '--';
        document.getElementById('metric-routes').textContent = routesResponse.ok ? `${routes.length}` : '--';
        document.getElementById('metric-modules').textContent = modulesResponse.ok ? `${modules.length}` : '--';

        timeline.innerHTML = `
            <div class="timeline-item">
                <strong>School name</strong>
                <span class="muted">${health.school || 'UniShield Academy'}</span>
            </div>
            <div class="timeline-item">
                <strong>Tagline</strong>
                <span class="muted">${health.tagline || 'Secure school management with API payload integrity'}</span>
            </div>
            <div class="timeline-item">
                <strong>Route discovery</strong>
                <span class="muted">${routesResponse.ok ? `${routes.length} routes available for the demo.` : 'Route map unavailable.'}</span>
            </div>
        `;

        moduleGrid.innerHTML = '';
        modules.forEach(module => {
            const card = document.createElement('div');
            card.className = 'card module-card';
            card.innerHTML = `
                <span class="eyebrow">${module.label}</span>
                <div class="metric">${module.metric}</div>
                <div class="muted">${module.metric_label}</div>
                <div class="subtitle" style="font-size:13px; margin:0;">${module.description}</div>
            `;
            moduleGrid.appendChild(card);
        });
    }

    window.addEventListener('DOMContentLoaded', renderLanding);
