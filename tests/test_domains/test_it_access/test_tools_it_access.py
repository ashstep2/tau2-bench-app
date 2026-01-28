# Copyright Sierra

import json

import pytest

from tau2.data_model.message import ToolCall
from tau2.domains.it_access.data_model import ItAccessDB
from tau2.domains.it_access.environment import get_environment
from tau2.environment.environment import Environment


@pytest.fixture
def it_access_db() -> ItAccessDB:
    return ItAccessDB(
        users={
            "user_001": {
                "user_id": "user_001",
                "name": "Alice Johnson",
                "email": "alice.johnson@company.com",
                "department": "Engineering",
                "role": "Software Engineer",
                "status": "active",
            },
            "user_002": {
                "user_id": "user_002",
                "name": "Bob Smith",
                "email": "bob.smith@company.com",
                "department": "Marketing",
                "role": "Marketing Manager",
                "status": "active",
            },
            "user_003": {
                "user_id": "user_003",
                "name": "Charlie Brown",
                "email": "charlie.brown@company.com",
                "department": "Engineering",
                "role": "Former Contractor",
                "status": "terminated",
            },
        },
        resources={
            "res_001": {
                "resource_id": "res_001",
                "name": "Engineering Shared Drive",
                "type": "drive",
                "owner_department": "Engineering",
            },
            "res_002": {
                "resource_id": "res_002",
                "name": "Project Alpha Folder",
                "type": "folder",
                "owner_department": "Engineering",
            },
        },
        permissions={
            "perm_001": {
                "permission_id": "perm_001",
                "user_id": "user_002",
                "resource_id": "res_002",
                "access_level": "read",
                "granted_date": "2024-01-15",
            },
        },
    )


@pytest.fixture
def environment(it_access_db: ItAccessDB) -> Environment:
    return get_environment(it_access_db)


@pytest.fixture
def get_user_info_call() -> ToolCall:
    return ToolCall(
        id="0",
        name="get_user_info",
        arguments={"user_id": "user_001"},
    )


def test_get_user_info(environment: Environment, get_user_info_call: ToolCall):
    response = environment.get_response(get_user_info_call)
    assert not response.error
    user = json.loads(response.content)
    assert user["user_id"] == "user_001"
    assert user["name"] == "Alice Johnson"
    # Check error for non-existent user
    get_user_info_call.arguments["user_id"] = "nonexistent"
    response = environment.get_response(get_user_info_call)
    assert response.error


@pytest.fixture
def get_user_permissions_call() -> ToolCall:
    return ToolCall(
        id="1",
        name="get_user_permissions",
        arguments={"user_id": "user_002"},
    )


def test_get_user_permissions(
    environment: Environment, get_user_permissions_call: ToolCall
):
    response = environment.get_response(get_user_permissions_call)
    assert not response.error
    permissions = json.loads(response.content)
    assert len(permissions) == 1
    assert permissions[0]["resource_id"] == "res_002"
    # Check empty permissions for user with none
    get_user_permissions_call.arguments["user_id"] = "user_001"
    response = environment.get_response(get_user_permissions_call)
    assert not response.error
    permissions = json.loads(response.content)
    assert len(permissions) == 0


@pytest.fixture
def grant_access_call() -> ToolCall:
    return ToolCall(
        id="2",
        name="grant_access",
        arguments={
            "user_id": "user_001",
            "resource_id": "res_001",
            "access_level": "read",
        },
    )


def test_grant_access(environment: Environment, grant_access_call: ToolCall):
    response = environment.get_response(grant_access_call)
    assert not response.error
    permission = json.loads(response.content)
    assert permission["user_id"] == "user_001"
    assert permission["resource_id"] == "res_001"
    # Verify permission exists
    permissions = environment.tools.get_user_permissions("user_001")
    assert len(permissions) == 1
    # Check error for duplicate grant
    response = environment.get_response(grant_access_call)
    assert response.error


def test_grant_access_to_terminated_user(environment: Environment):
    call = ToolCall(
        id="3",
        name="grant_access",
        arguments={
            "user_id": "user_003",
            "resource_id": "res_001",
            "access_level": "read",
        },
    )
    response = environment.get_response(call)
    assert response.error
    assert "terminated" in response.content.lower()


def test_grant_access_invalid_access_level(environment: Environment):
    call = ToolCall(
        id="4",
        name="grant_access",
        arguments={
            "user_id": "user_001",
            "resource_id": "res_001",
            "access_level": "superadmin",
        },
    )
    response = environment.get_response(call)
    assert response.error


@pytest.fixture
def revoke_access_call() -> ToolCall:
    return ToolCall(
        id="5",
        name="revoke_access",
        arguments={"user_id": "user_002", "resource_id": "res_002"},
    )


def test_revoke_access(environment: Environment, revoke_access_call: ToolCall):
    # Verify permission exists first
    permissions = environment.tools.get_user_permissions("user_002")
    assert len(permissions) == 1
    # Revoke access
    response = environment.get_response(revoke_access_call)
    assert not response.error
    # Verify permission removed
    permissions = environment.tools.get_user_permissions("user_002")
    assert len(permissions) == 0
    # Check error for revoking non-existent permission
    response = environment.get_response(revoke_access_call)
    assert response.error


@pytest.fixture
def transfer_to_human_agents_call() -> ToolCall:
    return ToolCall(
        id="6",
        name="transfer_to_human_agents",
        arguments={"summary": "User needs admin access to production database"},
    )


def test_transfer_to_human_agents(
    environment: Environment, transfer_to_human_agents_call: ToolCall
):
    response = environment.get_response(transfer_to_human_agents_call)
    assert not response.error
    assert "transfer" in response.content.lower()
