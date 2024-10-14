from prometheus_client import Counter

CORRECT_LINK = Counter(
    'correct_link',
    'Total number of correct link'
)
INCORRECT_LINK = Counter(
    'incorrect_link',
    'Total number of incorrect link'
)

CLICKS_ON_THE_STUB = Counter(
    'clicks_of_the_stub',
    'Total number of clicks on the stub'
)

ADDITION_TO_CHAT = Counter(
    'addition_to_chat',
    'Total number of additions to chat'
)

TIMEOUT_TO_ADD_TO_CHAT = Counter(
    'timeout_to_add_to_chat',
    'Total number of timeouts to add to chat'
)
SUCCESSFULLY_PARSING = Counter(
    'successfully_parsing',
    'Total number of succesful parsing'
)

PARSING_FAILED_PERMISSION_DENIED = Counter(
    'parsing_failed_permission_denied',
    'Total number of parsing failed because of permission denied'
)
PARSING_FAILED_VALUE_ERROR = Counter(
    'parsing_failed_value_error',
    'Total number of parsing failed because of value error'
)

TOTAL_FAILED_ATTEMPS = Counter(
    'total_failed_attemps',
    'Total number of failed attemps'
)
