from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from api.models.prompt import Prompt, Vote
from api.services.storage import upload_files
from api.models.user import User

MAX_MEDIA = 5


async def create_prompt(
    title: str,
    description: str,
    prompt_text: str,
    tags: List[str],
    files: List,
    current_user: User,
    db: Session,
):
    if len(files) > MAX_MEDIA:
        raise HTTPException(
            status_code=400, detail=f"You can attach a maximum of {MAX_MEDIA} files."
        )
    media_urls = await upload_files(files) if files else []
    prompt = Prompt(
        user_id=current_user.id,
        title=title,
        description=description,
        prompt_text=prompt_text,
        tags=tags,
        media_urls=media_urls,
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


async def vote(prompt_id: int, is_upvote: bool, user: User, db: Session):
    existing_vote = (
        db.query(Vote).filter_by(prompt_id=prompt_id, user_id=user.id).first()
    )
    if existing_vote:
        existing_vote.is_upvote = is_upvote
    else:
        existing_vote = Vote(prompt_id=prompt_id, user_id=user.id, is_upvote=is_upvote)
        db.add(existing_vote)
    db.commit()
    return {"status": "ok"}


async def list_prompts(
    db: Session, skip: int = 0, limit: int = 10, tag: Optional[str] = None
):
    query = db.query(Prompt)
    if tag:
        query = query.filter(Prompt.tags.contains([tag]))
    return query.offset(skip).limit(limit).all()
