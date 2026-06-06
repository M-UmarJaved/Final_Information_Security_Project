**Submitted**

**To:**

Sir Kamran

**Submitted By:**

Muhammad Umar Javed (2024-CS-190)

Muhammad Husnain (2024-CS-221)

Sunil Romi (2024-CS-55)

Abdullah Saif (2024-CS-194)

Muhammad Amir (2024-CS-183)

**Course:**

Information Security Lab

**Project Title:**

UniShield Academy - API Payload Interception and Security Middleware System

**DEPARTMENT OF COMPUTER SCIENCE**

# Table of Contents

1. INTRODUCTION ........................................................................................................ 1

   1.1 Introduction ...................................................................................................... 1

   1.2 Problem Statement ............................................................................................ 2

   1.3 Objectives ......................................................................................................... 2

   1.4 Scope ................................................................................................................ 3

2. BACKGROUND AND SECURITY CONCEPTS ....................................................... 4

   2.1 API Payload Tampering ..................................................................................... 4

   2.2 Man-in-the-Middle Attack ................................................................................. 4

   2.3 HMAC-SHA256 ................................................................................................. 5

   2.4 Replay Protection .............................................................................................. 5

3. SYSTEM OVERVIEW ............................................................................................... 6

   3.1 Project Theme ................................................................................................... 6

   3.2 System Architecture .......................................................................................... 6

   3.3 Technology Stack .............................................................................................. 8

4. SCHOOL MANAGEMENT SYSTEM MODULES .................................................... 9

   4.1 Student Portal .................................................................................................... 9

   4.2 Admin Dashboard ............................................................................................ 10

   4.3 User Management ............................................................................................ 10

   4.4 Security Policy Management ........................................................................... 11

   4.5 Academic and Financial Records ..................................................................... 11

5. DATABASE DESIGN .............................................................................................. 12

   5.1 Database Overview .......................................................................................... 12

   5.2 Main Tables ..................................................................................................... 12

   5.3 Seeded Demonstration Data ............................................................................ 13

6. UNSECURED MODE AND ATTACK DEMONSTRATION ................................... 14

   6.1 Unsecured API Flow ........................................................................................ 14

   6.2 Kali Linux Interception Setup .......................................................................... 15

   6.3 Student-Side Payload Attack ........................................................................... 16

   6.4 Admin-Side Payload Attack ............................................................................ 17

7. SECURE MIDDLEWARE DESIGN ......................................................................... 18

   7.1 Middleware Purpose ......................................................................................... 18

   7.2 Request Signing ............................................................................................... 18

   7.3 Server-Side Verification .................................................................................. 19

   7.4 Response Signing ............................................................................................ 20

   7.5 Authentication and Authorization .................................................................... 20

8. IMPLEMENTATION DETAILS .............................................................................. 22

   8.1 Backend Implementation .................................................................................. 22

   8.2 Frontend Implementation ................................................................................. 23

   8.3 Attacker-Side Script ........................................................................................ 24

   8.4 Network Configuration .................................................................................... 25

9. TESTING AND EVALUATION ............................................................................... 26

   9.1 Test Environment ............................................................................................. 26

   9.2 Test Cases ........................................................................................................ 26

   9.3 Evaluation Results ........................................................................................... 28

10. RESULTS AND DISCUSSION .............................................................................. 29

11. CHALLENGES AND SOLUTIONS ....................................................................... 31

12. LIMITATIONS ....................................................................................................... 33

13. FUTURE ENHANCEMENTS ................................................................................. 34

14. CONCLUSION ....................................................................................................... 35

15. REFERENCES ........................................................................................................ 36

# 1. INTRODUCTION

## 1.1 Introduction

Application Programming Interfaces (APIs) are widely used in modern web applications to transfer data between frontend interfaces, backend services, and databases. A school management system, for example, depends on APIs to retrieve student profiles, academic grades, attendance records, fee details, administrative users, and dashboard analytics. Because this data is sensitive, the integrity of API payloads is very important.

This Information Security Lab project, titled **UniShield Academy - API Payload Interception and Security Middleware System**, demonstrates how an attacker can intercept and modify API payloads in an unsecured environment and how a security middleware can detect and block such tampering. For evaluation, a complete school management system was developed by the team. The system behaves like a company management application that has purchased a middleware service to secure its API communication.

The project is divided into two major phases:

