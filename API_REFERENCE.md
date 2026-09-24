# API Reference

This document reflects the current project code in the repository as of the generated state of the app. It covers the routes registered in `urls.py`, the behavior in `views.py`, and the fields returned by each serializer in `serializers.py`.

## Summary table

| Method | Path                               | Capability                                            | Description                                                  |
| ------ | ---------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------ |
| POST   | /api/auth/login/                   | public                                                | Authenticate a user and return JWT payload plus user summary |
| POST   | /api/auth/refresh/                 | public                                                | Refresh an access token                                      |
| POST   | /api/auth/logout/                  | authenticated                                         | Blacklist a refresh token                                    |
| GET    | /api/auth/me/                      | authenticated                                         | Return current user profile and capabilities                 |
| POST   | /api/auth/password/change/         | authenticated                                         | Change the current user password                             |
| GET    | /api/months/                       | month.view                                            | List months                                                  |
| POST   | /api/months/                       | month.create                                          | Create a month                                               |
| GET    | /api/months/{id}/                  | month.view                                            | Retrieve a month                                             |
| PUT    | /api/months/{id}/                  | month.create                                          | Update month details                                         |
| PATCH  | /api/months/{id}/                  | month.create                                          | Partial update month details                                 |
| DELETE | /api/months/{id}/                  | authenticated                                         | Delete a month                                               |
| POST   | /api/months/{id}/open/             | month.open                                            | Open a PLANNED month                                         |
| POST   | /api/months/{id}/close/            | month.close                                           | Close an OPEN month                                          |
| POST   | /api/months/{id}/reopen/           | month.reopen                                          | Reopen a CLOSED month                                        |
| GET    | /api/months/{id}/members/          | month.view                                            | List month members for a month                               |
| PUT    | /api/months/{id}/manager/          | manager.assign                                        | Assign manager for the month                                 |
| GET    | /api/meals/                        | meal.view_all or meal.view_own                        | List meals                                                   |
| POST   | /api/meals/                        | meal.submit                                           | Create a meal                                                |
| GET    | /api/meals/{id}/                   | meal.view_all or meal.view_own                        | Retrieve a meal                                              |
| PATCH  | /api/meals/{id}/                   | meal.view_all or meal.view_own                        | Partial update a meal                                        |
| DELETE | /api/meals/{id}/                   | authenticated                                         | Delete a meal                                                |
| PATCH  | /api/meals/{id}/correct/           | meal.correct                                          | Correct a meal record                                        |
| GET    | /api/guest-meals/                  | guest_meal.view_all or guest_meal.view_own            | List guest meals                                             |
| POST   | /api/guest-meals/                  | guest_meal.submit                                     | Create a guest meal                                          |
| GET    | /api/guest-meals/{id}/             | guest_meal.view_all or guest_meal.view_own            | Retrieve a guest meal                                        |
| PATCH  | /api/guest-meals/{id}/             | guest_meal.view_all or guest_meal.view_own            | Partial update a guest meal                                  |
| DELETE | /api/guest-meals/{id}/             | authenticated                                         | Delete a guest meal                                          |
| POST   | /api/guest-meals/{id}/approve/     | guest_meal.approve                                    | Approve a pending guest meal                                 |
| POST   | /api/guest-meals/{id}/reject/      | guest_meal.approve                                    | Reject a guest meal                                          |
| GET    | /api/deposits/                     | deposit.approve or deposit.view_own                   | List deposits                                                |
| POST   | /api/deposits/                     | deposit.approve or deposit.view_own                   | Create a deposit                                             |
| GET    | /api/deposits/{id}/                | deposit.approve or deposit.view_own                   | Retrieve a deposit                                           |
| PATCH  | /api/deposits/{id}/                | deposit.approve or deposit.view_own                   | Partial update a deposit                                     |
| DELETE | /api/deposits/{id}/                | authenticated                                         | Delete a deposit                                             |
| POST   | /api/deposits/{id}/approve/        | deposit.approve                                       | Approve a pending deposit                                    |
| POST   | /api/deposits/{id}/reject/         | deposit.approve                                       | Reject a pending deposit                                     |
| GET    | /api/expenses/                     | expense.create                                        | List expenses                                                |
| POST   | /api/expenses/                     | expense.create                                        | Create an expense                                            |
| GET    | /api/expenses/{id}/                | expense.create                                        | Retrieve an expense                                          |
| PUT    | /api/expenses/{id}/                | expense.create                                        | Update an expense                                            |
| PATCH  | /api/expenses/{id}/                | expense.create                                        | Partial update an expense                                    |
| DELETE | /api/expenses/{id}/                | expense.delete                                        | Soft-delete an expense                                       |
| GET    | /api/adjustments/                  | adjustment.create                                     | List adjustments                                             |
| POST   | /api/adjustments/                  | adjustment.create                                     | Create an adjustment                                         |
| GET    | /api/adjustments/{id}/             | adjustment.create                                     | Retrieve an adjustment                                       |
| PUT    | /api/adjustments/{id}/             | adjustment.create                                     | Update an adjustment                                         |
| PATCH  | /api/adjustments/{id}/             | adjustment.create                                     | Partial update an adjustment                                 |
| DELETE | /api/adjustments/{id}/             | authenticated                                         | Delete an adjustment                                         |
| GET    | /api/notifications/                | authenticated                                         | List current user notifications                              |
| POST   | /api/notifications/{id}/mark-read/ | authenticated                                         | Mark one notification as read                                |
| GET    | /api/reports/monthly/              | report.view_own or report.view_all or current manager | Monthly totals report                                        |
| GET    | /api/reports/members/              | report.view_own or report.view_all or current manager | Monthly member report                                        |
| GET    | /api/reports/balances/             | report.view_own or report.view_all or current manager | Balance history report                                       |
| GET    | /api/dashboard/                    | authenticated                                         | Dashboard summary for the current user                       |
| N/A    | Settings API                       | NOT YET IMPLEMENTED                                   | No route file or view layer exists yet                       |
| N/A    | Audit API                          | NOT YET IMPLEMENTED                                   | No route file or view layer exists yet                       |

