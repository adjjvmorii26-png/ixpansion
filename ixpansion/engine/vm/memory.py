class Memory:
    def __init__(self) -> None:
        self.cells: dict[str, object] = {}

    def write(self, key: str, value: object) -> None:
        self.cells[key] = value

    def read(self, key: str) -> object:
        return self.cells[key]
