from typing import Callable, List, Dict

from langchain_core.messages import BaseMessage
from lfx.log.logger import logger


def tool_guard_validation(fc: List[Dict], messages: List[BaseMessage], tool_specs: List[Callable]) -> Dict:
    """Umbrella function for tool guards invocation

    Args:
        fc: the function to be called, along with its arguments
        messages: conversation history till this point
        tool_specs: a list of all tool specs

    Returns:
        A dictionary with validation result and error message, if any
    """

    #print(f'function_call: {fc}, tool_specs: {tool_specs}, messages: {messages}')

    func = fc[0]['function']['name']
    args = fc[0]['function']['arguments']

    logger.info(f'🔒️ToolGuard invocation for {func}: {func+" guard"}')

    # TODO: invoke the appropriate tool guard code
    #  return dictionary with "valid" (bool) and "error_msg" (str)

    return evaluate_expression_guard(args)


def evaluate_expression_guard(args: str) -> Dict:
    if '/2' in args:  # division by two, just as an example
        result = {'valid': False, 'error_msg': 'error raised in tool guard code: division by two is illegal\n'}
    else:
        result = {'valid': True, 'error_msg': None}
    return result

