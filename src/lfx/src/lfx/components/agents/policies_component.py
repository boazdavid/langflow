from langflow.inputs import MultilineInput
from lfx.base.agents.agent import LCToolsAgentComponent
from lfx.io import Output

from langchain_core.runnables import Runnable
from lfx.schema.message import Message
from lfx.log.logger import logger


class PoliciesComponent(LCToolsAgentComponent):
    def create_agent_runnable(self) -> Runnable:
        pass

    display_name = "Business Policies"
    description = "A list of clear and concise policies - one in a line, atomic and self-contained."
    documentation: str = "..."  # once we have a URL or alike
    icon = "clipboard-check"  # consider also file-text
    name = "policies"
    beta = True

    inputs = [
        MultilineInput(
            name="policies",
            display_name="ToolGuard Business Policies",
            info="Company business policies: concise, well-defined, self-contained policies, one in a line.",
            value="<example: division by zero is prohibited>",
            # advanced=True,
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
            logger.info(f"🔒️ToolGuard: Using the following tool specs {self.tools}")
        else:
            logger.error("🔒️ToolGuard: Policies cannot be empty!")

        # TODO: the actual buildtime code should come here, and the final result assigned to guard_code
        guard_code = "generated python code"

        return Message(text=guard_code, sender="toolguard buildtime")
