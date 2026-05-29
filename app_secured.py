import re
import secrets
import time

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

from config import (
    ADMIN_EMAILS,
    API_PORT,
    APP_SECRET_KEY,
    AUTH_RATE_LIMIT_MAX_ATTEMPTS,
    AUTH_RATE_LIMIT_WINDOW_SECONDS,
    EMAIL_DOMAIN_ALLOWLIST,
    ENFORCE_API_KEY,
    ENFORCE_IP_ALLOWLIST,
    LMS_ALLOWED_IPS,
    LMS_API_KEY,
    API_RATE_LIMIT_MAX_REQUESTS,
    API_RATE_LIMIT_WINDOW_SECONDS,
    SCHOOL_NAME,
    SCHOOL_TAGLINE,
    SECRET_KEY,
    SESSION_COOKIE_SECURE,
    STUDENT_ID_REGEX,
    WINDOWS_IP
)
from database import (
    create_user,
    get_announcements,
    get_attendance_records,
    get_courses,
    get_dashboard_data,
    get_fee_accounts,
    get_faculty,
    get_module_overview,
    get_policies,
    get_route_catalog,
    get_student_profile,
    get_students,
    get_user_by_auth_token,
    get_user_by_email,
    get_user_by_id,
    get_users,
    init_db,
    log_api_event,
    create_auth_token,
    update_policy_status,
    update_user_role
)
from middleware import sign_payload, verify_payload

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = SESSION_COOKIE_SECURE
CORS(
    app,
    supports_credentials=True,
    allow_headers=['Content-Type', 'X-API-Key', 'X-Auth-Token', 'Authorization']
)

_rate_limits = {}


@app.before_request
def setup():
    init_db()


@app.after_request
def apply_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Cache-Control'] = 'no-store'
    return response


def secure_response(payload, status=200):
    if isinstance(payload, dict):
        return jsonify(sign_payload(payload)), status
    return jsonify(payload), status


def get_client_ip():
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def enforce_rate_limit(scope, max_requests, window_seconds):
    now = time.time()
    key = (scope, get_client_ip())
    recent = [timestamp for timestamp in _rate_limits.get(key, []) if now - timestamp < window_seconds]
    if len(recent) >= max_requests:
        retry_after = int(window_seconds - (now - recent[0])) + 1
        _rate_limits[key] = recent
        log_api_event(request.path, request.method, 429, None, get_client_ip())
        return secure_response({'error': 'Too many requests', 'retry_after_seconds': max(retry_after, 1)}, 429)

    recent.append(now)
    _rate_limits[key] = recent
    return None


def read_json_object():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, 'JSON object required'
    return data, None


def is_valid_email(email):
    match = re.fullmatch(r'[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})', email)
    if not match:
        return False
    domain = match.group(1).lower()
    if not EMAIL_DOMAIN_ALLOWLIST:
        return True
    return domain in {item.lower() for item in EMAIL_DOMAIN_ALLOWLIST}


def is_strong_password(password):
    return len(password) >= 8 and bool(re.search(r'[A-Za-z]', password)) and bool(re.search(r'\d', password))


def is_valid_student_id(student_id):
    return bool(re.fullmatch(STUDENT_ID_REGEX, student_id))


def require_login():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.removeprefix('Bearer ').strip()
        user = get_user_by_auth_token(token)
        if user:
            return user

    token = request.headers.get('X-Auth-Token', '').strip()
    if token:
        user = get_user_by_auth_token(token)
        if user:
            return user

    user_id = session.get('user_id')
    if not user_id:
        return None
    return get_user_by_id(user_id)


def require_role(user, roles):
    return bool(user) and user.get('role') in roles


def validate_api_key():
    if not ENFORCE_API_KEY:
        return True, None
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != LMS_API_KEY:
        return False, 'Invalid API key'
    return True, None


def validate_ip_allowlist():
    if not ENFORCE_IP_ALLOWLIST:
        return True, None
    client_ip = get_client_ip()
    if client_ip not in LMS_ALLOWED_IPS:
        return False, f'IP {client_ip} not allowed'
    return True, None


