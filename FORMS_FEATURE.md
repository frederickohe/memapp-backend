# Form Management Feature Documentation

## Overview
The Form Management feature allows admins to create, manage, and track forms that can be assigned to different audiences. Forms can be public, assigned to specific programs, or assigned to individual users.

## Architecture

### Project Structure
```
src/core/forms/
├── model/
│   ├── form.py              # SQLAlchemy models for Form and FormResponse
│   └── __init__.py
├── dto/
│   ├── request/
│   │   ├── formrequest.py   # Request DTOs for form operations
│   │   └── __init__.py
│   ├── response/
│   │   ├── formresponse.py  # Response DTOs
│   │   └── __init__.py
│   └── __init__.py
├── service/
│   ├── formservice.py       # Business logic for form operations
│   └── __init__.py
├── controller/
│   ├── formcontroller.py    # API routes and endpoints
│   └── __init__.py
└── __init__.py
```

## Database Models

### Form Model
Stores form definitions and metadata.

**Fields:**
- `id` (String, Primary Key): Unique form identifier
- `admin_id` (String, FK): ID of the admin who created the form
- `title` (String): Form title
- `description` (Text): Form description
- `assignment_type` (Enum): PUBLIC, PROGRAM, or USER
- `program_id` (String, Optional): Program ID if assigned to a program
- `assigned_user_id` (String, FK, Optional): User ID if assigned to a specific user
- `fields` (JSONB): Form field definitions stored as JSON
- `is_active` (Boolean): Whether the form is active
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- Many-to-One with User (admin)
- One-to-Many with User (assigned_user)
- One-to-Many with FormResponse (responses)

### FormResponse Model
Stores form submissions.

**Fields:**
- `id` (String, Primary Key): Unique response identifier
- `form_id` (String, FK): ID of the form being responded to
- `user_id` (String, FK): ID of the user submitting the response
- `data` (JSONB): Form response data (key-value pairs)
- `notes` (Text, Optional): Additional notes about the submission
- `is_submitted` (Boolean): Whether the response is submitted
- `created_at` (DateTime): Submission timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- Many-to-One with Form (form)
- Many-to-One with User (user)

## Form Field Structure

Forms store their fields as JSONB. Each field has:

```json
{
  "field_name": {
    "name": "email",
    "label": "Email Address",
    "field_type": "email",
    "required": true,
    "placeholder": "Enter your email",
    "options": null,
    "validation": {"pattern": "email"},
    "order": 0
  }
}
```

**Supported Field Types:**
- `text`: Simple text input
- `email`: Email input with validation
- `number`: Numeric input
- `textarea`: Multi-line text input
- `select`: Dropdown selection
- `radio`: Radio button group
- `checkbox`: Checkbox group
- `date`: Date picker
- `file`: File upload
- Custom types as needed

## API Endpoints

### Admin Form Management

#### Create Form
```
POST /api/forms/create
Authentication: Required (Admin only)
```

**Request:**
```json
{
  "title": "Customer Feedback",
  "description": "Help us improve our services",
  "assignment_type": "PUBLIC",
  "program_id": null,
  "assigned_user_id": null,
  "fields": [
    {
      "name": "name",
      "label": "Your Name",
      "field_type": "text",
      "required": true,
      "placeholder": "John Doe"
    },
    {
      "name": "email",
      "label": "Email Address",
      "field_type": "email",
      "required": true
    },
    {
      "name": "rating",
      "label": "Rating",
      "field_type": "select",
      "required": true,
      "options": ["Very Good", "Good", "Average", "Poor"]
    }
  ],
  "is_active": true
}
```

**Response:**
```json
{
  "id": "FORM_abc123def456",
  "admin_id": "USER_123",
  "title": "Customer Feedback",
  "description": "Help us improve our services",
  "assignment_type": "PUBLIC",
  "program_id": null,
  "assigned_user_id": null,
  "fields": [...],
  "is_active": true,
  "created_at": "2024-02-02T10:30:00Z",
  "updated_at": "2024-02-02T10:30:00Z"
}
```

#### Get Form
```
GET /api/forms/{form_id}
Authentication: Optional
```

Returns form details including all fields.

#### Get Form Detail (with response count)
```
GET /api/forms/{form_id}/detail
Authentication: Optional
```

Returns form with the count of responses received.

#### List All Forms (Admin)
```
GET /api/forms?page=1&size=10&assignment_type=PUBLIC&is_active=true
Authentication: Required (Admin only)
```

**Query Parameters:**
- `page` (int, default: 1): Page number for pagination
- `size` (int, default: 10, max: 100): Items per page
- `assignment_type` (string, optional): Filter by PUBLIC, PROGRAM, or USER
- `is_active` (boolean, optional): Filter by active status

**Response:**
```json
{
  "total": 5,
  "page": 1,
  "size": 10,
  "items": [...]
}
```

#### Update Form
```
PUT /api/forms/{form_id}
Authentication: Required (Admin only)
```

Update any form fields. All fields are optional.

