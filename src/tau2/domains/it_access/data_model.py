# Copyright Sierra

from typing import Dict

from pydantic import BaseModel, Field

from tau2.domains.it_access.utils import IT_ACCESS_DB_PATH
from tau2.environment.db import DB


class User(BaseModel):
    """An employee in the system."""

    user_id: str = Field(description="Unique user identifier")
    name: str = Field(description="User's full name")
    email: str = Field(description="User's email address")
    department: str = Field(description="User's department")
    role: str = Field(description="User's job role")
    status: str = Field(description="active, inactive, or terminated")


class Resource(BaseModel):
    """A shared resource that can be accessed."""

    resource_id: str = Field(description="Unique resource identifier")
    name: str = Field(description="Resource name")
    type: str = Field(description="folder, application, or drive")
    owner_department: str = Field(description="Department that owns this resource")


class Permission(BaseModel):
    """A permission granting a user access to a resource."""

    permission_id: str = Field(description="Unique permission identifier")
    user_id: str = Field(description="User who has this permission")
    resource_id: str = Field(description="Resource being accessed")
    access_level: str = Field(description="read, write, or admin")
    granted_date: str = Field(description="When permission was granted")


class ItAccessDB(DB):
    """IT Access & Permissions Database."""

    users: Dict[str, User] = Field(description="All users indexed by user_id")
    resources: Dict[str, Resource] = Field(
        description="All resources indexed by resource_id"
    )
    permissions: Dict[str, Permission] = Field(
        description="All permissions indexed by permission_id"
    )


def get_db() -> ItAccessDB:
    return ItAccessDB.load(IT_ACCESS_DB_PATH)