def enforce_lms_controls():
    user = require_login()
    if user:
        return True, None, user

    ok, reason = validate_api_key()
    if not ok:
        log_api_event(request.path, request.method, 401, None, get_client_ip())
        return False, reason, None

    ok, reason = validate_ip_allowlist()
    if not ok:
        log_api_event(request.path, request.method, 403, None, get_client_ip())
        return False, reason, None

    return True, None, None


def require_admin():
    user = require_login()
    if not user or not require_role(user, {'admin'}):
        return None
    return user


def issue_auth_token(user_id):
    token = secrets.token_urlsafe(32)
    create_auth_token(token, user_id)
    return token


def revoke_auth_token(token):
    if token:
        from database import revoke_auth_token as revoke_token_record
        revoke_token_record(token)


def extract_auth_token():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header.removeprefix('Bearer ').strip()
    token = request.headers.get('X-Auth-Token', '').strip()
    return token or None


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'running',
        'mode': 'SECURED',
        'school': SCHOOL_NAME,
        'tagline': SCHOOL_TAGLINE
    }), 200


@app.route('/api/routes', methods=['GET'])
def route_catalog():
    ok, reason, user = enforce_lms_controls()
    if not ok:
        return secure_response({'error': reason}, 401 if 'API key' in reason else 403)
    return secure_response({
        'count': len(get_route_catalog()),
        'routes': get_route_catalog(),
        'mode': 'SECURED',
        'requested_by': user['email'] if user else 'service'
    })


@app.route('/api/modules', methods=['GET'])
def modules():
    ok, reason, user = enforce_lms_controls()
    if not ok:
        return secure_response({'error': reason}, 401 if 'API key' in reason else 403)
    return secure_response({
        'modules': get_module_overview(),
        'mode': 'SECURED',
        'requested_by': user['email'] if user else 'service'
    })


@app.route('/api/auth/signup', methods=['POST'])
def signup():
    rate_limit = enforce_rate_limit('auth', AUTH_RATE_LIMIT_MAX_ATTEMPTS, AUTH_RATE_LIMIT_WINDOW_SECONDS)
    if rate_limit:
        return rate_limit

    data, error_message = read_json_object()
    if error_message:
        return secure_response({'error': error_message}, 400)

    is_valid, reason = verify_payload(data)
    if not is_valid:
        return secure_response({'error': 'PAYLOAD INTEGRITY VIOLATION', 'reason': reason, 'status': 'BLOCKED'}, 403)

    email = (data.get('email') or '').strip().lower()
    full_name = (data.get('full_name') or '').strip()
    password = data.get('password') or ''

    if not email or not full_name or not password:
        return secure_response({'error': 'Email, full_name and password are required'}, 400)
    if len(full_name) < 3 or len(full_name) > 80:
        return secure_response({'error': 'Full name must be between 3 and 80 characters'}, 400)
    if not is_valid_email(email):
        return secure_response({'error': 'Email domain is not allowed'}, 400)
    if not is_strong_password(password):
        return secure_response({'error': 'Password must be at least 8 chars and include letters and numbers'}, 400)
    if get_user_by_email(email):
        return secure_response({'error': 'Email already registered'}, 409)

    role = 'admin' if email in ADMIN_EMAILS else 'student'
    password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    user_id = create_user(email, full_name, password_hash, role)
    session['user_id'] = user_id
    auth_token = issue_auth_token(user_id)
    return secure_response({'id': user_id, 'email': email, 'full_name': full_name, 'role': role, 'auth_token': auth_token}, 201)


@app.route('/api/auth/login', methods=['POST'])
def login():
    rate_limit = enforce_rate_limit('auth', AUTH_RATE_LIMIT_MAX_ATTEMPTS, AUTH_RATE_LIMIT_WINDOW_SECONDS)
    if rate_limit:
        return rate_limit

    data, error_message = read_json_object()
    if error_message:
        return secure_response({'error': error_message}, 400)

    is_valid, reason = verify_payload(data)
    if not is_valid:
        return secure_response({'error': 'PAYLOAD INTEGRITY VIOLATION', 'reason': reason, 'status': 'BLOCKED'}, 403)

    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return secure_response({'error': 'Email and password are required'}, 400)

    user = get_user_by_email(email)
    if not user or not check_password_hash(user['password_hash'], password):
        return secure_response({'error': 'Invalid email or password'}, 401)

    session['user_id'] = user['id']
    auth_token = issue_auth_token(user['id'])
    return secure_response({
        'id': user['id'],
        'email': user['email'],
        'full_name': user['full_name'],
        'role': user['role'],
        'auth_token': auth_token
    })


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    token = extract_auth_token()
    if token:
        revoke_auth_token(token)
    session.clear()
    return secure_response({'status': 'signed_out'})


