from typing import cast
from lfx.io import MessageTextInput
from langflow.inputs import MultilineInput

from lfx.base.agents.agent import LCToolsAgentComponent
from lfx.io import Output

from langchain_core.runnables import Runnable
from lfx.schema.message import Message
from lfx.log.logger import logger
from os.path import join

from altk.core.llm.base import get_llm
from altk.core.toolkit import AgentPhase
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
    ToolGuardCodeComponent,
    MeleaSessionData
)

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

    async def _build_guard_specs(self):
        LLMClient = get_llm("litellm.output_val")
        config = ToolGuardSpecComponentConfig(
            llm_client = LLMClient(
                model_name=MODEL,
                custom_llm_provider="azure", #FIXME
            )
        )
        component = ToolGuardSpecComponent(config = config)
        toolguard_step1_dir = join(self.guard_code_path, STEP1)
        input = ToolGuardSpecBuildInput(
            policy_text=self.policies,
            tools=self.tools,
            out_dir=toolguard_step1_dir,
        )
        return cast(
            ToolGuardSpecs,
            await component.aprocess(input, phase=AgentPhase.BUILDTIME)
        )

    async def _build_guard_code(self, specs: ToolGuardSpecs)->ToolGuardBuildOutput:
        config = ToolGuardCodeComponentConfig(
            llm_config = MeleaSessionData()
        )
        component = ToolGuardCodeComponent(config=config)

        work_dir = self.guard_code_path
        out_dir = join(work_dir, STEP2)
        build_input = ToolGuardCodeBuildInput(
            tools=self.tools,
            toolguard_specs = specs,
            out_dir=out_dir,
        )
        output = cast(ToolGuardBuildOutput,
            await component.aprocess(build_input, phase=AgentPhase.BUILDTIME)
        )
        return output

    async def build_guards(self) -> Message:
        assert self.policies, "🔒️ToolGuard: Policies cannot be empty!"

        logger.info(f"🔒️ToolGuard: Building guards for {self.policies}")
        logger.info(f"🔒️ToolGuard: Using the following tools {self.tools}")

        specs = await self._build_guard_specs()
        guards = await self._build_guard_code(specs)
        
        return Message(text=guards.out_dir, sender="toolguard buildtime")