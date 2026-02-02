# Program Management Feature Documentation

## Overview
The Program Management feature allows administrators to create, manage, and track programs/activities/projects within the YMCA organization. Programs can have associated forms, enrollment management, and detailed participant tracking.

## Architecture

### Project Structure
```
src/core/programs/
├── model/
│   ├── program.py                    # SQLAlchemy models for Program, ProgramEnrollment
│   └── __init__.py
├── dto/
│   ├── request/
│   │   ├── programrequest.py        # Request DTOs
│   │   └── __init__.py
│   ├── response/
│   │   ├── programresponse.py       # Response DTOs
│   │   └── __init__.py
│   └── __init__.py
├── service/
│   ├── programservice.py            # Business logic
│   └── __init__.py
├── controller/
│   ├── programcontroller.py         # API routes and endpoints
│   └── __init__.py
└── __init__.py
```

## Database Models

### Program Model
Stores program/activity information.

**Fields:**
- `id` (String, Primary Key): Unique program identifier
- `title` (String): Program title
- `description` (Text): Program description/about
- `starting_date` (DateTime): Program start date
- `end_date` (DateTime): Program end date
- `register_url` (String, Optional): Registration URL
- `youtube_url` (String, Optional): YouTube video URL
- `thumbnail_url` (String, Optional): Program thumbnail image
- `status` (Enum): UPCOMING, ONGOING, COMPLETED, CANCELLED (auto-determined)
- `created_by` (String, FK): Admin who created the program
- `capacity` (Integer, Optional): Maximum participants
- `category` (String, Optional): Program category/type
- `location` (String, Optional): Program location
- `is_published` (Boolean): Whether program is published
- `allow_registration` (Boolean): Whether registration is allowed
- `metadata` (JSONB, Optional): Custom metadata
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- Many-to-One with User (creator)
- Many-to-Many with Form (forms)
- Many-to-Many with User (participants)

### ProgramEnrollment Model
Tracks detailed enrollment information for each participant.

**Fields:**
- `id` (String, Primary Key): Unique enrollment identifier
- `program_id` (String, FK): Reference to program
- `user_id` (String, FK): Reference to user
- `status` (String): ACTIVE, DROPPED, COMPLETED, PENDING
- `completion_percentage` (Integer): Progress (0-100)
- `enrolled_at` (DateTime): Enrollment date
- `completed_at` (DateTime, Optional): Completion date
- `dropped_at` (DateTime, Optional): Drop date
- `notes` (Text, Optional): Enrollment notes
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

## Program Status
Status is automatically determined based on current date:
- **UPCOMING**: Current date < starting_date
- **ONGOING**: starting_date ≤ Current date ≤ end_date
- **COMPLETED**: Current date > end_date
- **CANCELLED**: Manually set

## Association Tables

### program_forms
Many-to-many relationship between programs and forms.
- `program_id`: Reference to program
- `form_id`: Reference to form
- `added_at`: When the form was associated

### program_participants
Many-to-many relationship between programs and users.
- `program_id`: Reference to program
- `user_id`: Reference to user
- `joined_at`: When user joined
- `status`: Participant status (ACTIVE, DROPPED, COMPLETED)

## API Endpoints

### Admin Program Management

#### Create Program
```
POST /api/programs/create
Authentication: Required (Admin only)
```

**Request:**
```json
{
  "title": "Beginner Yoga Class",
  "description": "Learn basic yoga techniques for beginners",
  "starting_date": "2024-03-01T10:00:00Z",
  "end_date": "2024-05-01T11:00:00Z",
  "register_url": "https://example.com/register/yoga-101",
  "youtube_url": "https://youtube.com/watch?v=...",
  "thumbnail_url": "https://example.com/images/yoga.jpg",
  "category": "Fitness",
  "location": "Main Branch - Studio A",
  "capacity": 30,
  "form_ids": ["FORM_abc123def456"],
  "is_published": true,
  "allow_registration": true,
  "metadata": {
    "instructor": "John Doe",
    "difficulty_level": "Beginner"
  }
}
```

