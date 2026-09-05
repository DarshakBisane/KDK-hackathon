from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import User, RoadmapItem
from app.schemas.schemas import (
    RoadmapProgressResponse,
    RoadmapItemResponse,
    RoadmapStatusUpdate,
)
from app.api.deps import get_current_user
from app.services.roadmap_service import (
    generate_or_get_roadmap,
    update_roadmap_item_status,
)

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])


def _build_progress_response(items: list[RoadmapItem]) -> RoadmapProgressResponse:
    total = len(items)
    completed = sum(1 for i in items if i.status == "Completed")
    learning = sum(1 for i in items if i.status == "Learning")
    not_started = sum(1 for i in items if i.status == "Not Started")
    
    pct = round((completed / total) * 100, 1) if total > 0 else 0.0

    items_res = [
        RoadmapItemResponse(
            id=i.id,
            title=i.title,
            description=i.description,
            week=i.week,
            status=i.status,
            importance=i.importance or "HIGH",
            skill_name=i.skill.name if i.skill else None
        )
        for i in items
    ]

    return RoadmapProgressResponse(
        total_items=total,
        completed_items=completed,
        learning_items=learning,
        not_started_items=not_started,
        progress_percentage=pct,
        items=items_res
    )


@router.get("", response_model=RoadmapProgressResponse)
def get_user_roadmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = generate_or_get_roadmap(current_user.id, db)
    return _build_progress_response(items)


@router.put("/{item_id}", response_model=RoadmapProgressResponse)
def update_item_status(
    item_id: int,
    status_data: RoadmapStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated = update_roadmap_item_status(
        user_id=current_user.id,
        item_id=item_id,
        new_status=status_data.status,
        db=db
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Roadmap milestone #{item_id} not found for this user."
        )

    # Fetch updated list
    all_items = (
        db.query(RoadmapItem)
        .filter(RoadmapItem.user_id == current_user.id)
        .order_by(RoadmapItem.week.asc())
        .all()
    )
    return _build_progress_response(all_items)