@app.route('/api/auth/me', methods=['GET'])
def me():
    user = require_login()
    if not user:
        return secure_response({'error': 'Unauthorized'}, 401)
    return secure_response({
        'id': user['id'],
        'email': user['email'],
        'full_name': user['full_name'],
        'role': user['role']
    })


@app.route('/api/student', methods=['POST'])
def get_student_data():
    ok, reason, user = enforce_lms_controls()
    if not ok:
        return secure_response({'error': reason}, 401 if 'API key' in reason else 403)

    rate_limit = enforce_rate_limit('student_lookup', API_RATE_LIMIT_MAX_REQUESTS, API_RATE_LIMIT_WINDOW_SECONDS)
    if rate_limit:
        return rate_limit

    data, error_message = read_json_object()
    if error_message:
        log_api_event('/api/student', 'POST', 400, None, get_client_ip())
        return secure_response({'error': error_message}, 400)

    is_valid, reason = verify_payload(data)
    if not is_valid:
        student_id = data.get('student_id') if isinstance(data, dict) else None
        log_api_event('/api/student', 'POST', 403, student_id, get_client_ip())
        return secure_response({
            'error': 'PAYLOAD INTEGRITY VIOLATION',
            'reason': reason,
            'status': 'BLOCKED'
        }, 403)

    student_id = (data.get('student_id') or '').strip().upper()
    if not is_valid_student_id(student_id):
        log_api_event('/api/student', 'POST', 400, student_id or None, get_client_ip())
        return secure_response({'error': 'Invalid student_id format. Expected pattern S###'}, 400)

    profile = get_student_profile(student_id)
    if not profile:
        log_api_event('/api/student', 'POST', 404, student_id, get_client_ip())
        return secure_response({'error': f'Student {student_id} not found'}, 404)

    log_api_event('/api/student', 'POST', 200, student_id, get_client_ip())
    return secure_response({
        'student_id': profile['id'],
        'name': profile['name'],
        'course': profile['course'],
        'grade': profile['grade'],
        'marks': profile['marks'],
        'gpa': profile['gpa'],
        'semester': profile.get('semester'),
        'advisor': profile.get('advisor'),
        'track': profile.get('track'),
        'campus': profile.get('campus'),
        'status': profile.get('status'),
        'attendance': profile.get('attendance'),
        'fee_account': profile.get('fee_account'),
        'enrolled_courses': profile.get('enrolled_courses', []),
        'security': 'PAYLOAD VERIFIED - TAMPER FREE'
    })


@app.route('/api/students', methods=['GET'])
def list_students():
    ok, reason, user = enforce_lms_controls()
    if not ok:
        return secure_response({'error': reason}, 401 if 'API key' in reason else 403)

    rate_limit = enforce_rate_limit('students_list', API_RATE_LIMIT_MAX_REQUESTS, API_RATE_LIMIT_WINDOW_SECONDS)
    if rate_limit:
        return rate_limit
    return secure_response({
        'count': len(get_students()),
        'students': get_students(),
        'requested_by': user['email'] if user else 'service'
    })


@app.route('/api/courses', methods=['GET'])
def list_courses():
    ok, reason, user = enforce_lms_controls()
    if not ok:
        return secure_response({'error': reason}, 401 if 'API key' in reason else 403)
    return secure_response({
        'count': len(get_courses()),
        'courses': get_courses(),
        'requested_by': user['email'] if user else 'service'
    })


@app.route('/api/faculty', methods=['GET'])
def list_faculty():
    ok, reason, user = enforce_lms_controls()
    if not ok:
        return secure_response({'error': reason}, 401 if 'API key' in reason else 403)
    return secure_response({
        'count': len(get_faculty()),
        'faculty': get_faculty(),
        'requested_by': user['email'] if user else 'service'
    })