**Response:**
```json
{
  "id": "PROG_abc123def456",
  "title": "Beginner Yoga Class",
  "description": "Learn basic yoga techniques for beginners",
  "starting_date": "2024-03-01T10:00:00Z",
  "end_date": "2024-05-01T11:00:00Z",
  "register_url": "https://example.com/register/yoga-101",
  "youtube_url": "https://youtube.com/watch?v=...",
  "thumbnail_url": "https://example.com/images/yoga.jpg",
  "category": "Fitness",
  "location": "Main Branch - Studio A",
  "capacity": 30,
  "status": "UPCOMING",
  "is_published": true,
  "allow_registration": true,
  "created_by": "ADMIN_123",
  "forms": [
    {
      "id": "FORM_abc123def456",
      "title": "Registration Form",
      "description": null,
      "fields": [...]
    }
  ],
  "participant_count": 0,
  "participants": [],
  "created_at": "2024-02-02T10:30:00Z",
  "updated_at": "2024-02-02T10:30:00Z"
}
```

#### Get Program
```
GET /api/programs/{program_id}
Authentication: Optional
```

Returns detailed program information with forms and participants.

#### List Admin's Programs
```
GET /api/programs?page=1&size=10&status=UPCOMING&category=Fitness&is_published=true
Authentication: Required (Admin only)
```

**Query Parameters:**
- `page` (int, default: 1): Page number
- `size` (int, default: 10, max: 100): Items per page
- `status` (string, optional): Filter by status
- `category` (string, optional): Filter by category
- `is_published` (boolean, optional): Filter by publish status

#### Update Program
```
PUT /api/programs/{program_id}
Authentication: Required (Admin only)
```

Update any program fields. All fields are optional.

**Request:**
```json
{
  "title": "Updated Title",
  "capacity": 50,
  "is_published": false
}
```

#### Delete Program
```
DELETE /api/programs/{program_id}
Authentication: Required (Admin only)
```

**Response:**
```json
{
  "message": "Program deleted successfully"
}
```

### Program Enrollment

#### Enroll User (Admin)
```
POST /api/programs/{program_id}/enroll
Authentication: Required (Admin only)
```

Admin can enroll any user in a program.

**Request:**
```json
{
  "user_id": "USER_789",
  "notes": "Referred by staff"
}
```

**Response:**
```json
{
  "id": "ENRL_xyz789abc123",
  "program_id": "PROG_abc123def456",
  "user_id": "USER_789",
  "status": "ACTIVE",
  "completion_percentage": 0,
  "enrolled_at": "2024-02-02T11:00:00Z",
  "completed_at": null,
  "dropped_at": null,
  "notes": "Referred by staff"
}
```

#### Self-Enroll User
```
POST /api/programs/{program_id}/self-enroll
Authentication: Required
```

User can self-enroll in a published program.

**Request:**
```json
{
  "user_id": "USER_123",
  "notes": "Interested in yoga"
}
```

#### Unenroll from Program
```
POST /api/programs/{program_id}/unenroll
Authentication: Required
```

User drops out from a program.

**Response:**
```json
{
  "message": "User unenrolled from program successfully"
}
```

#### Get Program Enrollments
```
GET /api/programs/{program_id}/enrollments?page=1&size=20
Authentication: Required (Admin only - program creator)
```

Get all enrollments for a program with pagination.

**Response:**
```json
{
  "program_id": "PROG_abc123def456",
  "program_title": "Beginner Yoga Class",
  "total_enrollments": 15,
  "page": 1,
  "size": 20,
  "enrollments": [...]
}
```

#### Update Enrollment Status
```
PUT /api/programs/enrollments/{enrollment_id}?program_id={program_id}
Authentication: Required (Admin only)
```

Update an enrollment's status and completion progress.

**Request:**
```json
{
  "status": "COMPLETED",
  "completion_percentage": 100,
  "notes": "Completed all sessions"
}
```

### Public Program Endpoints

#### Browse Public Programs
```
GET /api/programs/public/browse?page=1&size=10&category=Fitness
Authentication: Optional
```

Get all published programs for browsing.

**Query Parameters:**
- `page` (int, default: 1): Page number
- `size` (int, default: 10, max: 100): Items per page
- `category` (string, optional): Filter by category

### User Program Endpoints

#### Get My Programs
```
GET /api/programs/my-programs?page=1&size=10
Authentication: Required
```

Get all programs the current user is enrolled in.

**Response:**
```json
{
  "total": 3,
  "page": 1,
  "size": 10,
  "programs": [...]
}
```

