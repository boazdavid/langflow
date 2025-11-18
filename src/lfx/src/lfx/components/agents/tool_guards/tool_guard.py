import json
from typing import Callable, List, Dict, Any

from langchain_core.messages import BaseMessage
from lfx.log.logger import logger


def tool_guard_validation(path: str, fc: List[Dict], messages: List[BaseMessage], tools: List[Callable]) -> Dict:
    """Umbrella function for tool guards invocation

    Args:
        fc: the function to be called, along with its arguments
        messages: conversation history till this point
        tools: a list of all tool specs

    Returns:
        A dictionary with validation result and error message, if any
    """

    func = fc[0]['function']['name']
    args = fc[0]['function']['arguments']

    logger.info(f'🔒️ToolGuard invocation for {func}: {func+" guard"} with guard code at {path}')

    # TODO: invoke the appropriate tool guard code
    #  return dictionary with "valid" (bool) and "error_msg" (str)

    return book_reservation_guard(json.loads(args))


def book_reservation_guard(args: Dict[str, str]) -> Dict:
    logger.info(f'🔒️ToolGuard: in book_reservation_guard with: {args}')
    if int(args['passengers_number']) == 0:
        result = {'valid': False, 'error_msg': 'flight reservation must have at least one passenger\n'}
    elif int(args['passengers_number']) > 5:
        result = {'valid': False, 'error_msg': 'flight reservations with more than five passengers are not allowed\n'}
    else:
        result = {'valid': True, 'error_msg': None}
    return result

