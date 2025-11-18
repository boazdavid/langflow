import asyncio
from typing import cast
from langflow.inputs import MultilineInput
from lfx.base.agents.agent import LCToolsAgentComponent
from lfx.io import Output

from langchain_core.runnables import Runnable
from lfx.schema.message import Message
from lfx.log.logger import logger
from os.path import join

# from altk.toolkit_core.llm.base import get_llm
# from altk.toolkit_core.core.toolkit import AgentPhase
# from altk.pre_tool_guard_toolkit.pre_tool_guard.pre_tool_guard import PreToolGuardComponent
# from altk.pre_tool_guard_toolkit.core.types import ToolGuardComponentConfig, ToolGuardBuildInput, ToolGuardBuildOutput 

MODEL = "gpt-4o-2024-08-06"
STEP1 = "Step_1"
STEP2 = "Step_2"

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

        # OPENAILiteLLMClientOutputVal = get_llm("litellm.output_val")
        # config = ToolGuardComponentConfig(
        #     llm_client = OPENAILiteLLMClientOutputVal(
        #         model_name=MODEL,
        #         custom_llm_provider="azure",
        #     )
        # )
        # component = PreToolGuardComponent(config = config)
        # print("tools=", self.tools)

        # work_dir = "example"
        # toolguard_step1_dir = join(work_dir, STEP1)
        # out_dir = join(work_dir, STEP2)
        # build_input = ToolGuardBuildInput(
        #     policy_text=self.policies,
        #     tools=self.tools,
        #     step1_dir = toolguard_step1_dir,
        #     out_dir=out_dir,
        #     app_name="my_app"
        # )
        # output = cast(ToolGuardBuildOutput, asyncio.run(
        #     component.aprocess(build_input, phase=AgentPhase.BUILDTIME)
        # ))
        # return Message(text=output.generated_code.root_dir, sender="toolguard buildtime")


        # TODO: the actual buildtime code should come here, and the final result assigned to guard_code
        guard_code = f"def book_reservation_guard(args, history, api):\n" \
                     f"     if int(args.passengers) == 0:\n" \
                     f"         raise PolicyValidationException('A reservation must have at least one passenger.')\n" \
                     f"     if int(args.passengers) > 5:\n" \
                     f"         raise PolicyValidationException('A reservation can include up to five passengers.')\n" \
                     f"     ... \n"
                    
        return Message(text=guard_code, sender="toolguard buildtime")
    