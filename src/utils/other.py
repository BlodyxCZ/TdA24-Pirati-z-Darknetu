from dateutil import parser

def format_datetime(datetime_str: str) -> str:
    # input: 2024-02-26T14:48:43.931030439Z (ISO 8601)
    # output: 26.02.2024 14:48
    return parser.parse(datetime_str).strftime('%d.%m.%Y %H:%M')
