# API Documentation

Base URL: `http://localhost:8000`. Interactive docs at `/docs` (Swagger) and `/redoc`.
Authenticated endpoints require `Authorization: Bearer <token>`.

## Auth
| Method | Path | Body | Response |
|--------|------|------|----------|
| POST | `/api/auth/register` | `{email, full_name, password, phone?}` | `{access_token, token_type, user}` |
| POST | `/api/auth/login` | form: `username`, `password` | `{access_token, token_type, user}` |
| POST | `/api/auth/login/json` | `{email, password}` | same |

## Users
| GET | `/api/users/me` | – | `UserOut` |
| PATCH | `/api/users/me` | `{full_name?, phone?}` | `UserOut` |

## CV
| POST | `/api/cv/upload` | multipart `file` (pdf/docx/txt, ≤10MB) | `CVOut` |
| GET | `/api/cv` | – | `CVOut[]` |
| GET | `/api/cv/latest` | – | `CVOut \| null` |
| DELETE | `/api/cv/{id}` | – | 204 |

## Jobs
| GET | `/api/jobs?q=&location=&limit=&offset=` | – | `JobOut[]` (public) |
| GET | `/api/jobs/{id}` | – | `JobOut` |
| POST | `/api/jobs` | `JobCreate` | `JobOut` (auth) |

## Matching
| POST | `/api/matching/run?cv_id=&limit=` | – | `MatchOut[]` – recompute matches for CV |
| GET | `/api/matching/recommendations?limit=` | – | `MatchOut[]` – cached matches |

## Notifications
| GET | `/api/notifications?unread_only=` | – | `NotificationOut[]` |
| POST | `/api/notifications/{id}/read` | – | `NotificationOut` |
| POST | `/api/notifications/read-all` | – | `{updated}` |

## Schemas (abridged)

```ts
MatchOut { id, cv_id, job_id, score, skill_score, semantic_score, experience_score,
           matched_skills: string[], missing_skills: string[], created_at, job: JobOut }
CVOut    { id, user_id, file_name, summary, education: string[], experience: string[],
           years_of_experience, skills: {id,name}[], created_at }
```

Errors return `{ "detail": string }` with the appropriate HTTP status.
