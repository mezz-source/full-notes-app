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