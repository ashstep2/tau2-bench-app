# Copyright Sierra
"""An agent that verifies write operations by checking permissions after changes."""

import uuid
from typing import List, Optional

from tau2.agent.llm_agent import LLMAgent, LLMAgentState
from tau2.data_model.message import AssistantMessage, ToolCall, ToolMessage
from tau2.environment.tool import Tool


class VerifyingAccessAgent(LLMAgent):
    """
    An LLM agent that automatically verifies write operations.

    After grant_access or revoke_access succeeds, this agent forces a
    verification call to get_user_permissions before responding to the user.
    """

    WRITE_TOOLS = {"grant_access", "revoke_access"}
    VERIFY_TOOL = "get_user_permissions"

    def __init__(
        self,
        tools: List[Tool],
        domain_policy: str,
        llm: Optional[str] = None,
        llm_args: Optional[dict] = None,
    ):
        super().__init__(
            tools=tools,
            domain_policy=domain_policy,
            llm=llm,
            llm_args=llm_args,
        )

    def _get_last_tool_call(self, state: LLMAgentState) -> Optional[ToolCall]:
        """Find the most recent tool call from assistant messages."""
        for msg in reversed(state.messages):
            if isinstance(msg, AssistantMessage) and msg.tool_calls:
                return msg.tool_calls[0]
        return None

    def _needs_verification(
        self, message: ToolMessage, state: LLMAgentState
    ) -> Optional[str]:
        """
        Check if the incoming tool message needs verification.

        Returns the user_id to verify, or None if no verification needed.
        """
        if message.error:
            return None

        tool_call = self._get_last_tool_call(state)
        if tool_call is None:
            return None

        if tool_call.name not in self.WRITE_TOOLS:
            return None

        return tool_call.arguments.get("user_id")

    def _make_verification_call(self, user_id: str) -> AssistantMessage:
        """Create an AssistantMessage with a verification tool call."""
        return AssistantMessage(
            role="assistant",
            content=None,
            tool_calls=[
                ToolCall(
                    id=f"verify_{uuid.uuid4().hex[:8]}",
                    name=self.VERIFY_TOOL,
                    arguments={"user_id": user_id},
                )
            ],
        )

    def generate_next_message(
        self, message, state: LLMAgentState
    ) -> tuple[AssistantMessage, LLMAgentState]:
        """
        Generate the next message, with automatic verification after writes.
        """
        # Check if this is a tool result that needs verification
        if isinstance(message, ToolMessage):
            user_id = self._needs_verification(message, state)
            if user_id is not None:
                # Add the tool result to state
                state.messages.append(message)
                # Return a verification call instead of letting LLM respond
                verification = self._make_verification_call(user_id)
                state.messages.append(verification)
                return verification, state

        # Normal LLM behavior
        return super().generate_next_message(message, state)
