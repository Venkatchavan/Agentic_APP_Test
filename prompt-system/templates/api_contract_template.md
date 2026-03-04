# API Contract

## Endpoint metadata
- **Path**: `<method> /api/v1/<resource>`
- **Version**: v1
- **Auth**: Required | Optional | None
- **Rate limit**: <limit>
- **Idempotent**: Yes | No
- **Approval-gated**: Yes | No

---

## Description
<What does this endpoint do?>

---

## Request

### Headers
| Header | Required | Description |
|--------|----------|-------------|
| Authorization | Yes | Bearer token |
| Idempotency-Key | Conditional | Required for mutations |
| Content-Type | Yes | application/json |

### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| | | | |

### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| | | | | |

### Request Body
```json
{
  "field_1": "<type> — <description>",
  "field_2": "<type> — <description>"
}
```

### Request Example
```json
{
  "field_1": "value",
  "field_2": "value"
}
```

---

## Response

### Success (200 / 201)
```json
{
  "id": "<uuid>",
  "status": "<status>",
  "created_at": "<ISO 8601>",
  "data": {}
}
```

### Error Codes
| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | INVALID_REQUEST | Malformed request body |
| 401 | UNAUTHORIZED | Missing or invalid auth token |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Duplicate or conflicting state |
| 422 | VALIDATION_ERROR | Schema validation failed |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Unexpected server error |

### Error Response Shape
```json
{
  "error": {
    "code": "<ERROR_CODE>",
    "message": "<human-readable message>",
    "details": {}
  }
}
```

---

## Validation Rules
- <rule 1>
- <rule 2>

---

## Notes
- <any additional context, caveats, or dependencies>
