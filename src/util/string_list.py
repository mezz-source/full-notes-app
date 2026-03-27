async def add_item(string_list: str, item: str) -> str:
    items = string_list.split(",") if string_list else []
    if item not in items:
        items.append(item)
    return ",".join(items)

async def remove_item(string_list: str, item: str) -> str:
    items = string_list.split(",") if string_list else []
    if item in items:
        items.remove(item)
    return ",".join(items)

async def add_many_items(string_list: str, items: list) -> str:
    existing_items = string_list.split(",") if string_list else []
    for item in items:
        if item not in existing_items:
            existing_items.append(item)
    return ",".join(existing_items)

async def remove_many_items(string_list: str, items: list) -> str:
    existing_items = string_list.split(",") if string_list else []
    for item in items:
        if item in existing_items:
            existing_items.remove(item)
    return ",".join(existing_items)

async def parse_string_list(string_list: str) -> list:
    """Safely parse a comma-separated string into a list, filtering blanks"""
    if not string_list:
        return []
    return [item.strip() for item in string_list.split(",") if item.strip()]

async def filter_valid_items(items: list, valid_set: set) -> list:
    """Filter items to only those in the valid set"""
    return [item for item in items if item in valid_set]

async def remove_items_force(string_list: str, items_to_remove: list) -> str:
    """Remove items from string_list regardless of whether they are valid (allows cleanup of stale items)"""
    existing_items = await parse_string_list(string_list)
    for item in items_to_remove:
        if item in existing_items:
            existing_items.remove(item)
    return ",".join(existing_items)