**Request:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "is_active": false
}
```

#### Delete Form
```
DELETE /api/forms/{form_id}
Authentication: Required (Admin only)
```

**Response:**
```json
{
  "message": "Form deleted successfully"
}
```

### Form Response Management

#### Submit Form Response
```
POST /api/forms/{form_id}/submit
Authentication: Required
```

**Request:**
```json
{
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "rating": "Very Good"
  },
  "notes": "Optional notes about the submission"
}
```

**Response:**
```json
{
  "id": "FRESP_xyz789abc123",
  "form_id": "FORM_abc123def456",
  "user_id": "USER_123",
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "rating": "Very Good"
  },
  "notes": "Optional notes about the submission",
  "is_submitted": true,
  "created_at": "2024-02-02T11:00:00Z",
  "updated_at": "2024-02-02T11:00:00Z"
}
```

#### Get Form Responses (Admin Only)
```
GET /api/forms/{form_id}/responses?page=1&size=10
Authentication: Required (Admin only - form owner)
```

Returns all responses submitted to a form.

**Response:**
```json
{
  "form_id": "FORM_abc123def456",
  "form_title": "Customer Feedback",
  "total_responses": 25,
  "page": 1,
  "size": 10,
  "responses": [...]
}
```

### Public & User-Assigned Forms

#### Get Public Forms
```
GET /api/forms/public/list?page=1&size=10
Authentication: Optional
```

Get all publicly available forms.

#### Get My Assigned Forms
```
GET /api/forms/my-forms?page=1&size=10
Authentication: Required
```

Get all forms assigned to the current user.

## Form Assignment Types

### PUBLIC
- Anyone can access and submit responses
- No user-specific assignment
- Used for surveys, registrations, etc.

### PROGRAM
- Assigned to a specific program
- Only program members can access
- `program_id` field must be specified

### USER
- Assigned to a specific user
- Only that user can access and submit
- `assigned_user_id` field must be specified

## Usage Examples

### Example 1: Create a Public Survey
```bash
curl -X POST http://localhost:8000/api/forms/create \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "YMCA Membership Survey",
    "description": "Help us understand your needs",
    "assignment_type": "PUBLIC",
    "fields": [
      {
        "name": "age_group",
        "label": "Age Group",
        "field_type": "radio",
        "required": true,
        "options": ["18-25", "26-35", "36-50", "50+"]
      },
      {
        "name": "activities",
        "label": "Interested Activities",
        "field_type": "checkbox",
        "options": ["Swimming", "Gym", "Yoga", "Basketball"]
      }
    ],
    "is_active": true
  }'
```

### Example 2: Create a User-Assigned Form
```bash
curl -X POST http://localhost:8000/api/forms/create \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Annual Membership Review",
    "description": "Please review your membership details",
    "assignment_type": "USER",
    "assigned_user_id": "USER_456",
    "fields": [
      {
        "name": "current_activities",
        "label": "Current Activities",
        "field_type": "textarea",
        "required": false
      },
      {
        "name": "feedback",
        "label": "Feedback",
        "field_type": "textarea",
        "required": true
      }
    ],
    "is_active": true
  }'
```

### Example 3: Submit a Form Response
```bash
curl -X POST http://localhost:8000/api/forms/FORM_abc123def456/submit \
  -H "Authorization: Bearer <user_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "Jane Smith",
      "email": "jane@example.com",
      "feedback": "Great facilities and friendly staff!"
    },
    "notes": "Very satisfied with the service"
  }'
```

### Example 4: View Form Responses
```bash
curl -X GET http://localhost:8000/api/forms/FORM_abc123def456/responses?page=1&size=20 \
  -H "Authorization: Bearer <admin_token>"
```

## Security & Permissions

### Admin Permissions
- Create forms
- Update/delete their own forms
- View responses for their forms
- Activate/deactivate forms

### User Permissions
- Submit responses to public forms
- Submit responses to forms assigned to them
- View forms assigned to them
- Cannot create forms (non-admin only)

### Form Visibility
- **Public Forms**: Visible to everyone
- **Program Forms**: Visible only to program members
- **User Forms**: Visible only to the assigned user

## Validation

### Form Creation Validation
- Title is required and unique per admin
- Assignment type must be one of: PUBLIC, PROGRAM, USER
- For USER assignment: assigned_user_id must exist
- For PROGRAM assignment: program_id should reference valid program
- Fields array must not be empty
- Each field must have unique name

### Form Response Validation
- All required fields must be present
- Field values must match expected types
- Custom validation rules are applied if defined

## Data Flow

```
1. Admin creates form with fields
   ↓
2. Form is stored with JSON field definitions
   ↓
3. Form is assigned (PUBLIC/PROGRAM/USER)
   ↓
4. Users access form based on assignment
   ↓
5. Users submit responses
   ↓
6. Responses stored with user data
   ↓
7. Admin views and analyzes responses
```

## Future Enhancements

- [ ] Form templates for common use cases
- [ ] Conditional field logic (show/hide based on answers)
- [ ] Response filtering and export (CSV/PDF)
- [ ] Form versioning and archival
- [ ] Response statistics and analytics
- [ ] Email notifications on form submission
- [ ] Multi-language form support
- [ ] Form builder UI
- [ ] Response validation rules
- [ ] Access control per form (multiple admins)

## Database Migration

To apply the migration:

```bash
alembic upgrade heads
```

Or if using a specific migration:

```bash
alembic upgrade forms_migration_001
```

To rollback:

```bash
alembic downgrade -1
```

## Troubleshooting

### Issue: 403 Forbidden when creating forms
- Ensure user has admin role
- Check token expiration

### Issue: Form fields not displaying correctly
- Verify JSONB data format in database
- Check field type is supported

### Issue: Cannot submit response to user-assigned form
- Verify current user matches assigned_user_id
- Check if form is active

## Related Modules

- **Authentication**: `/core/auth/` - Token validation
- **Users**: `/core/user/` - User management
- **Notifications**: `/core/notification/` - Optional: notify on submissions
