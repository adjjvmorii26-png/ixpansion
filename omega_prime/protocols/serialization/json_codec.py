import json
from datetime import date, datetime
from typing import Any


class OPJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, (set, frozenset)):
            return list(o)
        if hasattr(o, "to_dict"):
            return o.to_dict()
        return super().default(o)


def dumps(data: Any) -> str:
    return json.dumps(data, cls=OPJSONEncoder, sort_keys=True, separators=(",", ":"))


def loads(raw: str | bytes) -> Any:
    return json.loads(raw)
