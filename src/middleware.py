from typing import Any, Callable
from fastapi.routing import APIRoute

class ExcludeNoneRoute(APIRoute):
    """
    Overriding the default APIRoute class to exclude null values from responses by default.
    Ensures that fields with null/None data are omitted entirely from JSON payloads, 
    making it cleaner for consumption in Flutter.
    """
    def __init__(self, path: str, endpoint: Callable[..., Any], **kwargs: Any) -> None:
        if "response_model_exclude_none" not in kwargs:
            kwargs["response_model_exclude_none"] = True
        super().__init__(path, endpoint, **kwargs)
