
from langflow.inputs import MultilineInput
from lfx.components.input_output import TextInputComponent
from lfx.io import Output


class PoliciesTextInput(TextInputComponent):
    display_name = "Business Policies Input"
    description = "A list of company business policies."
    #documentation: str = "https://docs.langflow.org/components-io#text-input"
    icon = "clipboard-check"  # consider also file-text
    name = "policies_text"
    beta = True

    inputs = [
        MultilineInput(
            name="input_value",
            display_name="Business Policies",
            info="A list of company business policies.",
        ),
    ]
    outputs = [
        Output(display_name="Output", name="text", method="text_response"),
    ]