1. **Unsecured Mode:** The school management system sends normal API requests to the backend database. An attacker using Kali Linux and mitmproxy can intercept the request or response, modify JSON payload values, and allow the altered data to continue toward the server or frontend.

2. **Secured Mode:** The same system uses a custom HMAC-based middleware. The frontend signs each request payload, the backend verifies the signature before processing, and the response is also signed. If an attacker changes any value in transit, the signature verification fails and the server blocks the request.

This project therefore provides a practical demonstration of payload integrity, API tampering, secure middleware design, and real-world attack simulation.

## 1.2 Problem Statement

Many web applications trust that API requests received by the backend are the same requests sent by the frontend. In an unsecured environment, this assumption can be dangerous. If traffic is routed through a proxy or captured by an attacker, request payloads and response data may be changed before reaching their destination.

In the school management system scenario, an attacker can change a student ID inside the request body and retrieve another student's data. The attacker can also modify the response before it reaches the frontend, for example changing a grade from `A` to `A+` or marks from `92` to `100`. The company using the application may not immediately realize that the data was altered during transmission because the API still returns a valid-looking response.

The main problem addressed by this project is:

**How can a middleware layer protect API payloads from unauthorized modification during transmission and prove that the received payload is exactly the one sent by the authorized client?**

## 1.3 Objectives

The main objectives of this project are:

- To build a realistic school management system with multiple working modules.
- To demonstrate unsecured API communication where JSON request and response payloads can be intercepted.
- To perform controlled payload tampering from Kali Linux using mitmproxy.
- To show both student-side and admin-side attack scenarios.
- To implement a custom security middleware using HMAC-SHA256.
- To verify request integrity on the backend before database access.
- To sign server responses and show tamper-free results on the frontend.
- To provide a professional frontend interface for project demonstration and evaluation.
- To compare unsecured and secured modes clearly during the lab presentation.

## 1.4 Scope

The scope of this project includes:

- A frontend school management website with landing, login, signup, student portal, admin panel, and dashboard pages.
- A backend Flask API in two modes: unsecured and secured.
- A SQLite database with seeded school data.
- Student records, course details, attendance, fee accounts, faculty information, users, policies, announcements, and API logs.
- Kali Linux attack demonstration using mitmproxy and a custom interception script.
- HMAC-SHA256 based request and response signing.
- Authentication and role-based admin access in secured mode.
- Practical testing of payload tampering and middleware defense.

This project focuses mainly on payload integrity. It does not claim to replace HTTPS/TLS encryption. HMAC protects against unauthorized modification, while confidentiality of traffic still requires encrypted transport such as HTTPS.

# 2. BACKGROUND AND SECURITY CONCEPTS

## 2.1 API Payload Tampering

API payload tampering is an attack in which an attacker modifies the data being sent between a client and a server. In JSON-based APIs, payloads commonly contain parameters such as `student_id`, `role`, `grade`, `marks`, or `policy_status`. If these values are not protected, an attacker may change them before they reach the backend.

Example unsecured request:

```json
{
  "student_id": "S006"
}
```

Modified attacker request:

```json
{
  "student_id": "S002"
}
```

In this case, the frontend expects data for student `S006`, but the backend receives `S002` and returns the wrong record. This creates a serious data integrity and privacy issue.

## 2.2 Man-in-the-Middle Attack

A Man-in-the-Middle (MITM) attack occurs when an attacker positions themselves between the client and server. The attacker can observe traffic and, in vulnerable setups, modify requests or responses.

In this project, the attack is performed in a controlled lab environment using:

- Kali Linux as the attacker machine.
- mitmproxy or mitmweb as the interception proxy.
- ZeroOmega browser extension to route Chrome traffic through Kali.
- A custom script named `intercept_grade.py` to hold and modify selected API flows.

The attack is not performed on any real external system. It is limited to the local lab project for educational and evaluation purposes.

## 2.3 HMAC-SHA256

HMAC stands for Hash-based Message Authentication Code. It combines a secret key with a cryptographic hash function to produce a signature for a message. In this project, the middleware uses HMAC with SHA-256.

The basic idea is:

1. The frontend creates a JSON payload.
2. A timestamp is added to the payload.
3. The payload is serialized in a consistent format.
4. HMAC-SHA256 generates a signature using a shared secret key.
5. The signature is sent with the payload.
6. The backend recomputes the signature and compares it with the received signature.

