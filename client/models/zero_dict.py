class ZeroDict(dict):
    def __getitem__(self, key):
        return super().__getitem__(key) if key in self else 0