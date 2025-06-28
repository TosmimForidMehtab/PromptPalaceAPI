from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
    Form,
    status,
)
from typing import List, Optional

from sqlalchemy import func, case
from api.schemas.common import ResponseModel
from api.services import prompts as prompts_service
from api.services.auth import get_current_user
from api.models.user import User
from api.models.prompt import Prompt, Vote
from sqlalchemy.orm import Session
from api.db.database import get_session

router = APIRouter()


@router.post("/prompts/", status_code=status.HTTP_201_CREATED)
async def create_prompt(
    title: str = Form(...),
    description: str = Form(...),
    prompt_text: str = Form(...),
    tags: List[str] = Form(...),
    files: List[UploadFile] = File([]),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    prompt = await prompts_service.create_prompt(
        title, description, prompt_text, tags, files, current_user, db
    )
    if prompt is None:
        raise HTTPException(status_code=400, detail="Prompt creation failed.")
    return ResponseModel(
        status="success",
        message="Prompt created successfully.",
        data={"prompt": prompt},
    )


@router.post("/prompts/{prompt_id}/vote/")
async def vote(
    prompt_id: int,
    is_upvote: bool,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    response = await prompts_service.vote(prompt_id, is_upvote, user, db)
    if response is None or response.get("status") != "ok":
        raise HTTPException(status_code=400, detail="Vote creation failed.")
    return ResponseModel(
        status="success",
        message="Vote created successfully.",
        data={"response": response},
    )


@router.get("/prompts/", status_code=status.HTTP_200_OK)
def list_prompts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    description: Optional[str] = None,
    tag: Optional[str] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = Query(None, enum=["upvotes", "downvotes"]),
    db: Session = Depends(get_session),
):
    """List prompts with optional filtering and sorting."""
    query = (
        db.query(
            Prompt,
            User.email,
            func.sum(case((Vote.is_upvote == True, 1), else_=0)).label("upvotes"),
            func.sum(case((Vote.is_upvote == False, 1), else_=0)).label("downvotes"),
        )
        .join(User, User.id == Prompt.user_id)
        .outerjoin(Vote, Vote.prompt_id == Prompt.id)
        .group_by(Prompt.id, User.email)
    )

    # Apply Filters
    if description:
        query = query.filter(Prompt.description.ilike(f"%{description}%"))
    if tag:
        query = query.filter(Prompt.tags.contains([tag]))
    if author:
        query = query.filter(User.email.ilike(f"%{author}%"))

    # Apply Sorting
    if sort_by == "upvotes":
        query = query.order_by(
            func.sum(case((Vote.is_upvote == True, 1), else_=0)).desc()
        )
    elif sort_by == "downvotes":
        query = query.order_by(
            func.sum(case((Vote.is_upvote == False, 1), else_=0)).desc()
        )
    else:
        query = query.order_by(Prompt.created_at.desc())

    total_count = query.count()
    results = query.offset((page - 1) * limit).limit(limit).all()

    prompts = []
    for prompt, email, upvotes, downvotes in results:
        prompts.append(
            {
                "id": prompt.id,
                "title": prompt.title,
                "description": prompt.description,
                "tags": prompt.tags,
                "media_urls": prompt.media_urls,
                "created_at": prompt.created_at,
                "author": email,
                "upvotes": upvotes or 0,
                "downvotes": downvotes or 0,
            }
        )
    pagination = {
        "count": total_count,
        "has_next": page * limit < total_count,
        "has_prev": page > 1,
        "limit": limit,
        "page": page,
    }
    return ResponseModel(
        status="success",
        message="Prompt list retrieved successfully.",
        data={"prompts": prompts, "pagination": pagination},
    )


@router.put("/prompts/{prompt_id}/", status_code=status.HTTP_200_OK)
def update_prompt(
    prompt_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    prompt_text: Optional[str] = Form(None),
    tags: Optional[List[str]] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Update a prompt owned by the current user."""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found.")
    if prompt.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this prompt."
        )

    if title is not None:
        prompt.title = title
    if description is not None:
        prompt.description = description
    if prompt_text is not None:
        prompt.prompt_text = prompt_text
    if tags is not None:
        prompt.tags = tags

    db.add(prompt)
    db.commit()
    db.refresh(prompt)

    return ResponseModel(
        status="success", message="Prompt updated successfully.", data={"id": prompt.id}
    )


@router.delete("/prompts/{prompt_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Delete a prompt owned by the current user."""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found.")
    if prompt.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this prompt."
        )

    db.delete(prompt)
    db.commit()
    return ResponseModel(status="success", message="Prompt deleted successfully.")
