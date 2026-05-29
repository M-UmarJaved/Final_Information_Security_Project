# database.py
# Creates and seeds the student database

import sqlite3
from config import DB_PATH, MODULE_CATALOG, ROUTE_CATALOG

_db_initialized = False

def init_db():
    """Initialize the database and seed with sample student records."""
    global _db_initialized
    if _db_initialized:
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create students table
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        course TEXT NOT NULL,
        grade TEXT NOT NULL,
        marks INTEGER NOT NULL,
        gpa REAL NOT NULL
    )''')

    # Create departments table
    c.execute('''CREATE TABLE IF NOT EXISTS departments (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        head TEXT NOT NULL
    )''')

    # Create courses table
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        code TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        department_id TEXT NOT NULL
    )''')

    # Create API logs table
    c.execute('''CREATE TABLE IF NOT EXISTS api_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        endpoint TEXT NOT NULL,
        method TEXT NOT NULL,
        status INTEGER NOT NULL,
        student_id TEXT,
        client_ip TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Create security policies table
    c.execute('''CREATE TABLE IF NOT EXISTS security_policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL,
        details TEXT NOT NULL
    )''')

    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Create school management tables for the demo
    c.execute('''CREATE TABLE IF NOT EXISTS student_profiles (
        student_id TEXT PRIMARY KEY,
        semester TEXT NOT NULL,
        advisor TEXT NOT NULL,
        track TEXT NOT NULL,
        campus TEXT NOT NULL,
        status TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS course_details (
        course_code TEXT PRIMARY KEY,
        credits INTEGER NOT NULL,
        instructor TEXT NOT NULL,
        schedule TEXT NOT NULL,
        room TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS faculty (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        department_id TEXT NOT NULL,
        title TEXT NOT NULL,
        email TEXT NOT NULL,
        office TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance_records (
        student_id TEXT PRIMARY KEY,
        semester TEXT NOT NULL,
        present_classes INTEGER NOT NULL,
        total_classes INTEGER NOT NULL,
        percentage REAL NOT NULL,
        trend TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS fee_accounts (
        student_id TEXT PRIMARY KEY,
        semester TEXT NOT NULL,
        total_fee REAL NOT NULL,
        paid_amount REAL NOT NULL,
        due_amount REAL NOT NULL,
        status TEXT NOT NULL,
        due_date TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS student_enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        course_code TEXT NOT NULL,
        study_mode TEXT NOT NULL
    )''')

    # Keep one enrollment row per student/course/mode and clean old duplicates.
    c.execute('''
        DELETE FROM student_enrollments
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM student_enrollments
            GROUP BY student_id, course_code, study_mode
        )
    ''')
    c.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_student_enrollments_unique
        ON student_enrollments (student_id, course_code, study_mode)
    ''')

    c.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        audience TEXT NOT NULL,
        body TEXT NOT NULL,
        priority TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Lightweight migration for existing databases
    c.execute("PRAGMA table_info(users)")
    user_columns = {row[1] for row in c.fetchall()}
    if 'role' not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'student'")

    # Seed sample student data
    students = [
        ('S001', 'Ahmed Khan', 'Computer Science', 'F', 38, 1.0),
        ('S002', 'Sara Ali', 'Computer Science', 'A', 92, 4.0),
        ('S003', 'Bilal Hassan', 'Computer Science', 'B', 75, 3.0),
        ('S004', 'Fatima Malik', 'Computer Science', 'A+', 98, 4.0),
        ('S005', 'Usman Sheikh', 'Computer Science', 'C', 60, 2.0),
        ('S006', 'Zainab Noor', 'Information Systems', 'A', 90, 3.9),
        ('S007', 'Hassan Raza', 'Information Systems', 'B', 78, 3.1),
        ('S008', 'Maryam Iqbal', 'Data Science', 'A+', 96, 4.0),
        ('S009', 'Ali Rauf', 'Cyber Security', 'B', 72, 2.9),
        ('S010', 'Ayesha Farooq', 'Software Engineering', 'A', 88, 3.7),
    ]

    c.executemany(
        'INSERT OR IGNORE INTO students VALUES (?,?,?,?,?,?)',
        students
    )

    departments = [
        ('CS', 'Computer Science', 'Dr. Usama Qureshi'),
        ('IS', 'Information Systems', 'Dr. Rabia Siddiqi'),
        ('DS', 'Data Science', 'Dr. Saad Mahmood'),
        ('SE', 'Software Engineering', 'Dr. Noor Fatima'),
        ('CY', 'Cyber Security', 'Dr. Hamza Tariq'),
    ]

    c.executemany(
        'INSERT OR IGNORE INTO departments VALUES (?,?,?)',
        departments
    )

    courses = [
        ('CS101', 'Programming Fundamentals', 'CS'),
        ('CS202', 'Computer Networks', 'CS'),
        ('IS210', 'Systems Analysis', 'IS'),
        ('DS310', 'Applied Machine Learning', 'DS'),
        ('SE201', 'Software Design', 'SE'),
        ('CY220', 'Digital Forensics', 'CY'),
    ]

    c.executemany(
        'INSERT OR IGNORE INTO courses VALUES (?,?,?)',
        courses
    )

    course_details = [
        ('CS101', 3, 'Dr. Usama Qureshi', 'Mon/Wed 09:00-10:30', 'Lab A'),
        ('CS202', 3, 'Dr. Hamza Tariq', 'Tue/Thu 11:00-12:30', 'Room C-12'),
        ('IS210', 3, 'Dr. Rabia Siddiqi', 'Mon/Wed 13:00-14:30', 'Room B-08'),
        ('DS310', 4, 'Dr. Saad Mahmood', 'Tue/Thu 14:00-15:30', 'Data Lab'),
        ('SE201', 3, 'Dr. Noor Fatima', 'Fri 09:00-12:00', 'Studio 2'),
        ('CY220', 3, 'Dr. Hamza Tariq', 'Fri 13:00-16:00', 'Security Lab')
    ]

    c.executemany(
        'INSERT OR IGNORE INTO course_details VALUES (?,?,?,?,?)',
        course_details
    )

    faculty = [
        ('Dr. Usama Qureshi', 'CS', 'Professor', 'usama.qureshi@unishield.edu', 'Room C-01'),
        ('Dr. Rabia Siddiqi', 'IS', 'Associate Professor', 'rabia.siddiqi@unishield.edu', 'Room B-04'),
        ('Dr. Saad Mahmood', 'DS', 'Assistant Professor', 'saad.mahmood@unishield.edu', 'Lab D-03'),
        ('Dr. Noor Fatima', 'SE', 'Professor', 'noor.fatima@unishield.edu', 'Studio 2'),
        ('Dr. Hamza Tariq', 'CY', 'Lecturer', 'hamza.tariq@unishield.edu', 'Security Lab'),
        ('Dr. Sana Qureshi', 'SE', 'Program Advisor', 'sana.qureshi@unishield.edu', 'Room A-11')
    ]

    c.executemany(
        'INSERT OR IGNORE INTO faculty (full_name, department_id, title, email, office) VALUES (?,?,?,?,?)',
        faculty
    )

    student_profiles = [
        ('S001', 'Semester 02', 'Dr. Sana Qureshi', 'Software Engineering', 'Main Campus', 'Probation'),
        ('S002', 'Semester 04', 'Dr. Rabia Siddiqi', 'Information Systems', 'Main Campus', 'Active'),
        ('S003', 'Semester 03', 'Dr. Usama Qureshi', 'Computer Science', 'North Wing', 'Active'),
        ('S004', 'Semester 05', 'Dr. Noor Fatima', 'Software Engineering', 'Main Campus', 'Active'),
        ('S005', 'Semester 01', 'Dr. Hamza Tariq', 'Cyber Security', 'North Wing', 'Watchlist'),
        ('S006', 'Semester 04', 'Dr. Rabia Siddiqi', 'Information Systems', 'Main Campus', 'Active'),
        ('S007', 'Semester 03', 'Dr. Saad Mahmood', 'Data Science', 'Data Block', 'Active'),
        ('S008', 'Semester 05', 'Dr. Saad Mahmood', 'Data Science', 'Data Block', "Dean's List"),
        ('S009', 'Semester 02', 'Dr. Hamza Tariq', 'Cyber Security', 'North Wing', 'Active'),
        ('S010', 'Semester 06', 'Dr. Noor Fatima', 'Software Engineering', 'Main Campus', 'Active')
    ]

    c.executemany(
        'INSERT OR IGNORE INTO student_profiles VALUES (?,?,?,?,?,?)',
        student_profiles
    )

    attendance_records = [
        ('S001', 'Spring 2026', 42, 54, 77.78, 'Watch'),
        ('S002', 'Spring 2026', 51, 52, 98.08, 'Excellent'),
        ('S003', 'Spring 2026', 46, 54, 85.19, 'Healthy'),
        ('S004', 'Spring 2026', 53, 54, 98.15, 'Excellent'),
        ('S005', 'Spring 2026', 38, 50, 76.0, 'Watch'),
        ('S006', 'Spring 2026', 48, 52, 92.31, 'Healthy'),
        ('S007', 'Spring 2026', 45, 51, 88.24, 'Healthy'),
        ('S008', 'Spring 2026', 52, 53, 98.11, 'Excellent'),
        ('S009', 'Spring 2026', 43, 50, 86.0, 'Healthy'),
        ('S010', 'Spring 2026', 50, 54, 92.59, 'Healthy')
    ]

    c.executemany(
        'INSERT OR IGNORE INTO attendance_records VALUES (?,?,?,?,?,?)',
        attendance_records
    )

    fee_accounts = [
        ('S001', 'Spring 2026', 120000, 82000, 38000, 'PARTIAL', '2026-06-15'),
        ('S002', 'Spring 2026', 118000, 118000, 0, 'PAID', '2026-06-15'),
        ('S003', 'Spring 2026', 115000, 90000, 25000, 'PARTIAL', '2026-06-15'),
        ('S004', 'Spring 2026', 122000, 122000, 0, 'PAID', '2026-06-15'),
        ('S005', 'Spring 2026', 110000, 60000, 50000, 'DUE', '2026-06-15'),
        ('S006', 'Spring 2026', 118000, 118000, 0, 'PAID', '2026-06-15'),
        ('S007', 'Spring 2026', 117000, 98000, 19000, 'PARTIAL', '2026-06-15'),
        ('S008', 'Spring 2026', 125000, 125000, 0, 'PAID', '2026-06-15'),
        ('S009', 'Spring 2026', 112000, 76000, 36000, 'PARTIAL', '2026-06-15'),
        ('S010', 'Spring 2026', 123000, 123000, 0, 'PAID', '2026-06-15')
    ]

    c.executemany(
        'INSERT OR IGNORE INTO fee_accounts VALUES (?,?,?,?,?,?,?)',
        fee_accounts
    )

    student_enrollments = [
        ('S001', 'SE201', 'Core'),
        ('S001', 'CS101', 'Core'),
        ('S001', 'IS210', 'Elective'),
        ('S002', 'IS210', 'Core'),
        ('S002', 'CS202', 'Core'),
        ('S002', 'SE201', 'Elective'),
        ('S003', 'CS101', 'Core'),
        ('S003', 'CS202', 'Core'),
        ('S003', 'CY220', 'Elective'),
        ('S004', 'SE201', 'Core'),
        ('S004', 'DS310', 'Elective'),
        ('S004', 'CS202', 'Core'),
        ('S005', 'CY220', 'Core'),
        ('S005', 'CS101', 'Core'),
        ('S005', 'IS210', 'Elective'),
        ('S006', 'IS210', 'Core'),
        ('S006', 'CS101', 'Core'),
        ('S006', 'DS310', 'Elective'),
        ('S007', 'DS310', 'Core'),
        ('S007', 'CS202', 'Core'),
        ('S007', 'IS210', 'Elective'),
        ('S008', 'DS310', 'Core'),
        ('S008', 'SE201', 'Core'),
        ('S008', 'CS101', 'Elective'),
        ('S009', 'CY220', 'Core'),
        ('S009', 'CS202', 'Core'),
        ('S009', 'IS210', 'Elective'),
        ('S010', 'SE201', 'Core'),
        ('S010', 'DS310', 'Core'),
        ('S010', 'CS101', 'Elective')
    ]

    c.executemany(
        'INSERT OR IGNORE INTO student_enrollments (student_id, course_code, study_mode) VALUES (?,?,?)',
        student_enrollments
    )

    announcements = [
        ('Midterm Timetable Released', 'All Students', 'The Spring 2026 midterm timetable is now available in the portal.', 'HIGH'),
        ('Fee Clearance Reminder', 'Finance Desk', 'Please clear partial fee accounts before the semester deadline.', 'MEDIUM'),
        ('Faculty Review Week', 'Faculty', 'Department coordinators will review attendance and lab submissions this week.', 'MEDIUM'),
        ('Security Drill Scheduled', 'Admin', 'The security lab demo will run for integration testing on Friday.', 'LOW')
    ]

    c.executemany(
        'INSERT OR IGNORE INTO announcements (title, audience, body, priority) VALUES (?,?,?,?)',
        announcements
    )

    policies = [
        ('HMAC Payload Integrity', 'ENABLED', 'HMAC-SHA256 signature with 30s freshness window.'),
        ('API Key Gate', 'ENABLED', 'Validates LMS API keys for service-to-service traffic.'),
        ('Role-Based Access', 'ENABLED', 'Scopes access by role: student, faculty, registrar.'),
        ('IP Allowlist', 'ENABLED', 'Restricts LMS traffic to approved campus IP ranges.'),
        ('Rate Limiting', 'READY', 'Protects endpoints from abuse and scraping.'),
        ('Audit Logging', 'ENABLED', 'Captures endpoint, status, client IP, timestamp.'),
    ]

    c.executemany(
        'INSERT OR IGNORE INTO security_policies (name, status, details) VALUES (?,?,?)',
        policies
    )

    conn.commit()
    conn.close()
    _db_initialized = True
    print('[DB] Student database ready with seeded records')

def get_student(student_id):
    """Retrieve a student record by ID. Returns dict or None."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_students():
    """Retrieve all students with academic summary fields."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT
            s.id,
            s.name,
            s.course,
            s.grade,
            s.marks,
            s.gpa,
            p.semester,
            p.advisor,
            p.track,
            p.status AS academic_status,
            a.percentage AS attendance_percentage,
            f.status AS fee_status
        FROM students s
        LEFT JOIN student_profiles p ON p.student_id = s.id
        LEFT JOIN attendance_records a ON a.student_id = s.id
        LEFT JOIN fee_accounts f ON f.student_id = s.id
        ORDER BY s.id
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_student_profile(student_id):
    """Retrieve a full student profile with related records."""
    student = get_student(student_id)
    if not student:
        return None

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT * FROM student_profiles WHERE student_id = ?', (student_id,))
    profile_row = c.fetchone()

    c.execute('SELECT * FROM attendance_records WHERE student_id = ?', (student_id,))
    attendance_row = c.fetchone()

    c.execute('SELECT * FROM fee_accounts WHERE student_id = ?', (student_id,))
    fee_row = c.fetchone()

    c.execute('''
        SELECT
            e.course_code,
            c.title,
            d.name AS department,
            COALESCE(cd.credits, 3) AS credits,
            COALESCE(cd.instructor, 'TBA') AS instructor,
            cd.schedule,
            e.study_mode
        FROM student_enrollments e
        LEFT JOIN courses c ON c.code = e.course_code
        LEFT JOIN departments d ON d.id = c.department_id
        LEFT JOIN course_details cd ON cd.course_code = e.course_code
        WHERE e.student_id = ?
        GROUP BY e.student_id, e.course_code, e.study_mode
        ORDER BY e.course_code
    ''', (student_id,))
    enrolled_courses = [dict(row) for row in c.fetchall()]

    conn.close()

    profile = dict(student)
    if profile_row:
        profile.update({
            'semester': profile_row['semester'],
            'advisor': profile_row['advisor'],
            'track': profile_row['track'],
            'campus': profile_row['campus'],
            'status': profile_row['status']
        })
    if attendance_row:
        profile['attendance'] = dict(attendance_row)
    else:
        profile['attendance'] = None
    if fee_row:
        profile['fee_account'] = dict(fee_row)
    else:
        profile['fee_account'] = None

    profile['enrolled_courses'] = enrolled_courses
    return profile

def get_courses():
    """Retrieve the full course catalog."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT
            c.code,
            c.title,
            d.name AS department,
            cd.credits,
            cd.instructor,
            cd.schedule,
            cd.room
        FROM courses c
        LEFT JOIN departments d ON d.id = c.department_id
        LEFT JOIN course_details cd ON cd.course_code = c.code
        ORDER BY c.code
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_faculty():
    """Retrieve faculty members with department labels."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT
            f.id,
            f.full_name,
            f.title,
            f.email,
            f.office,
            d.name AS department
        FROM faculty f
        LEFT JOIN departments d ON d.id = f.department_id
        ORDER BY f.id
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_attendance_records():
    """Retrieve attendance records with student names."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT
            a.student_id,
            s.name,
            a.semester,
            a.present_classes,
            a.total_classes,
            a.percentage,
            a.trend
        FROM attendance_records a
        LEFT JOIN students s ON s.id = a.student_id
        ORDER BY a.student_id
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_fee_accounts():
    """Retrieve fee ledger entries with student names."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT
            f.student_id,
            s.name,
            f.semester,
            f.total_fee,
            f.paid_amount,
            f.due_amount,
            f.status,
            f.due_date
        FROM fee_accounts f
        LEFT JOIN students s ON s.id = f.student_id
        ORDER BY f.student_id
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_announcements():
    """Retrieve campus announcements."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT id, title, audience, body, priority, created_at
        FROM announcements
        ORDER BY
            CASE priority
                WHEN 'HIGH' THEN 1
                WHEN 'MEDIUM' THEN 2
                ELSE 3
            END,
            id DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_route_catalog():
    """Return the route catalog used by the attacker visibility screens."""
    return list(ROUTE_CATALOG)

def get_module_overview():
    """Return module cards with live counts."""
    dashboard = get_dashboard_data()
    return [
        {
            'key': 'student-records',
            'label': 'Student Records',
            'description': 'Profiles, grades, attendance, and academic standing.',
            'metric': dashboard['total_students'],
            'metric_label': 'students'
        },
        {
            'key': 'academic-ops',
            'label': 'Academic Operations',
            'description': 'Courses, faculty, and departmental structure.',
            'metric': f"{dashboard['total_courses']} / {dashboard['total_faculty']}",
            'metric_label': 'courses / faculty'
        },
        {
            'key': 'finance-desk',
            'label': 'Finance Desk',
            'description': 'Term fees, dues, and payment collection health.',
            'metric': f"{dashboard['fee_collection_rate']}%",
            'metric_label': 'collection'
        },
        {
            'key': 'security-center',
            'label': 'Security Center',
            'description': 'Policies, logs, discovery, and payload integrity controls.',
            'metric': len(dashboard['security_policies']),
            'metric_label': 'policies'
        }
    ]

def get_user_by_email(email):
    """Retrieve a user by email. Returns dict or None."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id):
    """Retrieve a user by ID. Returns dict or None."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(email, full_name, password_hash, role='student'):
    """Create a new user record. Returns new user id."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        'INSERT INTO users (email, full_name, role, password_hash) VALUES (?,?,?,?)',
        (email, full_name, role, password_hash)
    )
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    return user_id

def get_users():
    """Retrieve all users. Returns list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT id, email, full_name, role, created_at FROM users ORDER BY id')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_user_role(user_id, role):
    """Update a user's role. Returns updated user dict or None."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('UPDATE users SET role = ? WHERE id = ?', (role, user_id))
    conn.commit()
    c.execute('SELECT id, email, full_name, role, created_at FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def log_api_event(endpoint, method, status, student_id=None, client_ip=None):
    """Persist a basic API audit log entry."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        'INSERT INTO api_logs (endpoint, method, status, student_id, client_ip) VALUES (?,?,?,?,?)',
        (endpoint, method, status, student_id, client_ip)
    )
    conn.commit()
    conn.close()

def get_dashboard_data():
    """Return dashboard analytics and security policy summaries."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT COUNT(*) AS total FROM students')
    total_students = c.fetchone()['total']

    c.execute('SELECT COUNT(*) AS total FROM faculty')
    total_faculty = c.fetchone()['total']

    c.execute('SELECT COUNT(*) AS total FROM courses')
    total_courses = c.fetchone()['total']

    c.execute('SELECT COUNT(*) AS total FROM departments')
    total_departments = c.fetchone()['total']

    c.execute('SELECT ROUND(AVG(gpa), 2) AS avg_gpa FROM students')
    avg_gpa = c.fetchone()['avg_gpa'] or 0

    c.execute('SELECT ROUND(AVG(percentage), 2) AS avg_attendance FROM attendance_records')
    avg_attendance = c.fetchone()['avg_attendance'] or 0

    c.execute('SELECT SUM(total_fee) AS total_fee, SUM(paid_amount) AS paid_amount FROM fee_accounts')
    fee_totals = c.fetchone()
    total_fee = fee_totals['total_fee'] or 0
    paid_amount = fee_totals['paid_amount'] or 0
    fee_collection_rate = round((paid_amount / total_fee) * 100, 2) if total_fee else 0

    c.execute('SELECT grade, COUNT(*) AS count FROM students GROUP BY grade ORDER BY grade')
    grade_distribution = [dict(row) for row in c.fetchall()]

    c.execute('''SELECT course, COUNT(*) AS count, ROUND(AVG(gpa), 2) AS avg_gpa
                 FROM students GROUP BY course ORDER BY count DESC''')
    course_metrics = [dict(row) for row in c.fetchall()]

    c.execute('''SELECT d.name AS department, COUNT(*) AS count
                 FROM courses c
                 LEFT JOIN departments d ON d.id = c.department_id
                 GROUP BY d.name
                 ORDER BY count DESC, department ASC''')
    department_breakdown = [dict(row) for row in c.fetchall()]

    c.execute('SELECT status, COUNT(*) AS count FROM fee_accounts GROUP BY status ORDER BY count DESC')
    fee_status_breakdown = [dict(row) for row in c.fetchall()]

    c.execute('SELECT COUNT(*) AS total FROM api_logs')
    total_requests = c.fetchone()['total']

    c.execute('''SELECT endpoint, method, status, student_id, client_ip, created_at
                 FROM api_logs ORDER BY id DESC LIMIT 8''')
    recent_logs = [dict(row) for row in c.fetchall()]

    c.execute('SELECT id, name, status, details FROM security_policies ORDER BY id')
    policies = [dict(row) for row in c.fetchall()]

    c.execute('SELECT id, title, audience, body, priority, created_at FROM announcements ORDER BY id DESC LIMIT 4')
    announcements = [dict(row) for row in c.fetchall()]

    c.execute('''
        SELECT s.id, s.name, COALESCE(a.percentage, 0) AS attendance_percentage, COALESCE(f.status, 'UNKNOWN') AS fee_status
        FROM students s
        LEFT JOIN attendance_records a ON a.student_id = s.id
        LEFT JOIN fee_accounts f ON f.student_id = s.id
        ORDER BY s.id
    ''')
    student_health = [dict(row) for row in c.fetchall()]

    conn.close()
    return {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_courses': total_courses,
        'total_departments': total_departments,
        'avg_gpa': avg_gpa,
        'avg_attendance': avg_attendance,
        'fee_collection_rate': fee_collection_rate,
        'grade_distribution': grade_distribution,
        'course_metrics': course_metrics,
        'department_breakdown': department_breakdown,
        'fee_status_breakdown': fee_status_breakdown,
        'student_health': student_health,
        'total_requests': total_requests,
        'recent_logs': recent_logs,
        'security_policies': policies,
        'announcements': announcements,
        'module_catalog': MODULE_CATALOG,
        'route_catalog': ROUTE_CATALOG
    }

def get_policies():
    """Retrieve all security policies. Returns list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT id, name, status, details FROM security_policies ORDER BY id')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_policy_status(policy_id, status):
    """Update policy status. Returns updated policy dict or None."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('UPDATE security_policies SET status = ? WHERE id = ?', (status, policy_id))
    conn.commit()
    c.execute('SELECT id, name, status, details FROM security_policies WHERE id = ?', (policy_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None
