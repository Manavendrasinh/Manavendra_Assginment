# app/crud/crud_event.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import Optional, List, Dict, Any
from datetime import datetime
from dateutil import parser # For parsing ISO datetime strings back to datetime objects

from app.models.event import Event
from app.models.permission import EventPermission
from app.models.version import EventVersion
from app.models.changelog import Changelog
from app.models.user import User, Role
from app.schemas.event import EventCreate, EventUpdate, EventResponse # For EventResponse.model_fields

def model_to_dict(obj) -> Dict[str, Any]:
    """Convert SQLAlchemy model to dict with datetime ISO formatting."""
    result = {}
    for c in obj.__table__.columns:
        value = getattr(obj, c.key)
        if isinstance(value, datetime):
            result[c.key] = value.isoformat()
        else:
            result[c.key] = value
    return result

def get_event_with_permission(db: Session, event_id: int, user_id: int) -> Optional[Event]:
    """Get event if user has access (owner, editor, or viewer)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None
    if event.owner_id == user_id:
        return event
    permission = db.query(EventPermission).filter(
        EventPermission.event_id == event_id,
        EventPermission.user_id == user_id
    ).first()
    if permission:
        return event
    return None

def get_events_with_permission(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    title: Optional[str] = None,
    owner_id: Optional[int] = None,
    start_time_after: Optional[datetime] = None,
    start_time_before: Optional[datetime] = None,
    sort_by: Optional[str] = None
) -> Dict[str, Any]:
    """Get events the user has access to, with pagination, filtering, and sorting"""
    permission_subquery = db.query(EventPermission.event_id).filter(
        EventPermission.user_id == user_id
    ).subquery()
    
    query = db.query(Event).filter(
        (Event.owner_id == user_id) | (Event.id.in_(permission_subquery))
    )

    if title:
        query = query.filter(Event.title.ilike(f"%{title}%"))
    if owner_id:
        query = query.filter(Event.owner_id == owner_id)
    if start_time_after:
        query = query.filter(Event.start_time >= start_time_after)
    if start_time_before:
        query = query.filter(Event.start_time <= start_time_before)

    if sort_by:
        if sort_by == "title":
            query = query.order_by(Event.title)
        elif sort_by == "start_time":
            query = query.order_by(Event.start_time)

    total = query.count()
    events = query.offset(skip).limit(limit).all()
    
    return {"items": events, "total": total}

def create_event(db: Session, event: EventCreate, owner_id: int) -> Event:
    """Create a new event. The creator is the owner."""
    db_event = Event(**event.model_dump(), owner_id=owner_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_event(
    db: Session,
    event_id: int,
    event: EventUpdate,
    user_id: int
) -> Optional[Event]:
    """Update an event, create a version and changelog entry."""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return None

    version_number = db.query(EventVersion).filter(
        EventVersion.event_id == event_id
    ).count() + 1

    version_data = model_to_dict(db_event) # Current state before update
    version = EventVersion(
        event_id=event_id,
        version_number=version_number,
        data=version_data,
        changed_by_user_id=user_id,
        timestamp=datetime.utcnow()
    )
    db.add(version)
    db.flush() # Ensure version.id is available for changelog

    changes = {}
    update_data = event.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(db_event, key)
        if old_value != value:
            changes[key] = {
                "old": old_value.isoformat() if isinstance(old_value, datetime) else old_value,
                "new": value.isoformat() if isinstance(value, datetime) else value
            }
    if changes:
        changelog = Changelog(
            event_id=event_id,
            version_id=version.id, # version.id should now be populated
            user_id=user_id,
            timestamp=datetime.utcnow(),
            changes=changes
        )
        db.add(changelog)

    for key, value in update_data.items():
        setattr(db_event, key, value)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def delete_event(db: Session, event_id: int, user_id: int) -> Optional[Event]:
    """Delete an event if user is owner."""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return None
    if db_event.owner_id != user_id:
        return None 
    db.delete(db_event)
    db.commit()
    return db_event

def create_events_batch(db: Session, events: List[EventCreate], owner_id: int) -> List[Event]:
    """Create multiple events in a single transaction."""
    db_events = []
    for event_data in events:
        db_event_obj = Event(**event_data.model_dump(), owner_id=owner_id)
        db.add(db_event_obj)
        db_events.append(db_event_obj)
    db.commit()
    for db_event_obj in db_events:
        db.refresh(db_event_obj)
    return db_events

# --- Permission CRUD Functions ---
def get_permissions_for_event(db: Session, event_id: int) -> List[Dict[str, Any]]:
    """Get all permissions for an event, including user and role details."""
    permissions = (
        db.query(EventPermission)
        .options(joinedload(EventPermission.user), joinedload(EventPermission.role))
        .filter(EventPermission.event_id == event_id)
        .all()
    )
    result = []
    for p in permissions:
        user_details = p.user
        role_details = p.role
        result.append({
            "id": p.id,
            "event_id": p.event_id,
            "user_id": user_details.id if user_details else None,
            "username": user_details.username if user_details else "N/A",
            "email": user_details.email if user_details else "N/A",
            "role_id": role_details.id if role_details else None,
            "role_name": role_details.name if role_details else "N/A"
        })
    return result

def update_permission(
    db: Session,
    event_id: int,
    user_id: int,
    role_id: int
) -> Optional[EventPermission]:
    """Update a user's permission for an event."""
    permission = db.query(EventPermission).filter(
        EventPermission.event_id == event_id,
        EventPermission.user_id == user_id
    ).first()
    if permission:
        permission.role_id = role_id
        db.add(permission)
        db.commit()
        db.refresh(permission)
    return permission

