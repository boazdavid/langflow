import json
from typing import Any, List, Dict, cast

from langchain_core.messages import BaseMessage
from altk.pre_tool.toolguard.toolguard_spec_component import (
    ToolGuardSpecComponentConfig,
    ToolGuardSpecBuildInput,
    ToolGuardSpecs,
    ToolGuardSpecComponent
)
from altk.pre_tool.toolguard.toolguard_code_component import (
    ToolGuardCodeComponentConfig,
    ToolGuardCodeBuildInput,
    ToolGuardBuildOutput,
    ToolGuardCodeRunInput,
    ToolGuardCodeRunOutput,
    ToolGuardCodeComponent,
)
from altk.pre_tool.toolguard.toolguard.runtime import LangchainToolInvoker

from altk.core.toolkit import AgentPhase
from lfx.base.agents.altk_base_agent import ALTKBaseTool, BaseToolWrapper
from lfx.field_typing.constants import BaseTool
from lfx.log.logger import logger
from pydantic import Field


class GuardedTool(ALTKBaseTool):
    """A wrapper tool that validates calls before execution using ToolGuard component.
    In case of error in ToolGuard code execution, the tool is activated w/o the guard code.
    """

    conversation_context: list[BaseMessage]| None = None
    tools: list[BaseTool]| None = None
    guard_path: str| None = None

    def __init__(
        self, 
        name: str,
        description: str,
        wrapped_tool: BaseTool, 
        agent: Any,
        # toolguard_component=None, 
        tools: List[BaseTool], 
        guard_path: str, 
        conversation_context:list[BaseMessage]
    ):
        super().__init__(
            name=name,
            description=description,
            wrapped_tool=wrapped_tool,
            agent=agent
        )
        self.tools = tools
        self.guard_path = guard_path
        self.conversation_context = conversation_context

    def _run(self, *args, **kwargs) -> str:
        return self._validate_and_run(*args, **kwargs)

    async def _arun(self, *args, **kwargs) -> str:
        return self._validate_and_run(*args, **kwargs)

    def _validate_and_run(self, *args, **kwargs) -> str:
        tool_guard_arguments = {
            "function": {
                "name": self.name, 
                "arguments": json.dumps(self._prepare_arguments(*args, **kwargs))
            }
        }
        logger.info(f"GuardedTool._validate_and_run() + {tool_guard_arguments}, guard_path = {self.guard_path}")
        logger.info(f"{self.guard_path}, tools={len(self.tools)}")
        try:
            # toolGuard invocation point
            result = self.toolguard_validation(
                toolguard_path=self.guard_path,
                fc=[tool_guard_arguments],
                messages=self.conversation_context,
                tools=self.tools,
            )
            logger.info(f"result={result}")
            if not result.violation:  # tool guard returned Ok
                logger.info(f"🔒️[Ok] ToolGuard evaluated and approved running {self.name}")
                return self._execute_tool(*args, **kwargs)

            logger.info(f"🔒️[X] ToolGuard evaluated and rejected running {self.name}")
            error_msg = result.violation.user_message or "Policy violation"
            return error_msg

        except Exception as e:
            logger.error(f"🔒️ToolGuard: error during validation: {e}")
            # execute directly on error (no fallback validation)
            return self._execute_tool(*args, **kwargs)

    def _prepare_arguments(self, *args, **kwargs) -> dict[str, Any]:
        # remove config parameter if present (not needed for validation)
        clean_kwargs = {k: v for k, v in kwargs.items() if k != "config"}
        return clean_kwargs

    def update_context(self, conversation_context: list[BaseMessage]):
        """Update the conversation context."""
        self.conversation_context = conversation_context

    def toolguard_validation(self, toolguard_path: str, fc: List[Dict], messages: List[BaseMessage], tools: List[BaseTool]) -> ToolGuardRunOutput:
        """Umbrella function for tool guards invocation
        Args:
            toolguard_path: path to toolguard generated code
            fc: the function to be called, along with its arguments
            messages: conversation history till this point
            tools: a list of all tools
        Returns:
            ToolGuardRunOutput: potentially with a violation object
        """
        config = ToolGuardCodeComponentConfig()
        component = ToolGuardCodeComponent(config=config)
        tool_name = fc[0]['function']['name']
        tool_args = {"args": json.loads(fc[0]['function']['arguments'])}
        logger.info(f"toolguarding tool={tool_name}, toolguard_path = {toolguard_path}")
        tool_invoker = LangchainToolInvoker(tools)
        toolguard_input = ToolGuardCodeRunInput(
            generated_guard_dir=toolguard_path,
            tool_name=tool_name,
            tool_args=tool_args,
            tool_invoker=tool_invoker,
            messages=messages,
            metadata={}
        )
        toolguard_output = cast(
            ToolGuardCodeRunOutput,
            component.process(toolguard_input, phase=AgentPhase.RUNTIME),
        )
        return toolguard_output


class PreToolGuardWrapper(BaseToolWrapper):
    """Tool wrapper that adds pre-tool tool guard capabilities.
    This wrapper validates tool calls before execution using the ToolGuard
    component to make sure the call does not violate policies.
    """
    tools: List[BaseTool] = []
    guard_path: str|None = None
    
    @property
    def is_available(self) -> bool:
        return True

    def wrap_tool(self, tool: BaseTool, **kwargs) -> BaseTool:
        logger.info(f"-----in wrap tool")
        # Check if validation is explicitly disabled
        enable_tool_guard = kwargs.get("enable_tool_guard", True)
        if not enable_tool_guard:
            logger.info(f"🔒️ToolGuard explicitly disabled for {tool.name}")
            return tool

        # self.guard_path = kwargs.get("guard_path", '<placeholder for path>')

        if isinstance(tool, GuardedTool):
            logger.info(f"Updating GuardedTool guard_path={self.guard_path}")
            # Already wrapped, update context and tool specs
            # tool.guard = self.tool_guard_component
            tool.tools = self.tools
            tool.guard_path = self.guard_path
            if "conversation_context" in kwargs:
                tool.update_context(kwargs["conversation_context"])
            logger.info(f"🔒️Updated existing {tool.name} with {len(self.tools)} tool")
            return tool

        # Wrap with tool guard
        logger.info(f"Creating GuardedTool guard_path={self.guard_path}")
        return GuardedTool(
            name = tool.name,
            description=f"guard: {tool.description}",
            wrapped_tool=tool,
            agent = kwargs.get("agent"),
            # tool_guard_component=self.tool_guard_component,
            tools=self.tools,
            guard_path=self.guard_path,
            conversation_context=kwargs.get("conversation_context", []),
        )