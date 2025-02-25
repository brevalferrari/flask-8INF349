class Json:
    _inner: str

    def __init__(self, json: dict):
        self._inner = json

    def is_like(self, schema: dict) -> bool:
        """Check if a JSON object matches a JSON schema.

        Args:
            schema (dict): JSON validation schema (key: type or key: {key: type} etc).

        Returns:
            bool: Wether this is a valid JSON according to the provided schema or not.
        """
        for k, v in schema.items():
            if (k not in self._inner) or (
                (
                    (is_dict := isinstance(v, dict))
                    and not Json(self._inner[k]).is_like(v)
                )
                or (not is_dict and not isinstance(self._inner[k], v))
            ):
                return False
        return True
