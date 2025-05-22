# app/models/__init__.py
from .user import User, Role
from .event import Event
from .permission import EventPermission
from .version import EventVersion
from .changelog import Changelog

# This allows you to import like: from app.models import User, Event, etc.