---

# Auth

## POST /api/auth/login/

**Capability:** `public`

**Request body**

```json
{
  "username": "alice",
  "password": "StrongPass123!"
}
```

**Response — 200 OK**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhbGljZSIsImV4cCI6MTYwMDAwMDAwMH0.example",
  "access": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhbGljZSIsImV4cCI6MTYwMDAwMDAwMH0.example",
  "user": {
    "id": 7,
    "username": "alice",
    "email": "",
    "role": "MEMBER",
    "must_change_password": true
  }
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | validation_error | Invalid username/password or serializer validation failure |

## POST /api/auth/refresh/

**Capability:** `public`

**Request body**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.example-refresh-token"
}
```

**Response — 200 OK**

```json
{
  "access": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.example-new-access-token",
  "refresh": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.example-refresh-token"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | token_not_valid | Token is invalid, expired, or malformed |

## POST /api/auth/logout/

**Capability:** `authenticated`

**Request body**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.example-refresh-token"
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
| 400 | invalid_token | Refresh token missing, invalid, or expired |

## GET /api/auth/me/

**Capability:** `authenticated`

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "id": 7,
  "username": "alice",
  "email": "",
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
| 401 | authentication_failed | Request is not authenticated |

## POST /api/auth/password/change/

**Capability:** `authenticated`

**Request body**

```json
{
  "current_password": "OldPass123!",
  "new_password": "NewStrongPass456!",
  "confirm_password": "NewStrongPass456!"
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
| 400 | validation_error | Current password wrong, new password invalid, or confirmation mismatch |

---

# Users

No dedicated `/api/users/` CRUD routes are defined in the current project. The only user-facing endpoints are the auth endpoints above.

---

# Months

## GET /api/months/

**Capability:** `month.view`

**Query parameters**

- None

**Request body**

```json
{}
```

**Response — 200 OK**

```json
[
  {
    "id": 1,
    "name": "2026-10",
    "start_date": "2026-10-01",
    "end_date": "2026-10-31",
    "status": "OPEN",
    "final_meal_rate": null,
    "final_total_expense": null,
    "final_total_meal_units": null,
    "rounding_residual": null,
    "closed_at": null,
    "closed_by": null,
    "reopened_count": 0,
    "last_reopened_at": null,
    "created_by": 7,
    "created_at": "2026-09-20T12:00:00Z",
    "updated_at": "2026-09-20T12:00:00Z"
  }
]
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | No `month.view` capability |

## POST /api/months/

**Capability:** `month.create`

**Request body**

```json
{
  "name": "2026-11",
  "start_date": "2026-11-01",
  "end_date": "2026-11-30"
}
```

**Response — 201 Created**

```json
{
  "id": 2,
  "name": "2026-11",
  "start_date": "2026-11-01",
  "end_date": "2026-11-30",
  "status": "PLANNED",
  "final_meal_rate": null,
  "final_total_expense": null,
  "final_total_meal_units": null,
  "rounding_residual": null,
  "closed_at": null,
  "closed_by": null,
  "reopened_count": 0,
  "last_reopened_at": null,
  "created_by": 7,
  "created_at": "2026-09-20T12:00:00Z",
  "updated_at": "2026-09-20T12:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | validation_error | Invalid month dates or overlapping month range |
| 403 | permission_denied | No `month.create` capability |

## GET /api/months/{id}/

**Capability:** `month.view`

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "id": 1,
  "name": "2026-10",
  "start_date": "2026-10-01",
  "end_date": "2026-10-31",
  "status": "OPEN",
  "final_meal_rate": null,
  "final_total_expense": null,
  "final_total_meal_units": null,
  "rounding_residual": null,
  "closed_at": null,
  "closed_by": null,
  "reopened_count": 0,
  "last_reopened_at": null,
  "created_by": 7,
  "created_at": "2026-09-20T12:00:00Z",
  "updated_at": "2026-09-20T12:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | No `month.view` capability |
| 404 | not_found | Object not found |

## PUT /api/months/{id}/

**Capability:** `month.create`

**Request body**

```json
{
  "name": "2026-10A",
  "start_date": "2026-10-01",
  "end_date": "2026-10-31"
}
```

**Response — 200 OK**

```json
{
  "id": 1,
  "name": "2026-10A",
  "start_date": "2026-10-01",
  "end_date": "2026-10-31",
  "status": "OPEN",
  "final_meal_rate": null,
  "final_total_expense": null,
  "final_total_meal_units": null,
  "rounding_residual": null,
  "closed_at": null,
  "closed_by": null,
  "reopened_count": 0,
  "last_reopened_at": null,
  "created_by": 7,
  "created_at": "2026-09-20T12:00:00Z",
  "updated_at": "2026-09-20T12:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | validation_error | Invalid month date range or overlapping month |
| 403 | permission_denied | No `month.create` capability |

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
  "id": 1,
  "name": "2026-10",
  "start_date": "2026-10-01",
  "end_date": "2026-10-31",
  "status": "OPEN",
  "final_meal_rate": null,
  "final_total_expense": null,
  "final_total_meal_units": null,
  "rounding_residual": null,
  "closed_at": null,
  "closed_by": null,
  "reopened_count": 0,
  "last_reopened_at": null,
  "created_by": 7,
  "created_at": "2026-09-20T12:00:00Z",
  "updated_at": "2026-09-20T12:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | validation_error | Invalid partial-update payload |
| 403 | permission_denied | No `month.create` capability |

## DELETE /api/months/{id}/

**Capability:** `authenticated` (default route permission, no capability override in code)

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
| 403 | permission_denied | Request not authenticated |
| 404 | not_found | Object not found |

## POST /api/months/{id}/open/

**Capability:** `month.open`

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "id": 1,
  "name": "2026-10",
  "start_date": "2026-10-01",
  "end_date": "2026-10-31",
  "status": "OPEN",
  "final_meal_rate": null,
  "final_total_expense": null,
  "final_total_meal_units": null,
  "rounding_residual": null,
  "closed_at": null,
  "closed_by": null,
  "reopened_count": 0,
  "last_reopened_at": null,
  "created_by": 7,
  "created_at": "2026-09-20T12:00:00Z",
  "updated_at": "2026-09-20T12:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | open_month_conflict | Another month is already OPEN |
| 400 | month_status_invalid | Month status is not PLANNED |
| 403 | permission_denied | No `month.open` capability |

## POST /api/months/{id}/close/

**Capability:** `month.close`

**Request body**

```json
{
  "idempotency_key": "close-2026-10-20261031"
}
```

**Response — 200 OK**

```json
{
  "id": 1,
  "name": "2026-10",
  "start_date": "2026-10-01",
  "end_date": "2026-10-31",
  "status": "CLOSED",
  "final_meal_rate": "0.9565",
  "final_total_expense": "12345.67",
  "final_total_meal_units": 215,
  "rounding_residual": "0.01",
  "closed_at": "2026-10-31T18:30:00Z",
  "closed_by": 7,
  "reopened_count": 0,
  "last_reopened_at": null,
  "created_by": 7,
  "created_at": "2026-09-20T12:00:00Z",
  "updated_at": "2026-10-31T18:30:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_close_blocked | Closure validation failed; `failures` contains the reasons, e.g. pending deposits, pending guest meals, no active manager, no meal units, no expense |
| 400 | month_status_invalid | Month is not OPEN |
| 200 | already_processed | Same idempotency key already processed |
| 403 | permission_denied | No `month.close` capability |

## POST /api/months/{id}/reopen/

**Capability:** `month.reopen`

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "id": 1,
  "name": "2026-10",
  "start_date": "2026-10-01",
  "end_date": "2026-10-31",
  "status": "OPEN",
  "final_meal_rate": null,
  "final_total_expense": null,
  "final_total_meal_units": null,
  "rounding_residual": null,
  "closed_at": null,
  "closed_by": null,
  "reopened_count": 1,
  "last_reopened_at": "2026-11-02T09:10:00Z",
  "created_by": 7,
  "created_at": "2026-09-20T12:00:00Z",
  "updated_at": "2026-11-02T09:10:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_status_invalid | Month is not CLOSED |
| 400 | open_month_conflict | Another month is already OPEN |
| 403 | permission_denied | No `month.reopen` capability |

## GET /api/months/{id}/members/

**Capability:** `month.view`

**Request body**

```json
{}
```

**Response — 200 OK**

```json
[
  {
    "id": 18,
    "member": 7,
    "member_username": "alice",
    "month": 1,
    "joined_on": "2026-10-01",
    "left_on": null,
    "opening_balance": "0.00",
    "lunch_count": 12,
    "dinner_count": 15,
    "meal_units": 27,
    "guest_lunch_count": 0,
    "guest_dinner_count": 0,
    "guest_meal_units": 0,
    "meal_rate_applied": "0.9565",
    "meal_cost": "25.84",
    "guest_meal_cost": "0.00",
    "adjustment_total": "0.00",
    "total_cost": "25.84",
    "approved_deposit_total": "0.00",
    "closing_balance": "-25.84",
    "finalized_at": null
  }
]
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | No `month.view` capability |
| 404 | not_found | Month not found |

## PUT /api/months/{id}/manager/

**Capability:** `manager.assign`

**Request body**

```json
{
  "user_id": 12
}
```

**Response — 200 OK**

```json
{
  "id": 5,
  "month": 1,
  "user": 12,
  "assigned_by": 7,
  "unassigned_by": null,
  "assigned_at": "2026-10-01T09:00:00Z",
  "unassigned_at": null
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | user_id_required | `user_id` not supplied |
| 400 | user_not_active | Target user is inactive |
| 400 | invalid_manager_target | Target user must have MEMBER role |
| 400 | manager_already_current | Target user is already the active manager |
| 403 | permission_denied | No `manager.assign` capability |
| 404 | user_not_found | Target user does not exist |

---

# Meals

## GET /api/meals/

**Capability:** `meal.view_all` or `meal.view_own`

**Query parameters**

- `month` or `month_id` — optional month filter

**Request body**

```json
{}
```

**Response — 200 OK**

```json
[
  {
    "id": 5,
    "member": 7,
    "month": 1,
    "meal_date": "2026-10-01",
    "lunch": true,
    "dinner": false,
    "last_corrected_by": null,
    "last_corrected_at": null,
    "correction_reason": "",
    "created_at": "2026-10-01T08:15:00Z",
    "updated_at": "2026-10-01T08:15:00Z"
  }
]
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks `meal.view_all` or `meal.view_own` |

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
  "id": 5,
  "member": 7,
  "month": 1,
  "meal_date": "2026-10-01",
  "lunch": true,
  "dinner": false,
  "last_corrected_by": null,
  "last_corrected_at": null,
  "correction_reason": "",
  "created_at": "2026-10-01T08:15:00Z",
  "updated_at": "2026-10-01T08:15:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | no_month_for_date | `meal_date` falls outside any PLANNED/OPEN month |
| 400 | deadline_passed | Submission is after the configured deadline for that date |
| 403 | permission_denied | No `meal.submit` capability |

## GET /api/meals/{id}/

**Capability:** `meal.view_all` or `meal.view_own`

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "id": 5,
  "member": 7,
  "month": 1,
  "meal_date": "2026-10-01",
  "lunch": true,
  "dinner": false,
  "last_corrected_by": null,
  "last_corrected_at": null,
  "correction_reason": "",
  "created_at": "2026-10-01T08:15:00Z",
  "updated_at": "2026-10-01T08:15:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks the required meal-view capability |
| 404 | not_found | Meal not found |

## PATCH /api/meals/{id}/

**Capability:** `meal.view_all` or `meal.view_own`

**Request body**

```json
{
  "lunch": false,
  "dinner": true
}
```

**Response — 200 OK**

```json
{
  "id": 5,
  "member": 7,
  "month": 1,
  "meal_date": "2026-10-01",
  "lunch": false,
  "dinner": true,
  "last_corrected_by": null,
  "last_corrected_at": null,
  "correction_reason": "",
  "created_at": "2026-10-01T08:15:00Z",
  "updated_at": "2026-10-01T08:15:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | validation_error | Serializer validation fails |
| 403 | permission_denied | User lacks the view capability |
| 404 | not_found | Meal not found |

## DELETE /api/meals/{id}/

**Capability:** `authenticated` (default route permission only)

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
| 403 | permission_denied | Request not authenticated |
| 404 | not_found | Meal not found |

## PATCH /api/meals/{id}/correct/

**Capability:** `meal.correct`

**Request body**

```json
{
  "lunch": true,
  "dinner": false,
  "reason": "Lunch was missed and corrected."
}
```

**Response — 200 OK**

```json
{
  "id": 5,
  "member": 7,
  "month": 1,
  "meal_date": "2026-10-01",
  "lunch": true,
  "dinner": false,
  "last_corrected_by": 9,
  "last_corrected_at": "2026-10-02T11:15:00Z",
  "correction_reason": "Lunch was missed and corrected.",
  "created_at": "2026-10-01T08:15:00Z",
  "updated_at": "2026-10-02T11:15:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_closed | Meal is in a CLOSED month and cannot be corrected |
| 400 | validation_error | `lunch` and `dinner` are both false, or reason is too short |
| 403 | permission_denied | No `meal.correct` capability or current-manager allowance |

---

# Guest Meals

## GET /api/guest-meals/

**Capability:** `guest_meal.view_all` or `guest_meal.view_own`

**Query parameters**

- None

**Request body**

```json
{}
```

**Response — 200 OK**

```json
[
  {
    "id": 3,
    "member": 7,
    "month": 1,
    "meal_date": "2026-10-08",
    "lunch_quantity": 1,
    "dinner_quantity": 0,
    "status": "PENDING",
    "rejection_reason": "",
    "remarks": "Family guest",
    "submitted_at": "2026-10-07T18:00:00Z",
    "processed_at": null,
    "processed_by": null
  }
]
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks view capability |

## POST /api/guest-meals/

**Capability:** `guest_meal.submit`

**Request body**

```json
{
  "meal_date": "2026-10-08",
  "lunch_quantity": 1,
  "dinner_quantity": 0,
  "remarks": "Family guest"
}
```

**Response — 201 Created**

```json
{
  "id": 3,
  "member": 7,
  "month": 1,
  "meal_date": "2026-10-08",
  "lunch_quantity": 1,
  "dinner_quantity": 0,
  "status": "PENDING",
  "rejection_reason": "",
  "remarks": "Family guest",
  "submitted_at": "2026-10-07T18:00:00Z",
  "processed_at": null,
  "processed_by": null
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | no_month_for_date | `meal_date` falls outside any PLANNED/OPEN month |
| 400 | meal_date | Duplicate guest meal already exists for that user/date |
| 403 | permission_denied | No `guest_meal.submit` capability |

## GET /api/guest-meals/{id}/

**Capability:** `guest_meal.view_all` or `guest_meal.view_own`

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "id": 3,
  "member": 7,
  "month": 1,
  "meal_date": "2026-10-08",
  "lunch_quantity": 1,
  "dinner_quantity": 0,
  "status": "PENDING",
  "rejection_reason": "",
  "remarks": "Family guest",
  "submitted_at": "2026-10-07T18:00:00Z",
  "processed_at": null,
  "processed_by": null
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks view capability |
| 404 | not_found | Guest meal not found |

## PATCH /api/guest-meals/{id}/

**Capability:** `guest_meal.view_all` or `guest_meal.view_own`

**Request body**

```json
{
  "remarks": "Updated notes",
  "lunch_quantity": 2
}
```

**Response — 200 OK**

```json
{
  "id": 3,
  "member": 7,
  "month": 1,
  "meal_date": "2026-10-08",
  "lunch_quantity": 2,
  "dinner_quantity": 0,
  "status": "PENDING",
  "rejection_reason": "",
  "remarks": "Updated notes",
  "submitted_at": "2026-10-07T18:00:00Z",
  "processed_at": null,
  "processed_by": null
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | validation_error | Validation failed |
| 403 | permission_denied | No access |
| 404 | not_found | Guest meal not found |

## DELETE /api/guest-meals/{id}/

**Capability:** `authenticated` (default route permission only)

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
| 403 | permission_denied | Not authenticated |
| 404 | not_found | Guest meal not found |

## POST /api/guest-meals/{id}/approve/

**Capability:** `guest_meal.approve`

**Request body**

```json
{
  "reason": "Approved for guest visit"
}
```

**Response — 200 OK**

```json
{
  "id": 3,
  "member": 7,
  "month": 1,
  "meal_date": "2026-10-08",
  "lunch_quantity": 1,
  "dinner_quantity": 0,
  "status": "APPROVED",
  "rejection_reason": "",
  "remarks": "Family guest",
  "submitted_at": "2026-10-07T18:00:00Z",
  "processed_at": "2026-10-09T05:00:00Z",
  "processed_by": 9
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | rejected_guest_meal | Guest meal status is REJECTED and cannot be approved |
| 403 | permission_denied | No `guest_meal.approve` capability or manager fallback |

## POST /api/guest-meals/{id}/reject/

**Capability:** `guest_meal.approve`

**Request body**

```json
{
  "reason": "Guest meal exceeds allowed limit"
}
```

**Response — 200 OK**

```json
{
  "id": 3,
  "member": 7,
  "month": 1,
  "meal_date": "2026-10-08",
  "lunch_quantity": 1,
  "dinner_quantity": 0,
  "status": "REJECTED",
  "rejection_reason": "Guest meal exceeds allowed limit",
  "remarks": "Family guest",
  "submitted_at": "2026-10-07T18:00:00Z",
  "processed_at": "2026-10-09T05:00:00Z",
  "processed_by": 9
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | approved_guest_meal | Guest meal status is APPROVED and cannot be rejected |
| 403 | permission_denied | No `guest_meal.approve` capability or manager fallback |

---

# Deposits

## GET /api/deposits/

**Capability:** `deposit.approve` or `deposit.view_own`

**Query parameters**

- None

**Request body**

```json
{}
```

**Response — 200 OK**

```json
[
  {
    "id": 11,
    "member": 7,
    "month": 1,
    "amount": "2500.00",
    "payment_method": "BKASH",
    "transaction_reference": "BKASH-2567",
    "payment_date": "2026-10-04",
    "status": "PENDING",
    "rejection_reason": "",
    "submitted_at": "2026-10-04T09:30:00Z",
    "processed_at": null,
    "processed_by": null,
    "note": "Top-up"
  }
]
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User lacks the required deposit permission |

## POST /api/deposits/

**Capability:** `deposit.approve` or `deposit.view_own`

**Request body**

```json
{
  "amount": "2500.00",
  "payment_method": "BKASH",
  "transaction_reference": "BKASH-2567",
  "payment_date": "2026-10-04",
  "note": "Top-up"
}
```

**Response — 201 Created**

```json
{
  "id": 11,
  "member": 7,
  "month": 1,
  "amount": "2500.00",
  "payment_method": "BKASH",
  "transaction_reference": "BKASH-2567",
  "payment_date": "2026-10-04",
  "status": "PENDING",
  "rejection_reason": "",
  "submitted_at": "2026-10-04T09:30:00Z",
  "processed_at": null,
  "processed_by": null,
  "note": "Top-up"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_not_open | No OPEN month exists or payment date is outside the OPEN month |
| 400 | validation_error | `amount` <= 0, or transaction reference missing for non-CASH |
| 403 | permission_denied | No matching deposit capability |

## GET /api/deposits/{id}/

**Capability:** `deposit.approve` or `deposit.view_own`

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "id": 11,
  "member": 7,
  "month": 1,
  "amount": "2500.00",
  "payment_method": "BKASH",
  "transaction_reference": "BKASH-2567",
  "payment_date": "2026-10-04",
  "status": "PENDING",
  "rejection_reason": "",
  "submitted_at": "2026-10-04T09:30:00Z",
  "processed_at": null,
  "processed_by": null,
  "note": "Top-up"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | User cannot view this deposit |
| 404 | not_found | Deposit not found |

## PATCH /api/deposits/{id}/

**Capability:** `deposit.approve` or `deposit.view_own`

**Request body**

```json
{
  "note": "Updated note"
}
```

**Response — 200 OK**

```json
{
  "id": 11,
  "member": 7,
  "month": 1,
  "amount": "2500.00",
  "payment_method": "BKASH",
  "transaction_reference": "BKASH-2567",
  "payment_date": "2026-10-04",
  "status": "PENDING",
  "rejection_reason": "",
  "submitted_at": "2026-10-04T09:30:00Z",
  "processed_at": null,
  "processed_by": null,
  "note": "Updated note"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | validation_error | Invalid deposit update |
| 403 | permission_denied | No access |
| 404 | not_found | Deposit not found |

## DELETE /api/deposits/{id}/

**Capability:** `authenticated` (default route permission only)

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
| 403 | permission_denied | Not authenticated |
| 404 | not_found | Deposit not found |

## POST /api/deposits/{id}/approve/

**Capability:** `deposit.approve`

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "id": 11,
  "member": 7,
  "month": 1,
  "amount": "2500.00",
  "payment_method": "BKASH",
  "transaction_reference": "BKASH-2567",
  "payment_date": "2026-10-04",
  "status": "APPROVED",
  "rejection_reason": "",
  "submitted_at": "2026-10-04T09:30:00Z",
  "processed_at": "2026-10-05T10:00:00Z",
  "processed_by": 9,
  "note": "Top-up"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | deposit_status_invalid | Deposit status is not PENDING |
| 400 | month_closed | Deposit month is no longer OPEN |
| 403 | permission_denied | No `deposit.approve` capability or manager fallback |

## POST /api/deposits/{id}/reject/

**Capability:** `deposit.approve`

**Request body**

```json
{
  "reason": "Transaction reference mismatch"
}
```

**Response — 200 OK**

```json
{
  "id": 11,
  "member": 7,
  "month": 1,
  "amount": "2500.00",
  "payment_method": "BKASH",
  "transaction_reference": "BKASH-2567",
  "payment_date": "2026-10-04",
  "status": "REJECTED",
  "rejection_reason": "Transaction reference mismatch",
  "submitted_at": "2026-10-04T09:30:00Z",
  "processed_at": "2026-10-05T10:00:00Z",
  "processed_by": 9,
  "note": "Top-up"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | reason_required | Reject reason missing |
| 400 | deposit_status_invalid | Deposit status is not PENDING |
| 400 | month_closed | Deposit month is no longer OPEN |
| 403 | permission_denied | No `deposit.approve` capability or manager fallback |

---

# Expenses

## GET /api/expenses/

**Capability:** `expense.create`

**Query parameters**

- None

**Request body**

```json
{}
```

**Response — 200 OK**

```json
[
  {
    "id": 14,
    "month": 1,
    "created_by": 7,
    "category": "Grocery",
    "amount": "1250.00",
    "expense_date": "2026-10-05",
    "description": "Groceries",
    "is_deleted": false,
    "deleted_at": null,
    "deleted_by": null,
    "delete_reason": "",
    "created_at": "2026-10-05T12:00:00Z",
    "updated_at": "2026-10-05T12:00:00Z"
  }
]
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | No `expense.create` capability |

## POST /api/expenses/

**Capability:** `expense.create`

**Request body**

```json
{
  "category": "Grocery",
  "amount": "1250.00",
  "expense_date": "2026-10-05",
  "description": "Groceries"
}
```

**Response — 201 Created**

```json
{
  "id": 14,
  "month": 1,
  "created_by": 7,
  "category": "Grocery",
  "amount": "1250.00",
  "expense_date": "2026-10-05",
  "description": "Groceries",
  "is_deleted": false,
  "deleted_at": null,
  "deleted_by": null,
  "delete_reason": "",
  "created_at": "2026-10-05T12:00:00Z",
  "updated_at": "2026-10-05T12:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_not_open | No current OPEN month or expense date outside that month |
| 400 | validation_error | Amount <= 0 or missing description |
| 403 | permission_denied | No `expense.create` capability |

## GET /api/expenses/{id}/

**Capability:** `expense.create`

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "id": 14,
  "month": 1,
  "created_by": 7,
  "category": "Grocery",
  "amount": "1250.00",
  "expense_date": "2026-10-05",
  "description": "Groceries",
  "is_deleted": false,
  "deleted_at": null,
  "deleted_by": null,
  "delete_reason": "",
  "created_at": "2026-10-05T12:00:00Z",
  "updated_at": "2026-10-05T12:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | No `expense.create` capability |
| 404 | not_found | Expense not found |

## PUT /api/expenses/{id}/

**Capability:** `expense.create`

**Request body**

```json
{
  "category": "Gas",
  "amount": "350.00",
  "expense_date": "2026-10-06",
  "description": "Fuel top-up"
}
```

**Response — 200 OK**

```json
{
  "id": 14,
  "month": 1,
  "created_by": 7,
  "category": "Gas",
  "amount": "350.00",
  "expense_date": "2026-10-06",
  "description": "Fuel top-up",
  "is_deleted": false,
  "deleted_at": null,
  "deleted_by": null,
  "delete_reason": "",
  "created_at": "2026-10-05T12:00:00Z",
  "updated_at": "2026-10-06T11:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_closed | Expense month is not OPEN |
| 400 | validation_error | Invalid amount/description/date |
| 403 | permission_denied | No `expense.create` capability |

## PATCH /api/expenses/{id}/

**Capability:** `expense.create`

**Request body**

```json
{
  "description": "Fuel top-up (edited)"
}
```

**Response — 200 OK**

```json
{
  "id": 14,
  "month": 1,
  "created_by": 7,
  "category": "Gas",
  "amount": "350.00",
  "expense_date": "2026-10-06",
  "description": "Fuel top-up (edited)",
  "is_deleted": false,
  "deleted_at": null,
  "deleted_by": null,
  "delete_reason": "",
  "created_at": "2026-10-05T12:00:00Z",
  "updated_at": "2026-10-06T11:05:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_closed | Expense month is not OPEN |
| 400 | validation_error | Invalid payload |
| 403 | permission_denied | No `expense.create` capability |

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
| 400 | reason_required | `reason` missing or blank |
| 400 | month_closed | Expense month is not OPEN |
| 403 | permission_denied | No `expense.delete` capability |
| 404 | not_found | Expense not found |

---

# Adjustments

## GET /api/adjustments/

**Capability:** `adjustment.create`

**Query parameters**

- None

**Request body**

```json
{}
```

**Response — 200 OK**

```json
[
  {
    "id": 8,
    "month": 1,
    "member": 7,
    "direction": "DEBIT",
    "amount": "50.00",
    "reason": "Adjustment for late settlement",
    "source_entity_type": "",
    "source_entity_id": null,
    "created_by": 9,
    "created_at": "2026-10-20T10:00:00Z"
  }
]
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | No `adjustment.create` capability |

## POST /api/adjustments/

**Capability:** `adjustment.create`

**Request body**

```json
{
  "month": 1,
  "member": 7,
  "direction": "DEBIT",
  "amount": "50.00",
  "reason": "Adjustment for late settlement"
}
```

**Response — 201 Created**

```json
{
  "id": 8,
  "month": 1,
  "member": 7,
  "direction": "DEBIT",
  "amount": "50.00",
  "reason": "Adjustment for late settlement",
  "source_entity_type": "",
  "source_entity_id": null,
  "created_by": 9,
  "created_at": "2026-10-20T10:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_not_open | `month` is not OPEN |
| 400 | validation_error | `amount` <= 0 or blank reason |
| 403 | permission_denied | No `adjustment.create` capability |

## GET /api/adjustments/{id}/

**Capability:** `adjustment.create`

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "id": 8,
  "month": 1,
  "member": 7,
  "direction": "DEBIT",
  "amount": "50.00",
  "reason": "Adjustment for late settlement",
  "source_entity_type": "",
  "source_entity_id": null,
  "created_by": 9,
  "created_at": "2026-10-20T10:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | No `adjustment.create` capability |
| 404 | not_found | Adjustment not found |

## PUT /api/adjustments/{id}/

**Capability:** `adjustment.create`

**Request body**

```json
{
  "month": 1,
  "member": 7,
  "direction": "CREDIT",
  "amount": "25.00",
  "reason": "Revised settlement"
}
```

**Response — 200 OK**

```json
{
  "id": 8,
  "month": 1,
  "member": 7,
  "direction": "CREDIT",
  "amount": "25.00",
  "reason": "Revised settlement",
  "source_entity_type": "",
  "source_entity_id": null,
  "created_by": 9,
  "created_at": "2026-10-20T10:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_not_open | Adjustment month is not OPEN |
| 400 | validation_error | Invalid payload |
| 403 | permission_denied | No `adjustment.create` capability |

## PATCH /api/adjustments/{id}/

**Capability:** `adjustment.create`

**Request body**

```json
{
  "amount": "30.00"
}
```

**Response — 200 OK**

```json
{
  "id": 8,
  "month": 1,
  "member": 7,
  "direction": "DEBIT",
  "amount": "30.00",
  "reason": "Adjustment for late settlement",
  "source_entity_type": "",
  "source_entity_id": null,
  "created_by": 9,
  "created_at": "2026-10-20T10:00:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_not_open | Adjustment month is not OPEN |
| 400 | validation_error | Invalid payload |
| 403 | permission_denied | No `adjustment.create` capability |

## DELETE /api/adjustments/{id}/

**Capability:** `authenticated` (default route permission only)

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
| 403 | permission_denied | Not authenticated |
| 404 | not_found | Adjustment not found |

---

# Settings

## NOT YET IMPLEMENTED

No `apps/settings_app/urls.py` or settings API views were found in the repository, so no live settings endpoints are registered at this time.

**Capability:** N/A

**Error responses**
| Status | Code | When |
|---|---|---|
| N/A | N/A | No settings routes implemented |

---

# Notifications

## GET /api/notifications/

**Capability:** `authenticated`

**Query parameters**

- None

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 15,
      "user": 7,
      "type": "MONTH_CLOSED",
      "message": "Month 2026-10 closed. Your closing balance is -25.84.",
      "entity_type": "MonthMember",
      "entity_id": 18,
      "is_read": false,
      "read_at": null,
      "created_at": "2026-10-31T18:40:00Z"
    },
    {
      "id": 14,
      "user": 7,
      "type": "deposit_approved",
      "message": "Your deposit of 2500.00 for 2026-10 was approved.",
      "entity_type": "Deposit",
      "entity_id": 11,
      "is_read": true,
      "read_at": "2026-10-31T19:00:00Z",
      "created_at": "2026-10-31T18:35:00Z"
    }
  ]
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 401 | authentication_failed | Not authenticated |

## POST /api/notifications/{id}/mark-read/

**Capability:** `authenticated`

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "id": 15,
  "user": 7,
  "type": "MONTH_CLOSED",
  "message": "Month 2026-10 closed. Your closing balance is -25.84.",
  "entity_type": "MonthMember",
  "entity_id": 18,
  "is_read": true,
  "read_at": "2026-10-31T18:45:00Z",
  "created_at": "2026-10-31T18:40:00Z"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 403 | permission_denied | Notification belongs to another user |
| 404 | not_found | Notification not found |

---

# Reports

## GET /api/reports/monthly/

**Capability:** `report.view_own` or `report.view_all` or current manager fallback

**Query parameters**

- `month_id` — required

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "month_id": 1,
  "month_name": "2026-10",
  "status": "OPEN",
  "calculation_status": "ESTIMATED",
  "total_expense": "15420.00",
  "total_meal_units": 318,
  "meal_rate": "0.9565",
  "rounding_residual": "0.00"
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_id_required | `month_id` missing |
| 403 | permission_denied | No report permission |
| 404 | not_found | Month does not exist |

## GET /api/reports/members/

**Capability:** `report.view_own` or `report.view_all` or current manager fallback

**Query parameters**

- `month_id` — required

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "month_id": 1,
  "month_name": "2026-10",
  "status": "OPEN",
  "calculation_status": "ESTIMATED",
  "members": [
    {
      "id": 18,
      "member": 7,
      "month": 1,
      "joined_on": "2026-10-01",
      "left_on": null,
      "meal_units": 27,
      "guest_meal_units": 0,
      "opening_balance": "0.00",
      "adjustment_total": "0.00",
      "approved_deposit_total": "0.00",
      "closing_balance": "-25.84",
      "finalized_at": null
    }
  ]
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | month_id_required | `month_id` missing |
| 403 | permission_denied | No report permission |
| 404 | not_found | Month does not exist |

## GET /api/reports/balances/

**Capability:** `report.view_own` or `report.view_all` or current manager fallback

**Query parameters**

- `member_id` — required

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "member_id": 7,
  "calculation_status": "FINAL",
  "history": [
    {
      "month_id": 1,
      "month_name": "2026-09",
      "closing_balance": "12.50",
      "finalized_at": "2026-09-30T18:00:00Z"
    },
    {
      "month_id": 2,
      "month_name": "2026-10",
      "closing_balance": "-25.84",
      "finalized_at": "2026-10-31T18:00:00Z"
    }
  ]
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 400 | member_id_required | `member_id` missing |
| 403 | permission_denied | Requester is not the same user and lacks `report.view_all` or manager access |

---

# Dashboard

## GET /api/dashboard/

**Capability:** `authenticated`

**Query parameters**

- None

**Request body**

```json
{}
```

**Response — 200 OK**

```json
{
  "current_month": {
    "id": 1,
    "name": "2026-10",
    "status": "OPEN"
  },
  "meal_units": 27,
  "guest_meal_units": 0,
  "closing_balance": "-25.84",
  "calculation_status": "ESTIMATED",
  "pending_deposit_count": 2,
  "pending_guest_meal_count": 1,
  "total_expense_so_far": "15420.00",
  "estimated_meal_rate": "0.9565",
  "total_active_members": 11,
  "current_manager": 9,
  "reopened_count": 0
}
```

**Error responses**
| Status | Code | When |
|---|---|---|
| 401 | authentication_failed | No authenticated user |

> Notes:
>
> - `pending_deposit_count`, `pending_guest_meal_count`, `total_expense_so_far`, and `estimated_meal_rate` are included only when the requester qualifies for the manager/reporting view.
> - `total_active_members`, `current_manager`, and `reopened_count` are included only for admin users.

---

# Audit

## NOT YET IMPLEMENTED

No `apps/audit/urls.py` or audit API viewset was created in the repository, so no audit read endpoints are currently exposed.

**Capability:** N/A

**Error responses**
| Status | Code | When |
|---|---|---|
| N/A | N/A | No audit endpoints implemented |

---

# Notes

- This document intentionally matches the fields present in the serializers and code paths that are actually implemented.
- Where a route is registered by DRF `DefaultRouter`, the standard model-viewset HTTP methods are listed even if the specific serializer or permission logic is not custom-made for each one.
- For any endpoint that is not in the codebase, it is marked as `NOT YET IMPLEMENTED` instead of being inferred.
