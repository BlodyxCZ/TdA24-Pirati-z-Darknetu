lecturer_post_schema = {
    "type": "object",
    "properties": {
        "title_before": {"type": "string"},
        "first_name": {"type": "string"},
        "middle_name": {"type": "string"},
        "last_name": {"type": "string"},
        "title_after": {"type": "string"},
        "picture_url": {"type": "string"},
        "location": {"type": "string"},
        "claim": {"type": "string"},
        "bio": {"type": "string"},
        "price_per_hour": {"type": "number"},
    },
    "required": ["first_name", "last_name", "picture_url", "location", "claim", "bio", "price_per_hour"]
}