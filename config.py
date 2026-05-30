# config.py
# Central configuration file for the API Security Lab

# Network configuration
WINDOWS_IP = '192.168.191.1'      # Your Windows host IP (VMware host-only / VMnet8)
KALI_IP    = '192.168.191.129'    # Your Kali Linux VM IP on the same network

API_PORT = 5000

# Database
DB_PATH = 'students.db'

# Product identity
SCHOOL_NAME = 'UniShield Academy'
SCHOOL_TAGLINE = 'Secure school management with API payload integrity'

# Module catalog used by the UI and route summaries
MODULE_CATALOG = [
	{
		'key': 'student-records',
		'label': 'Student Records',
		'description': 'Profiles, grades, attendance, and academic status at a glance.'
	},
	{
		'key': 'academic-ops',
		'label': 'Academic Operations',
		'description': 'Courses, faculty, departments, and enrollment data.'
	},
	{
		'key': 'finance-desk',
		'label': 'Finance Desk',
		'description': 'Fee balances, dues, payment status, and term summaries.'
	},
	{
		'key': 'security-center',
		'label': 'Security Center',
		'description': 'Policies, route discovery, audit logs, and payload integrity controls.'
	}
]

# API route catalog used for discovery/demo screens
ROUTE_CATALOG = [
	{'method': 'GET', 'path': '/api/health', 'module': 'Platform', 'visibility': 'public', 'purpose': 'API heartbeat and mode detection'},
	{'method': 'GET', 'path': '/api/routes', 'module': 'Platform', 'visibility': 'public', 'purpose': 'Route catalog for demo and attack-surface discovery'},
	{'method': 'GET', 'path': '/api/modules', 'module': 'Platform', 'visibility': 'public', 'purpose': 'School module overview cards'},
	{'method': 'GET', 'path': '/api/students', 'module': 'Student Records', 'visibility': 'service', 'purpose': 'Student directory and selector data'},
	{'method': 'POST', 'path': '/api/student', 'module': 'Student Records', 'visibility': 'service', 'purpose': 'Fetch a single student profile from a signed payload'},
	{'method': 'GET', 'path': '/api/courses', 'module': 'Academic Operations', 'visibility': 'service', 'purpose': 'Course catalog and schedule details'},
	{'method': 'GET', 'path': '/api/faculty', 'module': 'Academic Operations', 'visibility': 'service', 'purpose': 'Faculty directory and assignments'},
	{'method': 'GET', 'path': '/api/attendance', 'module': 'Academic Operations', 'visibility': 'service', 'purpose': 'Attendance overview by student'},
	{'method': 'GET', 'path': '/api/fees', 'module': 'Finance Desk', 'visibility': 'service', 'purpose': 'Fee ledger and payment status'},
	{'method': 'GET', 'path': '/api/announcements', 'module': 'Academic Operations', 'visibility': 'service', 'purpose': 'Campus notices and updates'},
	{'method': 'GET', 'path': '/api/dashboard', 'module': 'Security Center', 'visibility': 'service', 'purpose': 'Management analytics and logs'},
	{'method': 'GET', 'path': '/api/auth/me', 'module': 'Security Center', 'visibility': 'secured', 'purpose': 'Session identity lookup'},
	{'method': 'POST', 'path': '/api/auth/login', 'module': 'Security Center', 'visibility': 'secured', 'purpose': 'Authenticate a management user'},
	{'method': 'POST', 'path': '/api/auth/signup', 'module': 'Security Center', 'visibility': 'secured', 'purpose': 'Register a management user'},
	{'method': 'GET', 'path': '/api/admin/users', 'module': 'Security Center', 'visibility': 'admin', 'purpose': 'Admin roster and role control'},
	{'method': 'PUT', 'path': '/api/admin/users/<id>/role', 'module': 'Security Center', 'visibility': 'admin', 'purpose': 'Update a user role'},
	{'method': 'GET', 'path': '/api/admin/policies', 'module': 'Security Center', 'visibility': 'admin', 'purpose': 'Security policy catalog'},
	{'method': 'PUT', 'path': '/api/admin/policies/<id>/status', 'module': 'Security Center', 'visibility': 'admin', 'purpose': 'Toggle a policy status'}
]

# HMAC secret key – MUST be identical in middleware.py AND student_portal.html
SECRET_KEY = 'infosec-hmac-secret-2024'

# Flask session key for login/signup
APP_SECRET_KEY = 'unishield-session-secret-2026'
SESSION_COOKIE_SECURE = False

# LMS security controls
ENFORCE_API_KEY = True
ENFORCE_IP_ALLOWLIST = True
LMS_API_KEY = 'unishield-lms-key-2026'
LMS_ALLOWED_IPS = [
	'192.168.191.1',
	'192.168.191.129',
	'127.0.0.1',
	'::1'
]

# Admin users (auto-elevated on signup)
ADMIN_EMAILS = [
	'security.admin@university.edu'
]

# Validation and abuse prevention
# Leave empty to allow any domain
EMAIL_DOMAIN_ALLOWLIST = []
STUDENT_ID_REGEX = r'^S\d{3}$'
AUTH_RATE_LIMIT_WINDOW_SECONDS = 300
AUTH_RATE_LIMIT_MAX_ATTEMPTS = 12
API_RATE_LIMIT_WINDOW_SECONDS = 60
API_RATE_LIMIT_MAX_REQUESTS = 120