If even one character in the payload is changed, the signature changes. Therefore, tampering can be detected.

## 2.4 Replay Protection

Replay attacks occur when an attacker captures a valid request and sends it again later. To reduce this risk, the secured middleware includes a timestamp inside each signed payload. The backend accepts only requests within a short time window.

In this project, the middleware checks that:

- The timestamp exists.
- The timestamp is numeric.
- The timestamp is not older than the allowed replay window.
- The signature matches the exact payload.

This prevents attackers from reusing old signed requests after the allowed time has passed.

# 3. SYSTEM OVERVIEW

## 3.1 Project Theme

The project is based on a realistic business scenario:

A company is using a school management system. The school system communicates with a database through APIs. In the beginning, the company does not use any API security middleware, so an attacker can intercept and change payloads. The company receives responses from the API, but the information may be false because the attacker modified it during transmission.

Later, the company purchases and integrates our security middleware. After middleware integration, each API request is signed and verified. If an attacker modifies the request or response payload, the system detects the change and blocks the operation.

This theme makes the project easy to evaluate because the teacher can clearly see:

- What happens before security is applied.
- How the attacker changes data.
- What changes after middleware is enabled.
- Why the middleware improves API integrity.

## 3.2 System Architecture

The system contains four major components:

1. Frontend school management website.
2. Flask backend API.
3. SQLite database.
4. Kali Linux attacker proxy.

### Unsecured Mode Architecture

```text
Browser Frontend
      |
      | Normal JSON API Request
      v
Kali mitmproxy
      |
      | Modified JSON Payload
      v
Unsecured Flask API
      |
      v
SQLite Database
      |
      | API Response
      v
Kali mitmproxy
      |
      | Modified Response
      v
Browser Frontend
```

In unsecured mode, the attacker can hold the request, edit JSON values, resume the flow, and send false data to the server or frontend.

### Secured Mode Architecture

```text
Browser Frontend
      |
      | Signed JSON Payload
      v
Kali mitmproxy
      |
      | Any Modification Breaks Signature
      v
Secured Flask API + Middleware
      |
      | Verify HMAC Signature
      v
SQLite Database
      |
      | Signed Response
      v
Browser Frontend
```

In secured mode, the middleware verifies payload integrity before the backend reads from the database. If the attacker changes any field, the server returns an integrity violation response.

## 3.3 Technology Stack

| Layer | Technology Used | Purpose |
|---|---|---|
| Frontend | HTML, CSS, JavaScript | Professional school management interface |
| Backend | Python Flask | REST API implementation |
| Database | SQLite | Local school management database |
| Security Middleware | HMAC-SHA256 | Payload signing and verification |
| Attack Tool | Kali Linux | Attacker environment |
| Proxy Tool | mitmproxy / mitmweb | API interception and modification |
| Browser Proxy | ZeroOmega | Routes Chrome traffic through Kali |
| Development Environment | VS Code | Running frontend and backend servers |

# 4. SCHOOL MANAGEMENT SYSTEM MODULES

## 4.1 Student Portal

The student portal is the main demonstration page for the payload attack and secured middleware. It allows the user to select a student and fetch the student record from the backend API.

The student record includes:

- Student ID
- Name
- Course
- Semester
- Track
- Grade
- Marks
- GPA
- Advisor
- Attendance
- Fee account
- Enrolled courses
- Security status

In unsecured mode, the attacker can change the selected student ID in the API request. The frontend may believe it requested one student, but the backend returns another student's record because the payload was modified.

In secured mode, the same request contains a signature and timestamp. If the attacker changes the student ID, the backend detects the mismatch and blocks the request.

## 4.2 Admin Dashboard

The dashboard provides a high-level view of school data. It contains summary statistics and operational information such as:

- Total students
- Total faculty
- Total courses
- Average GPA
- Average attendance
- Fee collection
- Grade distribution
- Security policy status
- Recent API logs
- Announcements

This module helps demonstrate that the system is not only a single API page, but a complete school management environment.

## 4.3 User Management

The user management module allows admin-side operations. It includes administrative users and student users. In unsecured mode, admin-related API payloads can also be intercepted and modified.

Example admin-side attack possibilities:

- Changing a user's role.
- Modifying account status.
- Updating admin-related payload values.

In secured mode, admin operations require authentication, authorization, and signed payload verification.

## 4.4 Security Policy Management

