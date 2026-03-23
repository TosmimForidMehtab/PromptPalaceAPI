# Prompt Palace API

A FastAPI-based REST API for a prompt marketplace where users can create, share, and vote on AI prompts.

## Features

-   User authentication (register, login, JWT tokens)
-   Create, read, update, delete prompts
-   Upvote/downvote system
-   Tag-based organization
-   File uploads for prompts and profile images
-   Pagination and filtering
-   Author profiles

## Tech Stack

-   **Framework**: FastAPI
-   **Database**: PostgreSQL (via SQLModel)
-   **ORM**: SQLModel with Alembic migrations
-   **Authentication**: JWT (python-jose, bcrypt)
-   **File Storage**: ImageKit
-   **Server**: Uvicorn

## Prerequisites

-   Python 3.12+
-   PostgreSQL database

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd PromptPalace
```

2. Create and activate virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables in `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost/promptpalace
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=2880
IMAGEKIT_PUBLIC_KEY=your-imagekit-public-key
IMAGEKIT_PRIVATE_KEY=your-imagekit-private-key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your-endpoint
```

5. Run database migrations:

```bash
alembic upgrade head
```

## Running the API

```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:

-   Swagger UI: `http://localhost:8000/docs`
-   ReDoc: `http://localhost:8000/redoc`

## Endpoints

### Authentication

| Method | Endpoint                      | Description                 | Auth Required |
| ------ | ----------------------------- | --------------------------- | ------------- |
| POST   | `/api/v1/register/`           | Register new user           | No            |
| POST   | `/api/v1/login/`              | Login user                  | No            |
| GET    | `/api/v1/me/`                 | Get current user profile    | Yes           |
| PUT    | `/api/v1/me/`                 | Update current user profile | Yes           |
| GET    | `/api/v1/author/{author_id}/` | Get author profile          | No            |

### Prompts

| Method | Endpoint                            | Description                              | Auth Required |
| ------ | ----------------------------------- | ---------------------------------------- | ------------- |
| POST   | `/api/v1/prompts/`                  | Create new prompt                        | Yes           |
| GET    | `/api/v1/prompts/`                  | List prompts (with filtering/pagination) | No            |
| PUT    | `/api/v1/prompts/{prompt_id}/`      | Update prompt                            | Yes           |
| DELETE | `/api/v1/prompts/{prompt_id}/`      | Delete prompt                            | Yes           |
| POST   | `/api/v1/prompts/{prompt_id}/vote/` | Vote on prompt                           | Yes           |

## Request/Response Examples

### Register User

```bash
POST /api/v1/register/
Content-Type: multipart/form-data

email=user@example.com
password=password123
name=John Doe
profile_image=@avatar.png
```

### Create Prompt

```bash
POST /api/v1/prompts/
Authorization: Bearer <token>
Content-Type: multipart/form-data

title=Writing Assistant Prompt
description=A prompt for AI writing assistance
prompt_text=You are a professional writer...
tags=["writing", "ai", "assistant"]
files=@image.png
```

### List Prompts (with filters)

```bash
GET /api/v1/prompts/?page=1&limit=10&tag=writing&sort_by=upvotes
```

### Vote on Prompt

```bash
POST /api/v1/prompts/1/vote/?is_upvote=true
Authorization: Bearer <token>
```

## Response Format

All responses follow this structure:

```json
{
  "status": "success",
  "message": "Description of what happened",
  "data": { ... }
}
```

## Error Responses

```json
{
    "status": "error",
    "message": "Error description",
    "data": null
}
```

## Project Structure

```
PromptPalace/
├── api/
│   ├── api/v1/          # API routes
│   ├── core/            # Config, auth middleware
│   ├── db/              # Database connection
│   ├── models/          # SQLModel models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── main.py          # App entry point
├── alembic/             # Database migrations
├── public/uploads/     # Uploaded files
└── requirements.txt     # Dependencies
```

## Deployed URL = https://promptpalaceapi.onrender.com
