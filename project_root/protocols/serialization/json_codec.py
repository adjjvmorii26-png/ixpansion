import json
from datetime import date, datetime
from typing import Any


class NexusJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, set):
            return list(o)
        return super().default(o)


def dumps(data: Any) -> str:
    return json.dumps(data, cls=NexusJSONEncoder, sort_keys=True)


def loads(raw: str | bytes) -> Any:
    return json.loads(raw)
