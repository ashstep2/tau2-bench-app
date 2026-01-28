# Copyright Sierra
"""Toolkit for the IT Access & Permissions domain."""

from typing import List

from tau2.domains.it_access.data_model import ItAccessDB, Permission, User
from tau2.environment.toolkit import ToolKitBase, ToolType, is_tool


class ItAccessTools(ToolKitBase):
    """All the tools for the IT Access & Permissions domain."""

    db: ItAccessDB

    def __init__(self, db: ItAccessDB) -> None:
        super().__init__(db)

    def _get_new_permission_id(self) -> str:
        """Get a new deterministic permission id."""
        for perm_id in ["perm_new_001", "perm_new_002", "perm_new_003"]:
            if perm_id not in self.db.permissions:
                return perm_id
        raise ValueError("Too many permissions created")

    def _get_datetime(self) -> str:
        """Get a fixed datetime for deterministic output."""
        return "2024-05-15"

    def _get_user(self, user_id: str) -> User:
        """Get user from database."""
        if user_id not in self.db.users:
            raise ValueError(f"User {user_id} not found")
        return self.db.users[user_id]

    @is_tool(ToolType.READ)
    def get_user_info(self, user_id: str) -> User:
        """
        Get information about a user by their user ID.

        Args:
            user_id: The unique identifier of the user, such as 'user_001'.

        Returns:
            User object with name, email, department, role, and status.

        Raises:
            ValueError: If user_id not found.
        """
        return self._get_user(user_id)

    @is_tool(ToolType.READ)
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """
        Get all permissions for a specific user.

        Args:
            user_id: The unique identifier of the user, such as 'user_001'.

        Returns:
            List of Permission objects showing what resources the user can access.
        """
        return [p for p in self.db.permissions.values() if p.user_id == user_id]

    @is_tool(ToolType.WRITE)
    def grant_access(
        self, user_id: str, resource_id: str, access_level: str
    ) -> Permission:
        """
        Grant a user access to a resource.

        Args:
            user_id: The user to grant access to, such as 'user_001'.
            resource_id: The resource to grant access to, such as 'res_001'.
            access_level: Level of access - 'read', 'write', or 'admin'.

        Returns:
            The newly created Permission object.

        Raises:
            ValueError: If user or resource not found, or invalid access level.
        """
        if user_id not in self.db.users:
            raise ValueError(f"User {user_id} not found")
        if resource_id not in self.db.resources:
            raise ValueError(f"Resource {resource_id} not found")
        if access_level not in ["read", "write", "admin"]:
            raise ValueError(f"Invalid access level: {access_level}")

        user = self.db.users[user_id]
        if user.status != "active":
            raise ValueError(f"Cannot grant access to {user.status} user")

        for p in self.db.permissions.values():
            if p.user_id == user_id and p.resource_id == resource_id:
                raise ValueError(f"User {user_id} already has access to {resource_id}")

        permission_id = self._get_new_permission_id()
        permission = Permission(
            permission_id=permission_id,
            user_id=user_id,
            resource_id=resource_id,
            access_level=access_level,
            granted_date=self._get_datetime(),
        )
        self.db.permissions[permission_id] = permission
        return permission

    @is_tool(ToolType.WRITE)
    def revoke_access(self, user_id: str, resource_id: str) -> str:
        """
        Revoke a user's access to a resource.

        Args:
            user_id: The user to revoke access from, such as 'user_003'.
            resource_id: The resource to revoke access to, such as 'res_002'.

        Returns:
            Confirmation message.

        Raises:
            ValueError: If no matching permission found.
        """
        for perm_id, p in list(self.db.permissions.items()):
            if p.user_id == user_id and p.resource_id == resource_id:
                del self.db.permissions[perm_id]
                return f"Access revoked: {user_id} no longer has access to {resource_id}"
        raise ValueError(
            f"No permission found for user {user_id} on resource {resource_id}"
        )

    @is_tool(ToolType.GENERIC)
    def transfer_to_human_agents(self, summary: str) -> str:
        """
        Transfer the conversation to a human agent.

        Use this when the request requires manager approval, involves
        sensitive access, or is outside the scope of automated handling.

        Args:
            summary: Summary of the issue and why it needs human attention.

        Returns:
            Confirmation of transfer.
        """
        return "Transfer successful"