The security policy module contains policies used by the system to explain and demonstrate security controls. Example policies include:

- Payload integrity verification.
- Replay protection.
- Admin access control.
- API logging.
- Response signing.

In the secured API, policy changes are protected by signed payloads and admin authorization.

## 4.5 Academic and Financial Records

The school management system includes academic and financial data to make the demonstration realistic. The database stores:

- Course details
- Faculty records
- Student enrollments
- Attendance records
- Fee accounts
- Announcements

This makes the API payload meaningful during testing. Instead of dummy values, the system shows structured academic data that looks like a real institution management system.

# 5. DATABASE DESIGN

## 5.1 Database Overview

The project uses SQLite as the database engine. SQLite is lightweight, easy to run locally, and suitable for lab-based demonstrations. The database is automatically created and populated using the project seed functions.

The database stores complete school management information and supports both unsecured and secured backend modes.

## 5.2 Main Tables

| Table Name | Purpose |
|---|---|
| `students` | Stores student academic records such as marks, grade, GPA, course, and status |
| `departments` | Stores department names and campus information |
| `courses` | Stores course codes, course titles, credits, instructors, and schedules |
| `faculty` | Stores faculty profile information |
| `student_profiles` | Stores extended student information |
| `attendance_records` | Stores attendance percentage and class count |
| `fee_accounts` | Stores fee amount, paid amount, due amount, and fee status |
| `student_enrollments` | Links students with enrolled courses |
| `announcements` | Stores dashboard announcements |
| `users` | Stores login users and roles |
| `auth_tokens` | Stores authentication tokens for secured sessions |
| `security_policies` | Stores middleware and security policy settings |
| `api_logs` | Stores API activity and security event logs |

## 5.3 Seeded Demonstration Data

The database includes seeded records so the project can be demonstrated immediately after setup. It includes:

- 10 student profiles.
- Multiple academic courses.
- Faculty advisors and instructors.
- Attendance records for the current semester.
- Fee records with paid and due statuses.
- Admin and student users.
- Security policies.
- Dashboard announcements.

This seeded data allows the teacher to test different students, dashboards, and admin operations without manually entering data first.

# 6. UNSECURED MODE AND ATTACK DEMONSTRATION

## 6.1 Unsecured API Flow

In unsecured mode, the backend API accepts normal JSON payloads. The request does not include any cryptographic signature. The backend trusts whatever payload it receives.

Example unsecured API request:

```http
POST /api/student
Content-Type: application/json

{
  "student_id": "S006"
}
```

If this request is intercepted, the attacker can change `S006` to `S002`. The backend receives the modified request and returns the record for `S002`.

The unsecured API is intentionally vulnerable for demonstration purposes. It helps show why middleware protection is necessary.

## 6.2 Kali Linux Interception Setup

The attacker machine runs Kali Linux. The browser traffic from Windows is routed through Kali using a proxy.

### Lab Network Values

| Machine | IP Address | Purpose |
|---|---|---|
| Windows Host | `10.5.154.161` | Runs frontend and backend |
| VMware NAT Adapter | `192.168.191.1` | Host-side VMware network |
| Kali Linux | `192.168.191.129` | Attacker proxy machine |
| Frontend Port | `5500` | Static HTML server |
| Backend Port | `5000` | Flask API server |
| Proxy Port | `8080` | mitmproxy listener |

### Attack Proxy Command

```bash
mitmweb -s intercept_grade.py --listen-host 0.0.0.0 --listen-port 8080
```

or:

```bash
mitmdump -s intercept_grade.py --listen-host 0.0.0.0 --listen-port 8080
```

Chrome is configured through ZeroOmega:

- Proxy scheme: HTTP
- Server: `192.168.191.129`
- Port: `8080`

After this setup, API calls from the browser pass through Kali, where the attacker can view, hold, edit, and resume selected flows.

## 6.3 Student-Side Payload Attack

The student-side attack demonstrates request tampering and response tampering.

### Request Tampering

Original request:

```json
{
  "student_id": "S006"
}
```

Attacker-modified request:

```json
{
  "student_id": "S002"
}
```

Result:

- Frontend expects student `S006`.
- Backend receives student `S002`.
- Database returns data for `S002`.
- Frontend displays incorrect student information.

### Response Tampering

Original response values:

```json
{
  "grade": "A",
  "marks": 92
}
```