def delete_permission(
    db: Session,
    event_id: int,
    user_id: int
) -> bool:
    """Remove a user's permission for an event."""
    permission = db.query(EventPermission).filter(
        EventPermission.event_id == event_id,
        EventPermission.user_id == user_id
    ).first()
    if permission:
        db.delete(permission)
        db.commit()
        return True
    return False

# --- Version History and Rollback CRUD Functions ---

def get_specific_event_version(db: Session, event_version_id: int) -> Optional[EventVersion]:
    """
    Fetches a specific event version by its ID.
    """
    return db.query(EventVersion).filter(EventVersion.id == event_version_id).first()

def rollback_event_to_specific_version(
    db: Session,
    event_id: int,
    event_version_id: int,
    current_user_id: int
) -> Optional[Event]:
    """
    Rolls back an event to a specific version.
    - Updates the main event record.
    - Creates a new version record for this rollback action.
    - Creates a changelog entry for the rollback.
    """
    current_event = db.query(Event).filter(Event.id == event_id).first()
    if not current_event:
        return None

    target_version = db.query(EventVersion).filter(
        EventVersion.id == event_version_id,
        EventVersion.event_id == event_id
    ).first()
    if not target_version:
        return None

    rolled_back_data = target_version.data.copy()
    fields_to_update = {}
    original_event_state_before_rollback = model_to_dict(current_event)

    for key, value in rolled_back_data.items():
        if key in EventResponse.model_fields:
            if key in ["start_time", "end_time", "created_at", "updated_at"] and isinstance(value, str):
                try:
                    fields_to_update[key] = parser.parse(value)
                except (parser.ParserError, TypeError):
                    fields_to_update[key] = value 
            elif key not in ["id", "owner_id", "created_at", "updated_at"]: 
                fields_to_update[key] = value
    
    for key, value in fields_to_update.items():
        if hasattr(current_event, key):
            setattr(current_event, key, value)
    current_event.updated_at = datetime.utcnow()

    new_version_number_for_rollback = db.query(EventVersion).filter(
        EventVersion.event_id == event_id
    ).count() + 1
    
    data_for_new_version = model_to_dict(current_event)

    rollback_version_entry = EventVersion(
        event_id=event_id,
        version_number=new_version_number_for_rollback,
        data=data_for_new_version,
        changed_by_user_id=current_user_id,
        timestamp=datetime.utcnow()
    )
    db.add(rollback_version_entry)
    db.flush() # Ensure rollback_version_entry.id is available

    changes_due_to_rollback = {}
    for key, new_value_after_rollback in data_for_new_version.items():
        old_value_before_rollback = original_event_state_before_rollback.get(key)
        if new_value_after_rollback != old_value_before_rollback:
            changes_due_to_rollback[key] = {
                "old": old_value_before_rollback,
                "new": new_value_after_rollback
                }
            
    if changes_due_to_rollback:
        changelog_entry = Changelog(
            event_id=event_id,
            version_id=rollback_version_entry.id,
            user_id=current_user_id,
            timestamp=datetime.utcnow(),
            changes=changes_due_to_rollback
        )
        db.add(changelog_entry)

    db.commit()
    db.refresh(current_event)
    return current_event

# --- Changelog & Diff CRUD Functions ---

def get_event_changelog(db: Session, event_id: int) -> List[Dict[str, Any]]:
    """
    Fetches all changelog entries for a given event, ordered chronologically.
    Includes details of the user who made the change.
    """
    changelog_entries = (
        db.query(Changelog)
        .options(joinedload(Changelog.user_detail)) 
        .filter(Changelog.event_id == event_id)
        .order_by(Changelog.timestamp.asc())
        .all()
    )
    
    results = []
    for entry in changelog_entries:
        user_info = None
        if entry.user_detail:
            user_info = {
                "id": entry.user_detail.id,
                "username": entry.user_detail.username,
                "email": entry.user_detail.email,
            }
        results.append({
            "id": entry.id,
            "event_id": entry.event_id,
            "version_id": entry.version_id,
            "user_id": entry.user_id,
            "user_details": user_info,
            "timestamp": entry.timestamp,
            "changes": entry.changes,
        })
    return results

def get_diff_between_event_versions(
    db: Session,
    event_id: int,
    version_id1: int,
    version_id2: int
) -> Optional[Dict[str, Any]]:
    """
    Computes a diff between the 'data' fields of two EventVersion records for a specific event.
    Returns None if versions are not found or don't belong to the event.
    """
    ver1 = db.query(EventVersion).filter(
        EventVersion.id == version_id1,
        EventVersion.event_id == event_id
    ).first()

    ver2 = db.query(EventVersion).filter(
        EventVersion.id == version_id2,
        EventVersion.event_id == event_id
    ).first()

    if not ver1 or not ver2:
        return None

    data1 = ver1.data
    data2 = ver2.data

    diff_result = {}
    all_keys = set(data1.keys()).union(set(data2.keys()))

    for key in all_keys:
        val_from_v1 = data1.get(key)
        val_from_v2 = data2.get(key)
        
        if val_from_v1 != val_from_v2:
            diff_result[key] = {
                f"value_in_version_id_{version_id1}": val_from_v1,
                f"value_in_version_id_{version_id2}": val_from_v2
            }
    return diff_result
