from typing import Any, Callable

from lfx.io import MessageTextInput
from langflow.inputs import MultilineInput
from pydantic import BaseModel

from lfx.base.agents.agent import LCToolsAgentComponent
from lfx.io import Output

from langchain_core.runnables import Runnable
from lfx.schema.message import Message
from lfx.log.logger import logger


class PoliciesComponent(LCToolsAgentComponent):
    def create_agent_runnable(self) -> Runnable:
        pass

    display_name = "ToolGuard Buildtime"
    description = "Buildtime (offline) component converting textual policies to executable ToolGuard code."
    documentation: str = "..."  # once we have a URL or alike
    icon = "clipboard-check"  # consider also file-text
    name = "policies"
    beta = True

    inputs = [
        MultilineInput(
            name="policies",
            display_name="Business Policies",
            info="Company business policies: concise, well-defined, self-contained policies, one in a line.",
            value="<example: division by zero is prohibited>",
            # advanced=True,
        ),
        MessageTextInput(
            name="guard_code_path",
            display_name="ToolGuards Generated Code Path",
            info="Automatically generated ToolGuards code",
            # show_if={"enable_tool_guard": True},  # conditional visibility  # check how to do that
            #advanced=False,
        ),

        *LCToolsAgentComponent.get_base_inputs()[0:1],
    ]
    outputs = [
        Output(display_name="ToolGuard Code", name="guard_code", method="build_guards"),
    ]

    def run(self):
        pass

    def build_guards(self) -> Message:
        """ToolGuard buidtime component (both steps)

        Args:
        Returns:
            A textual message with the generated code for human review
        """

        if self.policies:
            logger.info(f"🔒️ToolGuard: Building guards for {self.policies}")
            logger.info(f"🔒️ToolGuard: Using the following tools {self.tools}")
        else:
            logger.error("🔒️ToolGuard: Policies cannot be empty!")

        # TODO: the actual buildtime code should come here, and the final result assigned to guard_code
        guard_code = f"def book_reservation_guard(args, history, api):\n" \
                     f"     if int(args.passengers) == 0:\n" \
                     f"         raise PolicyValidationException('A reservation must have at least one passenger.')\n" \
                     f"     if int(args.passengers) > 5:\n" \
                     f"         raise PolicyValidationException('A reservation can include up to five passengers.')\n" \
                     f"     ... \n"

        guard_code += ('\n\n' + self.guard_code_path)

        return Message(text=guard_code, sender="toolguard buildtime")