## Capacity Management

Programs can have optional capacity limits:
- If `capacity` is set, enrollment is limited to that number
- Enrollment fails if capacity is reached
- Only ACTIVE enrollments count toward capacity

## Form Association

Programs can have multiple associated forms:
- Forms are linked during program creation
- Forms can be added/updated when editing programs
- Forms are returned with program details
- Users can submit responses to program forms

## Enrollment Workflow

1. **Program Created** → Status: UPCOMING (if start date in future)
2. **Program Published** → Available for registration
3. **User Enrolls** → Enrollment created with ACTIVE status
4. **Program Ongoing** → Status: ONGOING (between dates)
5. **Completion Tracking** → Admin updates completion %
6. **Program Ends** → Status: COMPLETED (automatically)
7. **User Drops** → Enrollment marked as DROPPED

## Usage Examples

### Example 1: Create a Fitness Program
```bash
curl -X POST http://localhost:8000/api/programs/create \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weight Loss Challenge",
    "description": "8-week program to achieve your fitness goals",
    "starting_date": "2024-03-15T09:00:00Z",
    "end_date": "2024-05-10T09:00:00Z",
    "category": "Fitness",
    "location": "Main Branch",
    "capacity": 50,
    "is_published": true,
    "allow_registration": true,
    "metadata": {
      "difficulty": "intermediate",
      "sessions_per_week": 3
    }
  }'
```

### Example 2: Enroll User in Program
```bash
curl -X POST http://localhost:8000/api/programs/PROG_abc123def456/enroll \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_456",
    "notes": "New member enrollment"
  }'
```

### Example 3: Self-Enroll
```bash
curl -X POST http://localhost:8000/api/programs/PROG_abc123def456/self-enroll \
  -H "Authorization: Bearer <user_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_123",
    "notes": "Interested in fitness"
  }'
```

### Example 4: Track Completion
```bash
curl -X PUT http://localhost:8000/api/programs/enrollments/ENRL_xyz789abc123?program_id=PROG_abc123def456 \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "completion_percentage": 75,
    "notes": "Attended 6 out of 8 sessions"
  }'
```

### Example 5: Browse Public Programs
```bash
curl -X GET "http://localhost:8000/api/programs/public/browse?category=Fitness&page=1&size=10"
```

## Security & Permissions

### Admin Permissions
- Create programs
- Update/delete their own programs
- Enroll users in programs
- View/manage enrollments
- Update enrollment progress

### User Permissions
- View published programs
- Self-enroll in programs (if registration allowed)
- View their enrolled programs
- Unenroll from programs
- Cannot create/edit programs

### Program Visibility
- **Published Programs**: Visible to everyone
- **Unpublished Programs**: Only visible to creator

## Validation Rules

### Program Creation
- Title is required
- End date must be after start date
- Capacity must be positive if provided
- Form IDs must reference existing forms
- Creator must be valid user

### Enrollment
- Program must be published
- Registration must be allowed
- User must not already be enrolled
- Capacity limits must be respected
- User must exist

## Error Handling

Common error responses:

```json
{
  "detail": "Program not found",
  "status_code": 404
}
```

```json
{
  "detail": "Only admins can create programs",
  "status_code": 403
}
```

```json
{
  "detail": "Program is at full capacity",
  "status_code": 400
}
```

## Statistics & Reporting

Track across enrollments:
- Total enrollments per program
- Completion rates
- Dropout rates
- Active participant count
- Program status

## Database Migration

To apply the migration:

```bash
alembic upgrade heads
```

To rollback:

```bash
alembic downgrade -1
```

## Future Enhancements

- [ ] Program schedules/sessions
- [ ] Attendance tracking
- [ ] Certificate generation on completion
- [ ] Instructor assignment
- [ ] Program ratings and reviews
- [ ] Waitlist management
- [ ] Bulk enrollment import
- [ ] Email notifications
- [ ] Program templates
- [ ] Advanced reporting/analytics
- [ ] Resource allocation
- [ ] Cost/pricing management

## Related Modules

- **Forms**: `/core/forms/` - Associate forms with programs
- **Authentication**: `/core/auth/` - Token validation
- **Users**: `/core/user/` - User management
- **Notifications**: `/core/notification/` - Optional: notify on enrollment
