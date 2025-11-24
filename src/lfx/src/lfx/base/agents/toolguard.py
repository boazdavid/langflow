import json
from typing import List, Dict, cast

from langchain_core.messages import BaseMessage
from altk.pre_tool_guard_toolkit import ToolGuardRunInput, ToolGuardRunOutput, ToolGuardComponentConfig, PreToolGuardComponent, LangchainToolInvoker

from altk.toolkit_core.core.toolkit import AgentPhase
from lfx.field_typing.constants import BaseTool


def toolguard_validation(toolguard_path: str, fc: List[Dict], messages: List[BaseMessage], tools: List[BaseTool]) -> ToolGuardRunOutput:
    """Umbrella function for tool guards invocation
    Args:
        toolguard_path: path to toolguard generated code
        fc: the function to be called, along with its arguments
        messages: conversation history till this point
        tools: a list of all tools
    Returns:
        ToolGuardRunOutput: potentially with a violation object
    """
    config = ToolGuardComponentConfig()
    component = PreToolGuardComponent(config=config)

    tool_name = fc[0]['function']['name']
    tool_args = {"args": json.loads(fc[0]['function']['arguments'])}
    tool_invoker = LangchainToolInvoker(tools)
    toolguard_input = ToolGuardRunInput(
        generated_guard_dir=toolguard_path,
        tool_name=tool_name,
        tool_args=tool_args,
        tool_invoker=tool_invoker,
        messages=messages,
        metadata={}
    )
    toolguard_output = cast(
        ToolGuardRunOutput,
        component.process(toolguard_input, phase=AgentPhase.RUNTIME),
    )
    return toolguard_output