# AI Job Matching System - API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "is_seeker": true
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "is_seeker": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_seeker": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Users

#### Get User by ID
```http
GET /users/{user_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_seeker": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Update User
```http
PUT /users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "John Updated Doe",
  "phone": "+9876543210"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Updated Doe",
  "phone": "+9876543210",
  "is_seeker": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### CV Management

#### Upload CV
```http
POST /cv/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <cv_file>
title: "My Professional CV"
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "My Professional CV",
  "file_path": "/uploads/cvs/1_My_Professional_CV.pdf",
  "file_name": "cv.pdf",
  "parsed_text": "Extracted text from CV...",
  "skills": null,
  "experience": null,
  "education": null,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Get CV by ID
```http
GET /cv/{cv_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "My Professional CV",
  "file_path": "/uploads/cvs/1_My_Professional_CV.pdf",
  "file_name": "cv.pdf",
  "parsed_text": "Extracted text from CV...",
  "skills": "[\"python\", \"javascript\", \"react\"]",
  "experience": "[{\"title\": \"Developer\", \"company\": \"Tech Corp\"}]",
  "education": "[{\"degree\": \"BS Computer Science\"}]",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Get User CVs
```http
GET /cv/user/{user_id}
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "My Professional CV",
    "file_path": "/uploads/cvs/1_My_Professional_CV.pdf",
    "file_name": "cv.pdf",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Analyze CV
```http
POST /cv/{cv_id}/analyze
Authorization: Bearer <token>
```

**Response:**
```json
{
  "skills": ["python", "javascript", "react", "machine learning"],
  "experience": [
    {
      "title": "Senior Developer",
      "company": "Tech Company",
      "description": "Led development team...",
      "years": "5"
    }
  ],
  "education": [
    {
      "degree": "BS Computer Science",
      "institution": "University",
      "year": "2018"
    }
  ],
  "summary": "CV analysis complete. Found 1 experience entries and 1 education entries."
}
```

### Jobs

#### Create Job
```http
POST /jobs/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Senior Software Engineer",
  "company": "Tech Company",
  "description": "We are looking for a senior software engineer...",
  "requirements": "5+ years experience, Python, JavaScript",
  "skills": "python, javascript, react",
  "location": "San Francisco, CA",
  "salary_min": 120000,
  "salary_max": 180000,
  "job_type": "full-time"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Senior Software Engineer",
  "company": "Tech Company",
  "description": "We are looking for a senior software engineer...",
  "requirements": "5+ years experience, Python, JavaScript",
  "skills": "python, javascript, react",
  "location": "San Francisco, CA",
  "salary_min": 120000,
  "salary_max": 180000,
  "job_type": "full-time",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Get Jobs
```http
GET /jobs/?skip=0&limit=100&search=python&location=remote&job_type=full-time
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Senior Software Engineer",
    "company": "Tech Company",
    "description": "We are looking for a senior software engineer...",
    "location": "San Francisco, CA",
    "salary_min": 120000,
    "salary_max": 180000,
    "job_type": "full-time",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Get Job by ID
```http
GET /jobs/{job_id}
```

**Response:**
```json
{
  "id": 1,
  "title": "Senior Software Engineer",
  "company": "Tech Company",
  "description": "We are looking for a senior software engineer...",
  "requirements": "5+ years experience, Python, JavaScript",
  "skills": "python, javascript, react",
  "location": "San Francisco, CA",
  "salary_min": 120000,
  "salary_max": 180000,
  "job_type": "full-time",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Job Matching

#### Find Matches for CV
```http
POST /matching/cv/{cv_id}
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "cv_id": 1,
    "job_id": 1,
    "match_score": 85.5,
    "match_reasons": "{\"score_breakdown\": 85.5}",
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Get User Matches
```http
GET /matching/user/{user_id}
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "cv_id": 1,
    "job_id": 1,
    "match_score": 85.5,
    "match_reasons": "{\"score_breakdown\": 85.5}",
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Update Match Status
```http
PUT /matching/{match_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "viewed"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "cv_id": 1,
  "job_id": 1,
  "match_score": 85.5,
  "match_reasons": "{\"score_breakdown\": 85.5}",
  "status": "viewed",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Notifications

#### Get Notifications
```http
GET /notifications/?unread_only=false
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "type": "match",
    "title": "New Job Matches Found",
    "message": "We found 5 new job matches for your profile.",
    "is_read": false,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Mark Notification as Read
```http
PUT /notifications/{notification_id}/read
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "type": "match",
  "title": "New Job Matches Found",
  "message": "We found 5 new job matches for your profile.",
  "is_read": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Mark All Notifications as Read
```http
PUT /notifications/read-all
Authorization: Bearer <token>
```

**Response:**
```json
{
  "marked_as_read": 5
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Rate Limiting

API requests are rate-limited to prevent abuse:
- 100 requests per minute per IP address
- 1000 requests per hour per IP address

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination using `skip` and `limit` parameters:
- `skip` - Number of items to skip (default: 0)
- `limit` - Number of items to return (default: 100, max: 1000)

Example:
```
GET /jobs/?skip=20&limit=10
```

## Filtering and Search

Many endpoints support filtering and search parameters:
- `search` - Full-text search
- `location` - Filter by location
- `job_type` - Filter by job type
- Custom filters per endpoint

## Webhooks

Webhook notifications can be configured for real-time updates:
- CV analysis complete
- New job matches found
- Application status changes

Configure webhooks via user settings or contact support.