Attacker-modified response:

```json
{
  "grade": "A+",
  "marks": 100
}
```

Result:

- The server may return correct data.
- The attacker changes the response before it reaches the browser.
- The frontend displays false academic results.

This clearly proves that the unsecured system cannot guarantee data integrity.

## 6.4 Admin-Side Payload Attack

The admin-side attack demonstrates that administrative APIs are also dangerous if payloads are not protected.

Possible admin API targets include:

| API Route | Attack Demonstration |
|---|---|
| `/api/admin/users` | Modify role, status, or user values |
| `/api/admin/policies` | Modify security policy fields |
| `/api/dashboard` | Modify dashboard statistics or analytics |

In unsecured mode, these APIs can be intercepted and modified in the same way as the student portal API. This proves that the issue is not limited to student data only. Any management API can be manipulated if the payload is not protected.

# 7. SECURE MIDDLEWARE DESIGN

## 7.1 Middleware Purpose

The security middleware is the core contribution of this project. Its purpose is to protect API payload integrity between the frontend and backend.

The middleware ensures that:

- The payload was created by an authorized client.
- The payload was not changed during transmission.
- The request is not too old.
- The backend does not process tampered data.
- Sensitive admin operations require authentication and authorization.

## 7.2 Request Signing

In secured mode, the frontend signs the request before sending it to the backend.

The signing process is:

1. Create the JSON payload.
2. Add a timestamp.
3. Serialize the payload in a stable format.
4. Generate HMAC-SHA256 signature using the shared secret key.
5. Attach the signature to the request.
6. Send the signed payload to the backend.

Example signed payload:

```json
{
  "student_id": "S001",
  "timestamp": 1780064767,
  "signature": "7785e9a5fc9e2c9904d8663c9fad29bc6b7a724f2175f28787a755f174018b38"
}
```

If an attacker changes `student_id`, the old signature no longer matches the new payload.

## 7.3 Server-Side Verification

The backend middleware verifies the signed payload before processing the API request.

Verification checks include:

- Payload must be a JSON object.
- `signature` field must exist.
- `timestamp` field must exist.
- Signature must be a valid 64-character hexadecimal HMAC.
- Timestamp must be inside the allowed time window.
- Recomputed signature must match the received signature.

If verification fails, the backend returns an error and does not read from the database.

Example blocked response:

```json
{
  "error": "PAYLOAD INTEGRITY VIOLATION",
  "message": "Signature mismatch - payload was tampered"
}
```

This proves that the middleware prevents unauthorized payload modification.

## 7.4 Response Signing

The secured backend also signs response payloads. This allows the frontend to identify that the response was produced by the trusted server.

Response signing helps demonstrate:

- The server is returning a verified payload.
- The response can be marked as tamper-free.
- Any response modification can be detected by signature comparison.

The frontend displays security messages such as:

- `PAYLOAD VERIFIED - TAMPER FREE`
- `Signature mismatch - payload was tampered`

## 7.5 Authentication and Authorization

The secured mode includes authentication features for login and signup. After successful login, the backend issues an auth token or uses a server-side session. Protected routes check the user identity before allowing access.

Admin operations require:

- Valid login session or token.
- Admin role.
- Signed request payload.
- Valid source configuration.

This adds another security layer beyond payload integrity.

# 8. IMPLEMENTATION DETAILS

## 8.1 Backend Implementation

The backend is implemented in Python Flask. The project contains two backend files:

| File | Purpose |
|---|---|
| `app_unsecured.py` | Demonstrates vulnerable API behavior |
| `app_secured.py` | Implements protected API behavior with middleware |

The unsecured backend accepts normal JSON payloads. It is used for the first phase of the demonstration.

The secured backend uses the middleware to verify payloads before processing. It also applies security headers, authentication checks, and protected admin controls.

Important secured API routes include:

| Route | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Checks backend mode and status |
| `/api/auth/signup` | POST | Creates secured user account |
| `/api/auth/login` | POST | Authenticates user |
| `/api/auth/me` | GET | Checks current logged-in user |
| `/api/student` | POST | Fetches signed student record |
| `/api/students` | GET | Lists students |
| `/api/dashboard` | GET | Shows dashboard analytics |
| `/api/admin/users` | GET/POST | Manages users |
| `/api/admin/policies` | GET/POST | Manages security policies |

## 8.2 Frontend Implementation

