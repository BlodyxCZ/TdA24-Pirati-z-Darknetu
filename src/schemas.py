lecturer_schema = {
    "first_name": {"type": str, "required": True},
    "middle_name": {"type": str, "required": False},
    "last_name": {"type": str, "required": True},
    "title_before": {"type": str, "required": False},
    "title_after": {"type": str, "required": False},
    "picture_url": {"type": str, "required": False},
    "location": {"type": str, "required": False},
    "claim": {"type": str, "required": False},
    "bio": {"type": str, "required": False},
    "price_per_hour": {"type": int, "required": False},
    "contact": {"type": dict, "required": False},
    "tags": {"type": list, "required": False},
}


def validate_post_lecturer(data: dict) -> bool:
    # Check if it's a dict
    if not isinstance(data, dict):
        return False
    
    """ # Check if all required fields are present
    for field in lecturer_schema:
        if lecturer_schema[field]["required"] and field not in data:
            return False """
    
    # Check if the required fields are not None
    for field in lecturer_schema:
        if lecturer_schema[field]["required"] and data[field] is None:
            return False
        
    # Check for unknown fields
    for field in data:
        if field not in lecturer_schema:
            return False

    """ # Check if all fields are of the correct type
    for field in data:
        if not isinstance(data[field], lecturer_schema[field]["type"]):
            return False """
        
    return True