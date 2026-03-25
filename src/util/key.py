from typing import Dict, Any, List
async def validate(valid_keys: set[Any] | List[Any], current_keys: set[Any] | List[Any]) -> Dict[str, Any]:
    illegal_keys = []
    for key in current_keys:
        if key not in valid_keys:
            illegal_keys.insert(0, key)
    
    if len(illegal_keys) > 0:
        return {"valid": False, "illegal_keys": illegal_keys}
    else:
        return {"valid": True, "illegal_keys": None}