The frontend is built using HTML, CSS, and JavaScript. Each page has its own CSS and JS file to make UI customization easier.

Main frontend pages include:

| Page | Purpose |
|---|---|
| `landing.html` | Project introduction and navigation |
| `login.html` | User login |
| `signup.html` | User registration |
| `student_portal.html` | Student API demonstration |
| `dashboard.html` | School analytics dashboard |
| `admin.html` | Admin controls and policy management |

The UI was designed as a professional website rather than simple dummy pages. It includes:

- Consistent navigation bar.
- Branded colors.
- Dashboard cards.
- Smooth responsive layouts.
- Security status panels.
- Request console.
- Student record detail card.
- Admin and dashboard modules.

In secured mode, the frontend uses the Web Crypto API to generate HMAC signatures before sending payloads.

## 8.3 Attacker-Side Script

The attacker-side script is named `intercept_grade.py`. It runs inside mitmproxy or mitmweb and intercepts selected API routes.

The script targets routes such as:

- `/api/student`
- `/api/admin/users`
- `/api/admin/policies`
- `/api/dashboard`

When a matching request or response is captured, the script:

1. Prints the request or response in formatted JSON.
2. Holds the API flow.
3. Allows the attacker to edit the payload manually.
4. Resumes the request after editing.
5. Sends the modified data forward.

This creates a realistic hacking-style demonstration for the evaluation.

## 8.4 Network Configuration

The system is configured for a Windows host and Kali Linux virtual machine.

### Windows Host

The Windows machine runs:

- Flask backend on port `5000`.
- Static frontend server on port `5500`.
- Browser with ZeroOmega proxy extension.

### Kali Linux

Kali runs:

- mitmproxy or mitmweb on port `8080`.
- Custom interception script.

### Browser Proxy

ZeroOmega routes traffic through Kali:

```text
Proxy Server: 192.168.191.129
Proxy Port: 8080
Protocol: HTTP
```

When testing without attack, the proxy can be disabled. When testing unsecured attack mode, the proxy is enabled and the Kali interception tool is running.

# 9. TESTING AND EVALUATION

## 9.1 Test Environment

The project was tested in the following environment:

| Component | Configuration |
|---|---|
| Host OS | Windows |
| Attacker OS | Kali Linux |
| Backend | Python Flask |
| Database | SQLite |
| Frontend Server | Python HTTP server on port `5500` |
| API Server | Flask on port `5000` |
| Proxy | mitmproxy / mitmweb on port `8080` |
| Browser | Google Chrome |
| Proxy Extension | ZeroOmega |

## 9.2 Test Cases

| Test Case | Mode | Expected Result | Actual Result |
|---|---|---|---|
| Fetch student without attacker | Unsecured | Student record loads normally | Passed |
| Intercept student request | Unsecured | Request appears in Kali | Passed |
| Change `student_id` request value | Unsecured | Different student data is returned | Passed |
| Change grade in response | Unsecured | Frontend shows modified grade | Passed |
| Intercept admin route | Unsecured | Admin API payload is visible | Passed |
| Login with valid account | Secured | User is authenticated | Passed |
| Fetch signed student payload | Secured | Record loads for authorized frontend | Passed |
| Modify signed student payload | Secured | Backend blocks request | Passed |
| Replay old signed payload | Secured | Backend rejects old timestamp | Passed |
| Access admin controls without role | Secured | Access denied | Passed |

## 9.3 Evaluation Results

The evaluation clearly shows the difference between both modes:

| Feature | Unsecured Mode | Secured Mode |
|---|---|---|
| Request visibility in proxy | Visible | Visible in lab HTTP setup, but tamper-protected |
| Request modification | Possible | Blocked by HMAC mismatch |
| Response modification | Possible | Detectable by signed response |
| Student ID tampering | Successful | Blocked |
| Grade tampering | Successful | Detected |
| Admin payload tampering | Possible | Blocked with authentication and signing |
| Replay protection | Not available | Timestamp window applied |
| Data integrity | Not guaranteed | Guaranteed if secret key remains safe |

The secured middleware successfully prevents the attacker from changing API payloads without detection.

# 10. RESULTS AND DISCUSSION

The project successfully demonstrates the complete lifecycle of an API payload attack and its defense.

