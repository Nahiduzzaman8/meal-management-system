# Meal Management System API Reference

This document reflects the actual routes and behavior implemented in the project codebase as of the current snapshot.

> Scope note: Some apps are mounted under both `/api/...` and `/api/auth/...` because `config/urls.py` includes both the app URLs and the auth URLs. Where the same behavior is exposed at multiple prefixes, both paths are listed.

---

## Summary table

| Method | Path | Capability | Description |
|---|---|---|---|
| POST | /api/auth/login/ | public | Authenticate a user and return JWT access/refresh tokens plus the user payload. |
| POST | /api/auth/refresh/ | public | Refresh an existing JWT access token. |
| POST | /api/auth/logout/ | authenticated | Blacklist a refresh token and log the user out. |
| GET | /api/auth/me/ | authenticated | Return the current authenticated user plus capabilities and manager state. |
| POST | /api/auth/password/change/ | authenticated | Change the current user’s password. |
| GET | /api/users/ | user.view | List users with filtering and pagination. |
| POST | /api/users/ | user.create | Create a new user and issue a temporary password. |
| GET | /api/users/{id}/ | user.view | Fetch a single user record. |
| POST | /api/users/{id}/deactivate/ | user.deactivate | Deactivate a user, revoking tokens and clearing active manager assignment if applicable. |
| POST | /api/users/{id}/reactivate/ | user.deactivate | Reactivate a user account. |
| POST | /api/users/{id}/reset-password/ | user.reset_password | Reset a user password and force must_change_password. |
| GET | /api/auth/users/ | user.view | Same as /api/users/ behavior when mounted via auth prefix. |
| POST | /api/auth/users/ | user.create | Same as /api/users/ create behavior. |
| GET | /api/auth/users/{id}/ | user.view | Same as /api/users/{id}/. |
| POST | /api/auth/users/{id}/deactivate/ | user.deactivate | Same as /api/users/{id}/deactivate/. |
| POST | /api/auth/users/{id}/reactivate/ | user.deactivate | Same as /api/users/{id}/reactivate/. |
| POST | /api/auth/users/{id}/reset-password/ | user.reset_password | Same as /api/users/{id}/reset-password/. |
| GET | /api/months/ | month.view | List month records. |
| POST | /api/months/ | month.create | Create a month. |
| GET | /api/months/{id}/ | month.view | Fetch one month. |
| PUT | /api/months/{id}/ | month.create | Update a month. |
| PATCH | /api/months/{id}/ | month.create | Partial update a month. |
| DELETE | /api/months/{id}/ | month.create | Delete a month. |
| POST | /api/months/{id}/open/ | month.open | Open a PLANNED month and seed member rows. |
| POST | /api/months/{id}/close/ | month.close | Close an OPEN month with business validation and finalization. |
| POST | /api/months/{id}/reopen/ | month.reopen | Reopen a CLOSED month and clear finalized fields. |
| GET | /api/months/{id}/members/ | month.view | Return member rows for a month. |
| PUT | /api/months/{id}/manager/ | manager.assign | Assign or switch the current manager for a month. |
| GET | /api/meals/ | meal.view_all or meal.view_own | List meals; normal members only see their own food records. |
| POST | /api/meals/ | meal.submit | Create or update a meal record for the logged-in user. |
| GET | /api/meals/{id}/ | meal.view_all or meal.view_own | Fetch a meal record. |
| PUT | /api/meals/{id}/ | meal.submit | Replace a meal record. |
| PATCH | /api/meals/{id}/ | meal.submit | Partial update a meal record. |
| DELETE | /api/meals/{id}/ | meal.submit | Delete a meal record. |
| PATCH | /api/meals/{id}/correct/ | meal.correct | Correct lunch/dinner values and log the reason. |
| GET | /api/guest-meals/ | guest_meal.view_all or guest_meal.view_own | List guest meal submissions. |
| POST | /api/guest-meals/ | guest_meal.submit | Submit a guest meal entry. |
| GET | /api/guest-meals/{id}/ | guest_meal.view_all or guest_meal.view_own | Fetch a guest meal. |
| PUT | /api/guest-meals/{id}/ | guest_meal.submit | Replace a guest meal. |
| PATCH | /api/guest-meals/{id}/ | guest_meal.submit | Partial update a guest meal. |
| DELETE | /api/guest-meals/{id}/ | guest_meal.submit | Delete a guest meal. |
| POST | /api/guest-meals/{id}/approve/ | guest_meal.approve | Approve a pending guest meal. |
| POST | /api/guest-meals/{id}/reject/ | guest_meal.approve | Reject a pending guest meal. |
| GET | /api/deposits/ | deposit.approve or deposit.view_own | List deposits. |
| POST | /api/deposits/ | deposit.approve or deposit.view_own | Submit a deposit record. |
| GET | /api/deposits/{id}/ | deposit.approve or deposit.view_own | Fetch a deposit. |
| PUT | /api/deposits/{id}/ | deposit.approve or deposit.view_own | Replace a deposit. |
| PATCH | /api/deposits/{id}/ | deposit.approve or deposit.view_own | Partial update a deposit. |
| DELETE | /api/deposits/{id}/ | deposit.approve or deposit.view_own | Delete a deposit. |
| POST | /api/deposits/{id}/approve/ | deposit.approve | Approve a pending deposit. |
| POST | /api/deposits/{id}/reject/ | deposit.approve | Reject a pending deposit. |
| GET | /api/expenses/ | expense.create | List expenses. |
| POST | /api/expenses/ | expense.create | Create a new expense. |
| GET | /api/expenses/{id}/ | expense.create | Fetch an expense. |
| PUT | /api/expenses/{id}/ | expense.create | Replace an expense. |
| PATCH | /api/expenses/{id}/ | expense.create | Partial update an expense. |
| DELETE | /api/expenses/{id}/ | expense.delete | Soft-delete an expense. |
| GET | /api/adjustments/ | adjustment.create | List adjustments. |
| POST | /api/adjustments/ | adjustment.create | Create an adjustment. |
| GET | /api/adjustments/{id}/ | adjustment.create | Fetch an adjustment. |
| PUT | /api/adjustments/{id}/ | adjustment.create | Replace an adjustment. |
| PATCH | /api/adjustments/{id}/ | adjustment.create | Partial update an adjustment. |
| DELETE | /api/adjustments/{id}/ | adjustment.create | Delete an adjustment. |
| GET | /api/notifications/ | authenticated | List the current user’s notifications. |
| POST | /api/notifications/{id}/mark-read/ | authenticated | Mark a notification as read. |
| GET | /api/reports/monthly/ | authenticated | Get current or finalized month financial summary. |
| GET | /api/reports/members/ | authenticated | Get member-level month report data. |
| GET | /api/reports/balances/ | authenticated | Get finalized balance history for a member. |
| GET | /api/dashboard/ | authenticated | Get dashboard summary for current month and current user. |
| Audit | None | NOT YET IMPLEMENTED | No audit API URL patterns or views were found in the app. |
| Settings | None | NOT YET IMPLEMENTED | No settings API URL patterns or views were found in the app. |

