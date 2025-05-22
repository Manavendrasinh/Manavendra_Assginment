# app/api/routers/events.py

from fastapi import APIRouter, Depends, HTTPException, status, Response # Response is used for 204
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any # Added Dict, Any for the diff endpoint
from datetime import datetime

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.event import Event
from app.models.permission import EventPermission
# No need to import EventVersion model here, as router calls CRUD which handles it
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.schemas.permission import (
    EventPermissionCreate,
    EventPermissionResponse,
    EventPermissionDetail,
    EventPermissionUpdate
)
from app.schemas.pagination import PaginatedResponse
from app.schemas.changelog import ChangelogEntryResponseSchema # <-- New import for changelog schema
from app.crud import crud_event

router = APIRouter(
    prefix="/api/events",
    tags=["Events"]
)

# --- Standard Event Endpoints ---

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event_endpoint(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_event.create_event(db=db, event=event_data, owner_id=current_user.id)

@router.get("/", response_model=PaginatedResponse[EventResponse])
async def read_events_endpoint(
    skip: int = 0,
    limit: int = 100,
    title: Optional[str] = None,
    owner_id: Optional[int] = None,
    start_time_after: Optional[datetime] = None,
    start_time_before: Optional[datetime] = None,
    sort_by: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = crud_event.get_events_with_permission(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        title=title,
        owner_id=owner_id,
        start_time_after=start_time_after,
        start_time_before=start_time_before,
        sort_by=sort_by
    )
    return result

@router.get("/{event_id}", response_model=EventResponse)
async def read_single_event_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event_obj = crud_event.get_event_with_permission(db, event_id, current_user.id)
    if not event_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found or not authorized")
    return event_obj

@router.put("/{event_id}", response_model=EventResponse)
async def update_single_event_endpoint(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_event = crud_event.update_event(db, event_id, event_data, current_user.id)
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found or not authorized for update")
    return db_event

@router.delete("/{event_id}", response_model=EventResponse)
async def delete_single_event_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_event = crud_event.delete_event(db, event_id, current_user.id)
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found or not authorized for deletion")
    return db_event

@router.post("/batch", response_model=List[EventResponse], status_code=status.HTTP_201_CREATED)
async def create_events_batch_endpoint(
    events_data: List[EventCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_event.create_events_batch(db, events_data, owner_id=current_user.id)

# --- Event Sharing and Permission Endpoints ---

@router.post("/{event_id}/share", response_model=EventPermissionResponse)
async def share_event_endpoint(
    event_id: int,
    permission_in: EventPermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event_obj = db.query(Event).filter(Event.id == event_id, Event.owner_id == current_user.id).first()
    if not event_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the event owner can share this event"
        )
    
    user_to_share_with = db.query(User).filter(User.id == permission_in.user_id).first()
    if not user_to_share_with:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {permission_in.user_id} not found"
        )
    
    existing_permission = db.query(EventPermission).filter(
        EventPermission.event_id == event_id,
        EventPermission.user_id == permission_in.user_id
    ).first()
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {permission_in.user_id} already has a permission for event {event_id}. Use PUT to update."
        )

    new_permission = EventPermission(
        event_id=event_id,
        user_id=permission_in.user_id,
        role_id=permission_in.role_id
    )
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    return new_permission

@router.get("/{event_id}/permissions", response_model=List[EventPermissionDetail])
async def list_event_permissions_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event_obj = db.query(Event).filter(Event.id == event_id, Event.owner_id == current_user.id).first()
    if not event_obj:
        has_any_permission = db.query(EventPermission).filter(
            EventPermission.event_id == event_id,
            EventPermission.user_id == current_user.id
        ).first()
        if not has_any_permission: 
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view permissions for this event"
            )
    
    permissions_details = crud_event.get_permissions_for_event(db, event_id)
    return permissions_details

@router.put("/{event_id}/permissions/{target_user_id}", response_model=EventPermissionResponse)
async def update_user_permission_endpoint(
    event_id: int,
    target_user_id: int,
    permission_data: EventPermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event_obj = db.query(Event).filter(Event.id == event_id, Event.owner_id == current_user.id).first()
    if not event_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the event owner can update permissions"
        )
    
    updated_permission = crud_event.update_permission(
        db, event_id, target_user_id, permission_data.role_id
    )
    if not updated_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission for user ID {target_user_id} on event ID {event_id} not found"
        )
    return updated_permission

@router.delete("/{event_id}/permissions/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_permission_endpoint(
    event_id: int,
    target_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event_obj = db.query(Event).filter(Event.id == event_id, Event.owner_id == current_user.id).first()
    if not event_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the event owner can remove permissions"
        )
    
    success = crud_event.delete_permission(db, event_id, target_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission for user ID {target_user_id} on event ID {event_id} not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Event Version History and Rollback Endpoints ---

@router.get("/{event_id}/history/{version_id}", response_model=EventResponse)
async def get_event_version_history_endpoint(
    event_id: int,
    version_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event_access = crud_event.get_event_with_permission(db, event_id, current_user.id)
    if not event_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event ID {event_id} not found or user not authorized to view its history"
        )

    event_version_obj = crud_event.get_specific_event_version(db, version_id)

    if not event_version_obj or event_version_obj.event_id != event_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version ID {version_id} not found for event ID {event_id}"
        )
    return event_version_obj.data

@router.post("/{event_id}/rollback/{version_id}", response_model=EventResponse)
async def rollback_event_to_version_endpoint(
    event_id: int,
    version_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    is_owner = db.query(Event).filter(Event.id == event_id, Event.owner_id == current_user.id).first()
    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the event owner can perform a rollback"
        )

    rolled_back_event = crud_event.rollback_event_to_specific_version(
        db, event_id, version_id, current_user.id
    )
    
    if not rolled_back_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rollback failed. Event ID {event_id} or Version ID {version_id} not found, or version does not match event."
        )
    return rolled_back_event

# --- Changelog & Diff Endpoints ---

@router.get("/{event_id}/changelog", response_model=List[ChangelogEntryResponseSchema])
async def get_event_changelog_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event_access = crud_event.get_event_with_permission(db, event_id, current_user.id)
    if not event_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event ID {event_id} not found or user not authorized to view its changelog"
        )
    
    changelog_data = crud_event.get_event_changelog(db, event_id)
    return changelog_data

@router.get("/{event_id}/diff/{version_id1}/{version_id2}", response_model=Dict[str, Any])
async def get_event_versions_diff_endpoint(
    event_id: int,
    version_id1: int,
    version_id2: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event_access = crud_event.get_event_with_permission(db, event_id, current_user.id)
    if not event_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event ID {event_id} not found or user not authorized to view version diffs"
        )

    diff_data = crud_event.get_diff_between_event_versions(db, event_id, version_id1, version_id2)
    
    if diff_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"One or both versions (ID: {version_id1}, ID: {version_id2}) not found for event ID {event_id}, or they do not belong to this event."
        )
    
    return diff_data