@app.route('/api/attendance', methods=['GET'])
def list_attendance():
    ok, reason, user = enforce_lms_controls()
    if not ok:
        return secure_response({'error': reason}, 401 if 'API key' in reason else 403)
    return secure_response({
        'count': len(get_attendance_records()),
        'attendance': get_attendance_records(),
        'requested_by': user['email'] if user else 'service'
    })


@app.route('/api/fees', methods=['GET'])
def list_fees():
    ok, reason, user = enforce_lms_controls()
    if not ok:
        return secure_response({'error': reason}, 401 if 'API key' in reason else 403)
    return secure_response({
        'count': len(get_fee_accounts()),
        'fees': get_fee_accounts(),
        'requested_by': user['email'] if user else 'service'
    })


@app.route('/api/announcements', methods=['GET'])
def list_announcements():
    ok, reason, user = enforce_lms_controls()
    if not ok:
        return secure_response({'error': reason}, 401 if 'API key' in reason else 403)
    return secure_response({
        'count': len(get_announcements()),
        'announcements': get_announcements(),
        'requested_by': user['email'] if user else 'service'
    })


@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    user = require_login()
    if not user:
        return secure_response({'error': 'Unauthorized'}, 401)

    rate_limit = enforce_rate_limit('dashboard', API_RATE_LIMIT_MAX_REQUESTS, API_RATE_LIMIT_WINDOW_SECONDS)
    if rate_limit:
        return rate_limit

    data = get_dashboard_data()
    data['requested_by'] = user['email']
    return secure_response(data)


@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    user = require_admin()
    if not user:
        return secure_response({'error': 'Forbidden'}, 403)
    return secure_response({'users': get_users(), 'requested_by': user['email']})


@app.route('/api/admin/users/<int:user_id>/role', methods=['PUT'])
def admin_update_user_role(user_id):
    user = require_admin()
    if not user:
        return secure_response({'error': 'Forbidden'}, 403)

    data, error_message = read_json_object()
    if error_message:
        return secure_response({'error': error_message}, 400)

    is_valid, reason = verify_payload(data)
    if not is_valid:
        return secure_response({'error': 'PAYLOAD INTEGRITY VIOLATION', 'reason': reason, 'status': 'BLOCKED'}, 403)

    role = (data.get('role') or '').strip().lower()
    if role not in {'student', 'faculty', 'registrar', 'admin'}:
        return secure_response({'error': 'Invalid role'}, 400)

    updated = update_user_role(user_id, role)
    if not updated:
        return secure_response({'error': 'User not found'}, 404)
    updated['requested_by'] = user['email']
    return secure_response(updated)


@app.route('/api/admin/policies', methods=['GET'])
def admin_policies():
    user = require_admin()
    if not user:
        return secure_response({'error': 'Forbidden'}, 403)
    return secure_response({'policies': get_policies(), 'requested_by': user['email']})


@app.route('/api/admin/policies/<int:policy_id>/status', methods=['PUT'])
def admin_update_policy(policy_id):
    user = require_admin()
    if not user:
        return secure_response({'error': 'Forbidden'}, 403)

    data, error_message = read_json_object()
    if error_message:
        return secure_response({'error': error_message}, 400)

    is_valid, reason = verify_payload(data)
    if not is_valid:
        return secure_response({'error': 'PAYLOAD INTEGRITY VIOLATION', 'reason': reason, 'status': 'BLOCKED'}, 403)

    status = (data.get('status') or '').strip().upper()
    if status not in {'ENABLED', 'READY', 'DISABLED'}:
        return secure_response({'error': 'Invalid status'}, 400)

    updated = update_policy_status(policy_id, status)
    if not updated:
        return secure_response({'error': 'Policy not found'}, 404)
    updated['requested_by'] = user['email']
    return secure_response(updated)


if __name__ == '__main__':
    init_db()
    print(f'SECURED API running at http://{WINDOWS_IP}:{API_PORT}')
    print('Payload integrity verification: ACTIVE')
    app.run(host='0.0.0.0', port=API_PORT, debug=False)