In unsecured mode, the attacker can intercept API traffic through Kali Linux. The attacker can hold a request, change JSON values, and then resume the flow. The backend processes the modified request because it has no way to know that the payload was changed. The attacker can also modify the response before it reaches the browser. This makes the frontend display false information while still looking normal to the user.

The student-side attack is especially effective for demonstration. When the frontend sends a request for one student, the attacker changes the `student_id` and the backend returns another student's record. This shows a direct integrity failure. Similarly, changing a grade or marks value in the response proves that even correct backend data can be falsified before reaching the user.

In secured mode, the middleware changes the behavior completely. Every important request includes a timestamp and HMAC signature. The backend recalculates the signature using the same secret key. If the attacker changes even one field, the recalculated signature does not match the received signature. The backend then rejects the request before database access.

This result proves that middleware-based integrity verification is an effective defense against payload tampering. The project also shows that security should not depend only on frontend validation. The final decision must be made on the backend because the backend controls access to the database.

# 11. CHALLENGES AND SOLUTIONS

## 11.1 Proxy and Certificate Configuration

One challenge was routing browser traffic through Kali Linux. Initially, Chrome traffic showed certificate trust errors. This was resolved by installing the mitmproxy certificate from `http://mitm.it` and configuring ZeroOmega correctly.

## 11.2 Correct IP Address Selection

The lab network changed when the system moved between university Wi-Fi, mobile hotspot, and VMware NAT. The solution was to identify the correct Windows host IP and Kali IP and update the configuration accordingly.

## 11.3 CORS and Authentication Issues

During testing, some browser requests were blocked by CORS or returned `401 Unauthorized`. The secured backend was updated to support proper authentication routes and allowed origins. The unsecured backend was also given lightweight auth compatibility routes so the frontend could run smoothly during unsecured demonstrations.

## 11.4 Maintaining Two Modes

Another challenge was keeping unsecured and secured modes separate. If the frontend expected secured behavior while the unsecured backend was running, requests could fail. This was handled by health checks and mode detection in the frontend.

## 11.5 UI Consistency

The project required a professional interface for evaluation. Multiple pages were updated to use consistent colors, fonts, spacing, cards, and navigation patterns. This made the system look like a complete management application rather than a simple API demo.

# 12. LIMITATIONS

The project has some limitations:

- The lab uses HTTP for easier interception and demonstration. In real production systems, HTTPS/TLS must be used.
- HMAC protects payload integrity but does not encrypt the payload. Confidentiality requires TLS encryption.
- The shared secret key is present in the demo frontend for educational purposes. In production, stronger key management is required.
- SQLite is suitable for lab demonstration but larger systems should use production databases such as PostgreSQL or MySQL.
- The attack is demonstrated in a controlled lab environment only.
- The replay protection window is short and simple for demonstration; production systems may require nonce storage and stricter replay controls.

# 13. FUTURE ENHANCEMENTS

Future improvements can include:

- Full HTTPS/TLS integration.
- Public-key based request signing.
- JWT-based authentication with refresh tokens.
- Role-based permission matrix for admin modules.
- Centralized security audit logs.
- Real-time attack alerts on the admin dashboard.
- Database encryption for sensitive fields.
- Docker-based deployment for easier setup.
- Automated test suite for all API routes.
- Stronger key rotation and secret management.

# 14. CONCLUSION

The UniShield Academy project successfully demonstrates how API payloads can be intercepted and modified in an unsecured school management system and how a custom security middleware can protect against such attacks.

The unsecured phase shows a realistic problem: an attacker can change request and response JSON data without the company immediately knowing. The secured phase solves this problem by applying HMAC-SHA256 signatures, timestamp validation, backend verification, response signing, authentication, and admin access control.

The project includes a complete frontend, backend APIs, database, Kali Linux attack workflow, and professional demonstration flow. It clearly proves the importance of API payload integrity and shows how middleware can be used as a practical defense mechanism in modern web applications.

# 15. REFERENCES

1. OWASP Foundation, "OWASP API Security Top 10."

2. OWASP Foundation, "Web Security Testing Guide."

3. H. Krawczyk, M. Bellare, and R. Canetti, "HMAC: Keyed-Hashing for Message Authentication," RFC 2104.

4. Python Software Foundation, "Python hashlib and hmac Documentation."

5. Flask Documentation, "Flask Web Framework."

6. mitmproxy Documentation, "Interactive HTTPS Proxy."

7. SQLite Documentation, "SQLite Database Engine."

