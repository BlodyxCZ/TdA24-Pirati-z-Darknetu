lecturer_schema = {
    "type": "object",
    "properties": {
        "first_name": {"type": str, "required": True},
        "middle_name": {"type": str, "required": False},
        "last_name": {"type": str, "required": True},
        "title_before": {"type": str, "required": False},
        "title_after": {"type": str, "required": False},
        "picture_url": {"type": str, "required": True},
        "location": {"type": str, "required": True},
        "claim": {"type": str, "required": True},
        "bio": {"type": str, "required": True},
        "price_per_hour": {"type": int, "required": True},
        "contact": {"type": dict, "required": True},
        "tags": {"type": list, "required": False},
    },
}


""" def validate_post_lecturer(data: dict) -> bool:
    for key, prop in lecturer_schema:
        if prop["required"]:
            if key not in data or data[key] is None or (isinstance(data[key], str) and data[key].strip() == ""):
                return False
        if key in data and not isinstance(data[key], prop["type"]):
            return False

    return True """