from flask import Flask, jsonify, request
from flask_cors import CORS

from config import API_PORT, SCHOOL_NAME, SCHOOL_TAGLINE, WINDOWS_IP
from database import (
    get_announcements,
    get_attendance_records,
    get_dashboard_data,
    get_fee_accounts,
    get_faculty,
    get_module_overview,
    get_policies,
    get_route_catalog,
    get_student_profile,
    get_students,
    get_courses,
    get_users,
    init_db,
    log_api_event,
    update_policy_status,
    update_user_role
)

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.before_request
def setup():
    init_db()


def read_json_object():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify({'error': 'JSON object required'}), 400)
    return data, None


def open_response(payload, status=200):
    return jsonify(payload), status


@app.route('/api/health', methods=['GET'])
def health():
    return open_response({
        'status': 'running',
        'mode': 'UNSECURED',
        'school': SCHOOL_NAME,
        'tagline': SCHOOL_TAGLINE
    })


@app.route('/api/auth/me', methods=['GET', 'OPTIONS'])
def auth_me_unsecured():
    return open_response({
        'authenticated': False,
        'mode': 'UNSECURED',
        'role': 'guest',
        'message': 'Authentication is disabled in unsecured mode'
    }, 401)


@app.route('/api/auth/logout', methods=['POST', 'OPTIONS'])
def auth_logout_unsecured():
    return open_response({
        'ok': True,
        'mode': 'UNSECURED'
    })


@app.route('/api/routes', methods=['GET'])
def routes():
    return open_response({
        'count': len(get_route_catalog()),
        'routes': get_route_catalog(),
        'mode': 'UNSECURED'
    })


@app.route('/api/modules', methods=['GET'])
def modules():
    return open_response({
        'modules': get_module_overview(),
        'mode': 'UNSECURED'
    })


@app.route('/api/student', methods=['POST'])
def get_student_data():
    data, error_response = read_json_object()
    if error_response:
        log_api_event('/api/student', 'POST', 400, None, request.remote_addr)
        return error_response

    student_id = (data.get('student_id') or '').strip().upper()
    if not student_id:
        log_api_event('/api/student', 'POST', 400, None, request.remote_addr)
        return open_response({'error': 'student_id required'}, 400)

    profile = get_student_profile(student_id)
    if not profile:
        log_api_event('/api/student', 'POST', 404, student_id, request.remote_addr)
        return open_response({'error': f'Student {student_id} not found'}, 404)

    log_api_event('/api/student', 'POST', 200, student_id, request.remote_addr)
    return open_response({
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
        'security': 'UNSECURED - vulnerable to payload tampering'
    })


@app.route('/api/students', methods=['GET'])
def list_students():
    return open_response({
        'count': len(get_students()),
        'students': get_students()
    })


@app.route('/api/courses', methods=['GET'])
def list_courses():
    return open_response({
        'count': len(get_courses()),
        'courses': get_courses()
    })


@app.route('/api/faculty', methods=['GET'])
def list_faculty():
    return open_response({
        'count': len(get_faculty()),
        'faculty': get_faculty()
    })


@app.route('/api/attendance', methods=['GET'])
def list_attendance():
    return open_response({
        'count': len(get_attendance_records()),
        'attendance': get_attendance_records()
    })


@app.route('/api/fees', methods=['GET'])
def list_fees():
    return open_response({
        'count': len(get_fee_accounts()),
        'fees': get_fee_accounts()
    })


@app.route('/api/announcements', methods=['GET'])
def list_announcements():
    return open_response({
        'count': len(get_announcements()),
        'announcements': get_announcements()
    })


@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    return open_response(get_dashboard_data())


@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    return open_response({
        'users': get_users()
    })


@app.route('/api/admin/users/<int:user_id>/role', methods=['PUT'])
def admin_update_user_role(user_id):
    data, error_response = read_json_object()
    if error_response:
        return error_response

    role = (data.get('role') or '').strip().lower()
    if role not in {'student', 'faculty', 'registrar', 'admin'}:
        return open_response({'error': 'Invalid role'}, 400)

    updated = update_user_role(user_id, role)
    if not updated:
        return open_response({'error': 'User not found'}, 404)
    return open_response(updated)


@app.route('/api/admin/policies', methods=['GET'])
def admin_policies():
    return open_response({
        'policies': get_policies()
    })


@app.route('/api/admin/policies/<int:policy_id>/status', methods=['PUT'])
def admin_update_policy(policy_id):
    data, error_response = read_json_object()
    if error_response:
        return error_response

    status = (data.get('status') or '').strip().upper()
    if status not in {'ENABLED', 'READY', 'DISABLED'}:
        return open_response({'error': 'Invalid status'}, 400)

    updated = update_policy_status(policy_id, status)
    if not updated:
        return open_response({'error': 'Policy not found'}, 404)
    return open_response(updated)


@app.route('/api/healthcheck', methods=['GET'])
def healthcheck_alias():
    return health()


if __name__ == '__main__':
    init_db()
    print(f'UNSECURED API running at http://{WINDOWS_IP}:{API_PORT}')
    print('WARNING: This API exposes school-management data without integrity controls')
    app.run(host='0.0.0.0', port=API_PORT, debug=True)