---

# Auth

## POST /api/auth/login/

**Capability:** `public`

**Request body**
```json
{
  "username": "rahat",
  "password": "StrongPass#123"
}
```

**Response — 200 OK**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 3,
    "username": "rahat",
    "email": "rahat@example.com",
    "role": "MEMBER",
    "must_change_password": true
  }
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | validation_error | Username/password validation fails in `TokenObtainPairSerializer` or required fields are missing. |

## POST /api/auth/refresh/

**Capability:** `public`

**Request body**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response — 200 OK**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | token_not_valid | `RefreshToken` is invalid, expired, or malformed. |

## POST /api/auth/logout/

**Capability:** `authenticated`

**Request body**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response — 200 OK**
```json
{
  "detail": "Logged out successfully."
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | invalid_token | Missing refresh token or token cannot be blacklisted. |

## GET /api/auth/me/

**Capability:** `authenticated`

**Query parameters**
- None

**Response — 200 OK**
```json
{
  "id": 3,
  "username": "rahat",
  "email": "rahat@example.com",
  "role": "MEMBER",
  "must_change_password": true,
  "is_manager": false,
  "capabilities": [
    "meal.submit",
    "meal.view_own",
    "deposit.submit",
    "deposit.view_own",
    "guest_meal.submit",
    "guest_meal.view_own",
    "report.view_own"
  ]
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 401 | authentication_failed | Request is unauthenticated. |

## POST /api/auth/password/change/

**Capability:** `authenticated`

**Request body**
```json
{
  "current_password": "OldPass#123",
  "new_password": "NewPass#456",
  "confirm_password": "NewPass#456"
}
```

**Response — 200 OK**
```json
{
  "detail": "Password changed successfully."
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | wrong_password | Current password does not match the user’s stored password. |
| 400 | password_mismatch | `new_password` and `confirm_password` do not match. |
| 400 | password_invalid | New password fails Django password validators. |

---

# Users

## GET /api/users/

**Capability:** `user.view`

**Query parameters**
- `role` (optional) — filter by `ADMIN` or `MEMBER`
- `is_active` (optional) — `true` or `false`
- `search` (optional) — text match against username/email
- `page` (optional) — pagination
- `page_size` (optional) — pagination, max 100

**Response — 200 OK**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "first_name": "",
      "last_name": "",
      "role": "ADMIN",
      "phone": "",
      "is_active": true,
      "is_staff": true,
      "is_superuser": true,
      "date_joined": "2026-09-01T10:00:00Z"
    },
    {
      "id": 3,
      "username": "rahat",
      "email": "rahat@example.com",
      "first_name": "Rahat",
      "last_name": "Hossain",
      "role": "MEMBER",
      "phone": "01712345678",
      "is_active": true,
      "is_staff": false,
      "is_superuser": false,
      "date_joined": "2026-09-02T09:30:00Z"
    }
  ]
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `user.view`. |

## POST /api/users/

**Capability:** `user.create`

**Request body**
```json
{
  "username": "shahid",
  "email": "shahid@example.com",
  "first_name": "Shahid",
  "last_name": "Rahman",
  "role": "MEMBER",
  "phone": "01798765432"
}
```

**Response — 201 Created**
```json
{
  "id": 7,
  "username": "shahid",
  "email": "shahid@example.com",
  "first_name": "Shahid",
  "last_name": "Rahman",
  "role": "MEMBER",
  "phone": "01798765432",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "must_change_password": true,
  "date_joined": "2026-09-24T12:15:00Z",
  "temporary_password": "A5Q!fN8hLJb#vY3r"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | username_taken | Username already exists, case-insensitive. |
| 400 | email_taken | Email already exists, case-insensitive. |
| 403 | permission_denied | User lacks `user.create`. |

## GET /api/users/{id}/

**Capability:** `user.view`

**Response — 200 OK**
```json
{
  "id": 3,
  "username": "rahat",
  "email": "rahat@example.com",
  "first_name": "Rahat",
  "last_name": "Hossain",
  "role": "MEMBER",
  "phone": "01712345678",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "must_change_password": true,
  "date_joined": "2026-09-02T09:30:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `user.view`. |
| 404 | not_found | User ID does not exist. |

## POST /api/users/{id}/deactivate/

**Capability:** `user.deactivate`

**Request body**
```json
{}
```

**Response — 200 OK**
```json
{
  "id": 3,
  "username": "rahat",
  "email": "rahat@example.com",
  "first_name": "Rahat",
  "last_name": "Hossain",
  "role": "MEMBER",
  "phone": "01712345678",
  "is_active": false,
  "is_staff": false,
  "is_superuser": false,
  "must_change_password": true,
  "date_joined": "2026-09-02T09:30:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `user.deactivate`. |
| 404 | not_found | User ID does not exist. |

## POST /api/users/{id}/reactivate/

**Capability:** `user.deactivate`

**Request body**
```json
{}
```

**Response — 200 OK**
```json
{
  "id": 3,
  "username": "rahat",
  "email": "rahat@example.com",
  "first_name": "Rahat",
  "last_name": "Hossain",
  "role": "MEMBER",
  "phone": "01712345678",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "must_change_password": true,
  "date_joined": "2026-09-02T09:30:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `user.deactivate`. |
| 404 | not_found | User ID does not exist. |

## POST /api/users/{id}/reset-password/

**Capability:** `user.reset_password`

**Request body**
```json
{}
```

**Response — 200 OK**
```json
{
  "id": 3,
  "username": "rahat",
  "temporary_password": "H7!iJm2xL@q4P9sR"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `user.reset_password`. |
| 404 | not_found | User ID does not exist. |

### Note on duplicate user routes
The same user API is also mounted under `/api/auth/users/` via `apps.users.urls` and `config/urls.py`. The behavior is the same as the `/api/users/` routes above.

---

# Months

## GET /api/months/

**Capability:** `month.view`

**Query parameters**
- `page` (optional)
- `page_size` (optional)

**Response — 200 OK**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 11,
      "name": "2026-09",
      "start_date": "2026-09-01",
      "end_date": "2026-09-30",
      "status": "OPEN",
      "final_meal_rate": null,
      "final_total_expense": null,
      "final_total_meal_units": null,
      "rounding_residual": null,
      "closed_at": null,
      "closed_by": null,
      "reopened_count": 0,
      "last_reopened_at": null,
      "created_by": 1,
      "created_at": "2026-08-29T09:00:00Z",
      "updated_at": "2026-09-01T08:00:00Z"
    }
  ]
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `month.view`. |

## POST /api/months/

**Capability:** `month.create`

**Request body**
```json
{
  "name": "2026-10",
  "start_date": "2026-10-01",
  "end_date": "2026-10-31"
}
```

**Response — 201 Created**
```json
{
  "id": 12,
  "name": "2026-10",
  "start_date": "2026-10-01",
  "end_date": "2026-10-31",
  "status": "PLANNED",
  "final_meal_rate": null,
  "final_total_expense": null,
  "final_total_meal_units": null,
  "rounding_residual": null,
  "closed_at": null,
  "closed_by": null,
  "reopened_count": 0,
  "last_reopened_at": null,
  "created_by": 1,
  "created_at": "2026-09-24T10:30:00Z",
  "updated_at": "2026-09-24T10:30:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | end_date | `end_date` is not after `start_date`. |
| 400 | non_field_errors | Date range overlaps an existing month. |
| 403 | permission_denied | User lacks `month.create`. |

## GET /api/months/{id}/

**Capability:** `month.view`

**Response — 200 OK**
```json
{
  "id": 11,
  "name": "2026-09",
  "start_date": "2026-09-01",
  "end_date": "2026-09-30",
  "status": "OPEN",
  "final_meal_rate": null,
  "final_total_expense": null,
  "final_total_meal_units": null,
  "rounding_residual": null,
  "closed_at": null,
  "closed_by": null,
  "reopened_count": 0,
  "last_reopened_at": null,
  "created_by": 1,
  "created_at": "2026-08-29T09:00:00Z",
  "updated_at": "2026-09-01T08:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `month.view`. |
| 404 | not_found | Month does not exist. |

## PUT /api/months/{id}/

**Capability:** `month.create`

**Request body**
```json
{
  "name": "2026-09",
  "start_date": "2026-09-01",
  "end_date": "2026-09-30"
}
```

**Response — 200 OK**
```json
{
  "id": 11,
  "name": "2026-09",
  "start_date": "2026-09-01",
  "end_date": "2026-09-30",
  "status": "OPEN",
  "final_meal_rate": null,
  "final_total_expense": null,
  "final_total_meal_units": null,
  "rounding_residual": null,
  "closed_at": null,
  "closed_by": null,
  "reopened_count": 0,
  "last_reopened_at": null,
  "created_by": 1,
  "created_at": "2026-08-29T09:00:00Z",
  "updated_at": "2026-09-24T11:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | end_date | end date is invalid. |
| 400 | non_field_errors | Month overlaps another month. |
| 403 | permission_denied | User lacks `month.create`. |
| 404 | not_found | Month does not exist. |

## PATCH /api/months/{id}/

**Capability:** `month.create`

**Request body**
```json
{
  "status": "OPEN"
}
```

**Response — 200 OK**
```json
{
  "id": 11,
  "name": "2026-09",
  "start_date": "2026-09-01",
  "end_date": "2026-09-30",
  "status": "OPEN",
  "final_meal_rate": null,
  "final_total_expense": null,
  "final_total_meal_units": null,
  "rounding_residual": null,
  "closed_at": null,
  "closed_by": null,
  "reopened_count": 0,
  "last_reopened_at": null,
  "created_by": 1,
  "created_at": "2026-08-29T09:00:00Z",
  "updated_at": "2026-09-24T11:15:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | end_date | `end_date` is invalid after partial update. |
| 403 | permission_denied | User lacks `month.create`. |
| 404 | not_found | Month does not exist. |

## DELETE /api/months/{id}/

**Capability:** `month.create`

**Request body**
```json
{}
```

**Response — 204 No Content**
```json
{ }
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `month.create`. |
| 404 | not_found | Month does not exist. |

## POST /api/months/{id}/open/

**Capability:** `month.open`

**Request body**
```json
{}
```

**Response — 200 OK**
```json
{
  "id": 11,
  "name": "2026-09",
  "start_date": "2026-09-01",
  "end_date": "2026-09-30",
  "status": "OPEN",
  "final_meal_rate": null,
  "final_total_expense": null,
  "final_total_meal_units": null,
  "rounding_residual": null,
  "closed_at": null,
  "closed_by": null,
  "reopened_count": 0,
  "last_reopened_at": null,
  "created_by": 1,
  "created_at": "2026-08-29T09:00:00Z",
  "updated_at": "2026-09-24T11:20:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | detail | Only `PLANNED` months can be opened. |
| 400 | detail | Another month is already OPEN. |
| 403 | permission_denied | User lacks `month.open`. |

## POST /api/months/{id}/close/

**Capability:** `month.close`

**Request body**
```json
{
  "Idempotency-Key": "close-2026-09-24-abc123"
}
```

**Response — 200 OK**
```json
{
  "id": 11,
  "name": "2026-09",
  "start_date": "2026-09-01",
  "end_date": "2026-09-30",
  "status": "CLOSED",
  "final_meal_rate": "19.5000",
  "final_total_expense": "12345.67",
  "final_total_meal_units": 122,
  "rounding_residual": "0.00",
  "closed_at": "2026-09-24T12:00:00Z",
  "closed_by": 1,
  "reopened_count": 0,
  "last_reopened_at": null,
  "created_by": 1,
  "created_at": "2026-08-29T09:00:00Z",
  "updated_at": "2026-09-24T12:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_close_blocked | Closed month did not satisfy pre-close validations. `failures` list may include `Month must be OPEN to close.`, `There are pending deposits for this month.`, `There are pending guest meals for this month.`, `Countable meal units must be greater than zero.`, `Total non-deleted expense amount must be greater than zero.`, `At least one active MonthMember is required.`, or `A currently active ManagerAssignment is required.` |
| 200 | detail | Same `Idempotency-Key` already processed; the closure is considered already done. |
| 403 | permission_denied | User lacks `month.close`. |

## POST /api/months/{id}/reopen/

**Capability:** `month.reopen`

**Request body**
```json
{}
```

**Response — 200 OK**
```json
{
  "id": 11,
  "name": "2026-09",
  "start_date": "2026-09-01",
  "end_date": "2026-09-30",
  "status": "OPEN",
  "final_meal_rate": null,
  "final_total_expense": null,
  "final_total_meal_units": null,
  "rounding_residual": null,
  "closed_at": null,
  "closed_by": null,
  "reopened_count": 1,
  "last_reopened_at": "2026-09-24T12:05:00Z",
  "created_by": 1,
  "created_at": "2026-08-29T09:00:00Z",
  "updated_at": "2026-09-24T12:05:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | detail | Month is not `CLOSED`. |
| 400 | detail | Another month is already OPEN. |
| 403 | permission_denied | User lacks `month.reopen`. |

## GET /api/months/{id}/members/

**Capability:** `month.view`

**Response — 200 OK**
```json
[
  {
    "id": 14,
    "member": 3,
    "member_username": "rahat",
    "month": 11,
    "joined_on": "2026-09-01",
    "left_on": null,
    "opening_balance": "0.00",
    "lunch_count": 10,
    "dinner_count": 8,
    "meal_units": 18,
    "guest_lunch_count": 0,
    "guest_dinner_count": 0,
    "guest_meal_units": 0,
    "meal_rate_applied": null,
    "meal_cost": "0.00",
    "guest_meal_cost": "0.00",
    "adjustment_total": "0.00",
    "total_cost": "0.00",
    "approved_deposit_total": "0.00",
    "closing_balance": "0.00",
    "finalized_at": null
  }
]
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `month.view`. |
| 404 | not_found | Month does not exist. |

## PUT /api/months/{id}/manager/

**Capability:** `manager.assign`

**Request body**
```json
{
  "user_id": 3
}
```

**Response — 200 OK**
```json
{
  "id": 22,
  "month": 11,
  "user": 3,
  "assigned_by": 1,
  "unassigned_by": null,
  "assigned_at": "2026-09-24T11:30:00Z",
  "unassigned_at": null
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | detail | `user_id` missing. |
| 404 | detail | User not found. |
| 400 | detail | Target user is inactive. |
| 400 | detail | Target user is not a `MEMBER`. |
| 400 | detail | Target user is already the current manager. |
| 403 | permission_denied | User lacks `manager.assign`. |

---

# Meals

## GET /api/meals/

**Capability:** `meal.view_all` or `meal.view_own`

**Query parameters**
- `month` or `month_id` (optional) — filter meals by month id
- `page` (optional)
- `page_size` (optional)

**Response — 200 OK**
```json
[
  {
    "id": 51,
    "member": 3,
    "month": 11,
    "meal_date": "2026-09-03",
    "lunch": true,
    "dinner": false,
    "last_corrected_by": null,
    "last_corrected_at": null,
    "correction_reason": "",
    "created_at": "2026-09-03T08:10:00Z",
    "updated_at": "2026-09-03T08:10:00Z"
  }
]
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks the required meal view capability. |

## POST /api/meals/

**Capability:** `meal.submit`

**Request body**
```json
{
  "meal_date": "2026-10-01",
  "lunch": true,
  "dinner": false
}
```

**Response — 201 Created**
```json
{
  "id": 52,
  "member": 3,
  "month": 12,
  "meal_date": "2026-10-01",
  "lunch": true,
  "dinner": false,
  "last_corrected_by": null,
  "last_corrected_at": null,
  "correction_reason": "",
  "created_at": "2026-10-01T07:15:00Z",
  "updated_at": "2026-10-01T07:15:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | validation_error | Meal date falls outside any PLANNED/OPEN month. |
| 400 | deadline_passed | Submission is after the configured deadline for that date. |
| 403 | permission_denied | User lacks `meal.submit`. |

## GET /api/meals/{id}/

**Capability:** `meal.view_all` or `meal.view_own`

**Response — 200 OK**
```json
{
  "id": 51,
  "member": 3,
  "month": 11,
  "meal_date": "2026-09-03",
  "lunch": true,
  "dinner": false,
  "last_corrected_by": null,
  "last_corrected_at": null,
  "correction_reason": "",
  "created_at": "2026-09-03T08:10:00Z",
  "updated_at": "2026-09-03T08:10:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User cannot view this meal. |
| 404 | not_found | Meal not found. |

## PUT /api/meals/{id}/

**Capability:** `meal.submit`

**Request body**
```json
{
  "meal_date": "2026-10-01",
  "lunch": true,
  "dinner": true
}
```

**Response — 200 OK**
```json
{
  "id": 52,
  "member": 3,
  "month": 12,
  "meal_date": "2026-10-01",
  "lunch": true,
  "dinner": true,
  "last_corrected_by": null,
  "last_corrected_at": null,
  "correction_reason": "",
  "created_at": "2026-10-01T07:15:00Z",
  "updated_at": "2026-10-01T08:10:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | deadline_passed | PUT occurs after the deadline. |
| 403 | permission_denied | User lacks `meal.submit`. |
| 404 | not_found | Meal not found. |

## PATCH /api/meals/{id}/

**Capability:** `meal.submit`

**Request body**
```json
{
  "dinner": true
}
```

**Response — 200 OK**
```json
{
  "id": 52,
  "member": 3,
  "month": 12,
  "meal_date": "2026-10-01",
  "lunch": true,
  "dinner": true,
  "last_corrected_by": null,
  "last_corrected_at": null,
  "correction_reason": "",
  "created_at": "2026-10-01T07:15:00Z",
  "updated_at": "2026-10-01T08:15:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | deadline_passed | PATCH occurs after the deadline. |
| 403 | permission_denied | User lacks `meal.submit`. |
| 404 | not_found | Meal not found. |

## DELETE /api/meals/{id}/

**Capability:** `meal.submit`

**Request body**
```json
{}
```

**Response — 204 No Content**
```json
{}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `meal.submit`. |
| 404 | not_found | Meal not found. |

## PATCH /api/meals/{id}/correct/

**Capability:** `meal.correct`

**Request body**
```json
{
  "lunch": false,
  "dinner": true,
  "reason": "Incorrect previous entry made during travel."
}
```

**Response — 200 OK**
```json
{
  "id": 52,
  "member": 3,
  "month": 12,
  "meal_date": "2026-10-01",
  "lunch": false,
  "dinner": true,
  "last_corrected_by": 1,
  "last_corrected_at": "2026-10-01T18:00:00Z",
  "correction_reason": "Incorrect previous entry made during travel.",
  "created_at": "2026-10-01T07:15:00Z",
  "updated_at": "2026-10-01T18:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_closed | Attempt to correct meals in a closed month. |
| 400 | detail | At least one of `lunch` or `dinner` must be selected. |
| 403 | permission_denied | User lacks `meal.correct` or manager override without manager status. |
| 404 | not_found | Meal not found. |

---

# Guest Meals

## GET /api/guest-meals/

**Capability:** `guest_meal.view_all` or `guest_meal.view_own`

**Response — 200 OK**
```json
[
  {
    "id": 10,
    "member": 3,
    "month": 12,
    "meal_date": "2026-10-02",
    "lunch_quantity": 2,
    "dinner_quantity": 1,
    "status": "PENDING",
    "rejection_reason": "",
    "remarks": "Guest for family dinner",
    "submitted_at": "2026-10-02T07:10:00Z",
    "processed_at": null,
    "processed_by": null
  }
]
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks guest meal view access. |

## POST /api/guest-meals/

**Capability:** `guest_meal.submit`

**Request body**
```json
{
  "meal_date": "2026-10-02",
  "lunch_quantity": 2,
  "dinner_quantity": 1,
  "remarks": "Guest for family dinner"
}
```

**Response — 201 Created**
```json
{
  "id": 10,
  "member": 3,
  "month": 12,
  "meal_date": "2026-10-02",
  "lunch_quantity": 2,
  "dinner_quantity": 1,
  "status": "PENDING",
  "rejection_reason": "",
  "remarks": "Guest for family dinner",
  "submitted_at": "2026-10-02T07:10:00Z",
  "processed_at": null,
  "processed_by": null
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | meal_date | Duplicate guest meal for the same user/date already exists. |
| 400 | detail | `meal_date` does not map to a valid PLANNED/OPEN month. |
| 403 | permission_denied | User lacks `guest_meal.submit`. |

## GET /api/guest-meals/{id}/

**Capability:** `guest_meal.view_all` or `guest_meal.view_own`

**Response — 200 OK**
```json
{
  "id": 10,
  "member": 3,
  "month": 12,
  "meal_date": "2026-10-02",
  "lunch_quantity": 2,
  "dinner_quantity": 1,
  "status": "PENDING",
  "rejection_reason": "",
  "remarks": "Guest for family dinner",
  "submitted_at": "2026-10-02T07:10:00Z",
  "processed_at": null,
  "processed_by": null
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User cannot access the record. |
| 404 | not_found | Guest meal does not exist. |

## PUT /api/guest-meals/{id}/

**Capability:** `guest_meal.submit`

**Request body**
```json
{
  "meal_date": "2026-10-02",
  "lunch_quantity": 3,
  "dinner_quantity": 1,
  "remarks": "Updated guest count"
}
```

**Response — 200 OK**
```json
{
  "id": 10,
  "member": 3,
  "month": 12,
  "meal_date": "2026-10-02",
  "lunch_quantity": 3,
  "dinner_quantity": 1,
  "status": "PENDING",
  "rejection_reason": "",
  "remarks": "Updated guest count",
  "submitted_at": "2026-10-02T07:10:00Z",
  "processed_at": null,
  "processed_by": null
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `guest_meal.submit`. |
| 404 | not_found | Guest meal does not exist. |

## PATCH /api/guest-meals/{id}/

**Capability:** `guest_meal.submit`

**Request body**
```json
{
  "remarks": "Guest request adjusted"
}
```

**Response — 200 OK**
```json
{
  "id": 10,
  "member": 3,
  "month": 12,
  "meal_date": "2026-10-02",
  "lunch_quantity": 3,
  "dinner_quantity": 1,
  "status": "PENDING",
  "rejection_reason": "",
  "remarks": "Guest request adjusted",
  "submitted_at": "2026-10-02T07:10:00Z",
  "processed_at": null,
  "processed_by": null
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `guest_meal.submit`. |
| 404 | not_found | Guest meal does not exist. |

## DELETE /api/guest-meals/{id}/

**Capability:** `guest_meal.submit`

**Request body**
```json
{}
```

**Response — 204 No Content**
```json
{}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `guest_meal.submit`. |
| 404 | not_found | Guest meal not found. |

## POST /api/guest-meals/{id}/approve/

**Capability:** `guest_meal.approve`

**Request body**
```json
{
  "reason": "Normal guest meal for family visit."
}
```

**Response — 200 OK**
```json
{
  "id": 10,
  "member": 3,
  "month": 12,
  "meal_date": "2026-10-02",
  "lunch_quantity": 3,
  "dinner_quantity": 1,
  "status": "APPROVED",
  "rejection_reason": "",
  "remarks": "Normal guest meal for family visit.",
  "submitted_at": "2026-10-02T07:10:00Z",
  "processed_at": "2026-10-02T12:00:00Z",
  "processed_by": 1
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | detail | Rejected guest meals cannot be approved. |
| 403 | permission_denied | User lacks `guest_meal.approve` or manager override. |
| 404 | not_found | Guest meal does not exist. |

## POST /api/guest-meals/{id}/reject/

**Capability:** `guest_meal.approve`

**Request body**
```json
{
  "reason": "Entry does not match approved guest list."
}
```

**Response — 200 OK**
```json
{
  "id": 10,
  "member": 3,
  "month": 12,
  "meal_date": "2026-10-02",
  "lunch_quantity": 3,
  "dinner_quantity": 1,
  "status": "REJECTED",
  "rejection_reason": "Entry does not match approved guest list.",
  "remarks": "",
  "submitted_at": "2026-10-02T07:10:00Z",
  "processed_at": "2026-10-02T12:01:00Z",
  "processed_by": 1
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | detail | Approved guest meals cannot be rejected. |
| 403 | permission_denied | User lacks `guest_meal.approve` or manager override. |
| 404 | not_found | Guest meal does not exist. |

---

# Deposits

## GET /api/deposits/

**Capability:** `deposit.approve` or `deposit.view_own`

**Query parameters**
- `page` (optional)
- `page_size` (optional)

**Response — 200 OK**
```json
[
  {
    "id": 17,
    "member": 3,
    "month": 12,
    "amount": "2000.00",
    "payment_method": "BKASH",
    "transaction_reference": "BKASH-2026-10-01-1234",
    "payment_date": "2026-10-01",
    "status": "PENDING",
    "rejection_reason": "",
    "submitted_at": "2026-10-01T09:00:00Z",
    "processed_at": null,
    "processed_by": null,
    "note": "Monthly deposit"
  }
]
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks deposit access. |

## POST /api/deposits/

**Capability:** `deposit.approve` or `deposit.view_own` (create uses serializer validation and user member assignment; access is controlled by permission class)

**Request body**
```json
{
  "amount": "2000.00",
  "payment_method": "BKASH",
  "transaction_reference": "BKASH-2026-10-01-1234",
  "payment_date": "2026-10-01",
  "note": "Monthly deposit"
}
```

**Response — 201 Created**
```json
{
  "id": 17,
  "member": 3,
  "month": 12,
  "amount": "2000.00",
  "payment_method": "BKASH",
  "transaction_reference": "BKASH-2026-10-01-1234",
  "payment_date": "2026-10-01",
  "status": "PENDING",
  "rejection_reason": "",
  "submitted_at": "2026-10-01T09:00:00Z",
  "processed_at": null,
  "processed_by": null,
  "note": "Monthly deposit"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | amount | Amount is not greater than zero. |
| 400 | transaction_reference | Non-cash payment methods require a transaction reference. |
| 400 | month_not_open | No currently OPEN month exists or the month is not OPEN. |
| 400 | payment_date | Payment date is outside the currently OPEN month. |
| 403 | permission_denied | User lacks deposit creation access. |

## GET /api/deposits/{id}/

**Capability:** `deposit.approve` or `deposit.view_own`

**Response — 200 OK**
```json
{
  "id": 17,
  "member": 3,
  "month": 12,
  "amount": "2000.00",
  "payment_method": "BKASH",
  "transaction_reference": "BKASH-2026-10-01-1234",
  "payment_date": "2026-10-01",
  "status": "PENDING",
  "rejection_reason": "",
  "submitted_at": "2026-10-01T09:00:00Z",
  "processed_at": null,
  "processed_by": null,
  "note": "Monthly deposit"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User cannot view the deposit. |
| 404 | not_found | Deposit not found. |

## POST /api/deposits/{id}/approve/

**Capability:** `deposit.approve`

**Request body**
```json
{}
```

**Response — 200 OK**
```json
{
  "id": 17,
  "member": 3,
  "month": 12,
  "amount": "2000.00",
  "payment_method": "BKASH",
  "transaction_reference": "BKASH-2026-10-01-1234",
  "payment_date": "2026-10-01",
  "status": "APPROVED",
  "rejection_reason": "",
  "submitted_at": "2026-10-01T09:00:00Z",
  "processed_at": "2026-10-01T18:30:00Z",
  "processed_by": 1,
  "note": "Monthly deposit"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | detail | Only `PENDING` deposits can be approved. |
| 400 | month_closed | Deposit can only be approved while the month remains OPEN. |
| 403 | permission_denied | User lacks `deposit.approve` or manager override. |
| 404 | not_found | Deposit not found. |

## POST /api/deposits/{id}/reject/

**Capability:** `deposit.approve`

**Request body**
```json
{
  "reason": "Bank transfer reference does not match."
}
```

**Response — 200 OK**
```json
{
  "id": 17,
  "member": 3,
  "month": 12,
  "amount": "2000.00",
  "payment_method": "BKASH",
  "transaction_reference": "BKASH-2026-10-01-1234",
  "payment_date": "2026-10-01",
  "status": "REJECTED",
  "rejection_reason": "Bank transfer reference does not match.",
  "submitted_at": "2026-10-01T09:00:00Z",
  "processed_at": "2026-10-01T18:35:00Z",
  "processed_by": 1,
  "note": "Monthly deposit"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | reason | Rejection reason is required. |
| 400 | detail | Only `PENDING` deposits can be rejected. |
| 400 | month_closed | Deposit can only be rejected while the month remains OPEN. |
| 403 | permission_denied | User lacks `deposit.approve` or manager override. |
| 404 | not_found | Deposit not found. |

---

# Expenses

## GET /api/expenses/

**Capability:** `expense.create`

**Response — 200 OK**
```json
[
  {
    "id": 9,
    "month": 12,
    "created_by": 1,
    "category": "Grocery",
    "amount": "8500.00",
    "expense_date": "2026-10-03",
    "description": "Rice and vegetables",
    "is_deleted": false,
    "deleted_at": null,
    "deleted_by": null,
    "delete_reason": "",
    "created_at": "2026-10-03T08:20:00Z",
    "updated_at": "2026-10-03T08:20:00Z"
  }
]
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `expense.create`. |

## POST /api/expenses/

**Capability:** `expense.create`

**Request body**
```json
{
  "month": 12,
  "category": "Grocery",
  "amount": "8500.00",
  "expense_date": "2026-10-03",
  "description": "Rice and vegetables"
}
```

**Response — 201 Created**
```json
{
  "id": 9,
  "month": 12,
  "created_by": 1,
  "category": "Grocery",
  "amount": "8500.00",
  "expense_date": "2026-10-03",
  "description": "Rice and vegetables",
  "is_deleted": false,
  "deleted_at": null,
  "deleted_by": null,
  "delete_reason": "",
  "created_at": "2026-10-03T08:20:00Z",
  "updated_at": "2026-10-03T08:20:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | amount | `amount` must be greater than zero. |
| 400 | description | Description is required or blank. |
| 400 | month_not_open | No OPEN month exists or selected month is not OPEN. |
| 400 | expense_date | Expense date falls outside the selected OPEN month. |
| 403 | permission_denied | User lacks `expense.create`. |

## GET /api/expenses/{id}/

**Capability:** `expense.create`

**Response — 200 OK**
```json
{
  "id": 9,
  "month": 12,
  "created_by": 1,
  "category": "Grocery",
  "amount": "8500.00",
  "expense_date": "2026-10-03",
  "description": "Rice and vegetables",
  "is_deleted": false,
  "deleted_at": null,
  "deleted_by": null,
  "delete_reason": "",
  "created_at": "2026-10-03T08:20:00Z",
  "updated_at": "2026-10-03T08:20:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `expense.create`. |
| 404 | not_found | Expense not found. |

## PUT /api/expenses/{id}/

**Capability:** `expense.create`

**Request body**
```json
{
  "month": 12,
  "category": "Gas",
  "amount": "2200.00",
  "expense_date": "2026-10-12",
  "description": "Cylinder refill"
}
```

**Response — 200 OK**
```json
{
  "id": 9,
  "month": 12,
  "created_by": 1,
  "category": "Gas",
  "amount": "2200.00",
  "expense_date": "2026-10-12",
  "description": "Cylinder refill",
  "is_deleted": false,
  "deleted_at": null,
  "deleted_by": null,
  "delete_reason": "",
  "created_at": "2026-10-03T08:20:00Z",
  "updated_at": "2026-10-12T10:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_closed | Expense can only be updated while the month remains OPEN. |
| 403 | permission_denied | User lacks `expense.create`. |
| 404 | not_found | Expense not found. |

## PATCH /api/expenses/{id}/

**Capability:** `expense.create`

**Request body**
```json
{
  "amount": "2400.00"
}
```

**Response — 200 OK**
```json
{
  "id": 9,
  "month": 12,
  "created_by": 1,
  "category": "Gas",
  "amount": "2400.00",
  "expense_date": "2026-10-12",
  "description": "Cylinder refill",
  "is_deleted": false,
  "deleted_at": null,
  "deleted_by": null,
  "delete_reason": "",
  "created_at": "2026-10-03T08:20:00Z",
  "updated_at": "2026-10-12T10:05:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_closed | Expense can only be updated while the month remains OPEN. |
| 403 | permission_denied | User lacks `expense.create`. |
| 404 | not_found | Expense not found. |

## DELETE /api/expenses/{id}/

**Capability:** `expense.delete`

**Request body**
```json
{
  "reason": "Duplicate entry"
}
```

**Response — 200 OK**
```json
{
  "detail": "Expense marked as deleted."
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | reason | Delete reason is required. |
| 400 | month_closed | Expense can only be soft-deleted while the month remains OPEN. |
| 403 | permission_denied | User lacks `expense.delete`. |
| 404 | not_found | Expense not found. |

---

# Adjustments

## GET /api/adjustments/

**Capability:** `adjustment.create`

**Response — 200 OK**
```json
[
  {
    "id": 2,
    "month": 12,
    "member": 3,
    "direction": "DEBIT",
    "amount": "50.00",
    "reason": "Extra meal subsidy",
    "source_entity_type": null,
    "source_entity_id": null,
    "created_by": 1,
    "created_at": "2026-10-02T06:00:00Z"
  }
]
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `adjustment.create`. |

## POST /api/adjustments/

**Capability:** `adjustment.create`

**Request body**
```json
{
  "month": 12,
  "member": 3,
  "direction": "DEBIT",
  "amount": "50.00",
  "reason": "Extra meal subsidy",
  "source_entity_type": "Meal",
  "source_entity_id": 51
}
```

**Response — 201 Created**
```json
{
  "id": 2,
  "month": 12,
  "member": 3,
  "direction": "DEBIT",
  "amount": "50.00",
  "reason": "Extra meal subsidy",
  "source_entity_type": "Meal",
  "source_entity_id": 51,
  "created_by": 1,
  "created_at": "2026-10-02T06:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | amount | Amount must be greater than zero. |
| 400 | reason | Reason is required. |
| 400 | month_not_open | Adjustments are only allowed against an OPEN month. |
| 403 | permission_denied | User lacks `adjustment.create`. |

## GET /api/adjustments/{id}/

**Capability:** `adjustment.create`

**Response — 200 OK**
```json
{
  "id": 2,
  "month": 12,
  "member": 3,
  "direction": "DEBIT",
  "amount": "50.00",
  "reason": "Extra meal subsidy",
  "source_entity_type": "Meal",
  "source_entity_id": 51,
  "created_by": 1,
  "created_at": "2026-10-02T06:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `adjustment.create`. |
| 404 | not_found | Adjustment does not exist. |

## PUT /api/adjustments/{id}/

**Capability:** `adjustment.create`

**Request body**
```json
{
  "month": 12,
  "member": 3,
  "direction": "CREDIT",
  "amount": "30.00",
  "reason": "Balance correction",
  "source_entity_type": "Adjustment",
  "source_entity_id": 1
}
```

**Response — 200 OK**
```json
{
  "id": 2,
  "month": 12,
  "member": 3,
  "direction": "CREDIT",
  "amount": "30.00",
  "reason": "Balance correction",
  "source_entity_type": "Adjustment",
  "source_entity_id": 1,
  "created_by": 1,
  "created_at": "2026-10-02T06:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `adjustment.create`. |
| 404 | not_found | Adjustment does not exist. |

## PATCH /api/adjustments/{id}/

**Capability:** `adjustment.create`

**Request body**
```json
{
  "amount": "45.00"
}
```

**Response — 200 OK**
```json
{
  "id": 2,
  "month": 12,
  "member": 3,
  "direction": "CREDIT",
  "amount": "45.00",
  "reason": "Balance correction",
  "source_entity_type": "Adjustment",
  "source_entity_id": 1,
  "created_by": 1,
  "created_at": "2026-10-02T06:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `adjustment.create`. |
| 404 | not_found | Adjustment does not exist. |

## DELETE /api/adjustments/{id}/

**Capability:** `adjustment.create`

**Request body**
```json
{}
```

**Response — 204 No Content**
```json
{}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `adjustment.create`. |
| 404 | not_found | Adjustment does not exist. |

---

# Settings

No settings API endpoints were found under the project app code. There is a `SystemSetting` model in `apps/settings_app/models.py`, but no corresponding `urls.py`, `views.py`, or serializer-based API is implemented in the codebase.

**Status:** `NOT YET IMPLEMENTED`

---

# Notifications

## GET /api/notifications/

**Capability:** `authenticated`

**Query parameters**
- `page` (optional)
- `page_size` (optional)

**Response — 200 OK**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 5,
      "user": 3,
      "type": "deposit_approved",
      "message": "Your deposit of 2000.00 for 2026-10 was approved.",
      "entity_type": "Deposit",
      "entity_id": 17,
      "is_read": false,
      "read_at": null,
      "created_at": "2026-10-01T18:40:00Z"
    }
  ]
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 401 | authentication_failed | Request is unauthenticated. |

## POST /api/notifications/{id}/mark-read/

**Capability:** `authenticated`

**Request body**
```json
{}
```

**Response — 200 OK**
```json
{
  "id": 5,
  "user": 3,
  "type": "deposit_approved",
  "message": "Your deposit of 2000.00 for 2026-10 was approved.",
  "entity_type": "Deposit",
  "entity_id": 17,
  "is_read": true,
  "read_at": "2026-10-01T18:45:00Z",
  "created_at": "2026-10-01T18:40:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | Notification belongs to another user. |
| 404 | not_found | Notification does not exist. |

---

# Reports

## GET /api/reports/monthly/

**Capability:** `authenticated` (logical access gates enforce `report.view_own`, `report.view_all`, or manager status)

**Query parameters**
- `month_id` (required)

**Response — 200 OK**
```json
{
  "month_id": 12,
  "month_name": "2026-10",
  "status": "OPEN",
  "calculation_status": "ESTIMATED",
  "total_expense": "12345.67",
  "total_meal_units": 120,
  "meal_rate": "205.4000",
  "rounding_residual": "0.00"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | detail | `month_id` is missing. |
| 403 | detail | User lacks report access. |
| 404 | not_found | Month not found. |

## GET /api/reports/members/

**Capability:** `authenticated` (logical access gates enforce `report.view_own`, `report.view_all`, or manager status)

**Query parameters**
- `month_id` (required)

**Response — 200 OK**
```json
{
  "month_id": 12,
  "month_name": "2026-10",
  "status": "OPEN",
  "calculation_status": "ESTIMATED",
  "members": [
    {
      "id": 14,
      "member": 3,
      "member_username": "rahat",
      "month": 12,
      "joined_on": "2026-10-01",
      "left_on": null,
      "opening_balance": "0.00",
      "lunch_count": 10,
      "dinner_count": 8,
      "meal_units": 18,
      "guest_lunch_count": 0,
      "guest_dinner_count": 0,
      "guest_meal_units": 0,
      "meal_rate_applied": null,
      "meal_cost": "0.00",
      "guest_meal_cost": "0.00",
      "adjustment_total": "0.00",
      "total_cost": "0.00",
      "approved_deposit_total": "0.00",
      "closing_balance": "0.00",
      "finalized_at": null
    }
  ]
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | detail | `month_id` is missing. |
| 403 | detail | User lacks member report access. |
| 404 | not_found | Month not found. |

## GET /api/reports/balances/

**Capability:** `authenticated` (logical access gates enforce self-only access unless `report.view_all` or manager status)

**Query parameters**
- `member_id` (required)

**Response — 200 OK**
```json
{
  "member_id": 3,
  "calculation_status": "FINAL",
  "history": [
    {
      "month_id": 11,
      "month_name": "2026-09",
      "closing_balance": "125.50",
      "finalized_at": "2026-09-30T18:00:00Z"
    }
  ]
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | detail | `member_id` is missing. |
| 403 | detail | User tries to view another member’s balance without report access. |

---

# Dashboard

## GET /api/dashboard/

**Capability:** `authenticated`

**Response — 200 OK**
```json
{
  "current_month": {
    "id": 12,
    "name": "2026-10",
    "status": "OPEN"
  },
  "meal_units": 18,
  "guest_meal_units": 0,
  "closing_balance": "125.50",
  "calculation_status": "ESTIMATED",
  "pending_deposit_count": 2,
  "pending_guest_meal_count": 3,
  "total_expense_so_far": "12345.67",
  "estimated_meal_rate": "205.4000",
  "total_active_members": 8,
  "current_manager": 3,
  "reopened_count": 0
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 401 | authentication_failed | Request is unauthenticated. |

---

# Audit

No audit API endpoints were found in the project. The `AuditLog` model exists in `apps/audit/models.py`, and the code uses it as a server-side logging object, but there is no `urls.py` or API view exposed for direct audit retrieval.

**Status:** `NOT YET IMPLEMENTED`

---

# Endpoint coverage notes

- The project exposes user management through both `/api/users/` and `/api/auth/users/` because the same views are included under both prefixes.
- The app uses `DefaultRouter`-generated CRUD actions for model-backed APIs (`Months`, `Meals`, `Guest Meals`, `Deposits`, `Expenses`, `Adjustments`).
- Several actions are custom and have explicit business guards:
  - `open`, `close`, `reopen` for months
  - `correct` for meals
  - `approve`, `reject` for guest meals and deposits
  - `mark-read` for notifications
- Some app categories are intentionally not exposed as public API yet: `Settings` and `Audit`.
