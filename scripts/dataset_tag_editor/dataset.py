class Data:
    def __init__(self, imgpath: str, caption: str):
        self.imgpath = imgpath
        self.tags = [t.strip() for t in caption.split(",")]
        self.tagset = set(self.tags)

    def tag_contains_allof(self, tags: set[str]):
        return self.tagset.issuperset(tags)

    def tag_contains_anyof(self, tags: set[str]):
        return not self.tagset.isdisjoint(tags)


class Dataset:
    def __init__(self):
        self.datas: dict[str, Data] = dict()
        # [PERF] cache of the union of all tags; invalidated on mutation
        self._tagset_cache: set[str] | None = None

    def __len__(self):
        return len(self.datas)

    def _invalidate(self):
        self._tagset_cache = None

    def clear(self):
        self.datas.clear()
        self._invalidate()

    def merge(self, dataset, overwrite: bool = True):
        if type(dataset) is Dataset:
            for path in dataset.datas.keys():
                if overwrite or path not in self.datas.keys():
                    self.datas[path] = dataset[path]
            self._invalidate()
        return self

    def append_data(self, data: Data):
        self.datas[data.imgpath] = data
        self._invalidate()

    def remove(self, dataset):
        if type(dataset) is Dataset:
            for path in dataset.datas.keys():
                if path in self.datas.keys():
                    del self.datas[path]
            self._invalidate()
        return self

    def remove_by_path(self, path: str):
        if path in self.datas.keys():
            del self.datas[path]
            self._invalidate()

    def copy(self):
        res = Dataset()
        res.datas = self.datas.copy()
        # do not share the mutable tagset cache with the original
        res._tagset_cache = None
        return res

    def filter(self, filter):
        return filter.apply(self)

    def get_data(self, path: str):
        return self.datas.get(path)

    def get_data_tags(self, path: str):
        data = self.get_data(path)
        if data:
            return data.tags
        else:
            return []

    def get_data_tagset(self, path: str):
        data = self.get_data(path)
        if data:
            return data.tagset
        else:
            return {}

    def get_tagset(self):
        # [PERF] return a cached union (as a fresh copy, callers may mutate it)
        if self._tagset_cache is None:
            tags = set()
            for data in self.datas.values():
                tags |= data.tagset
            self._tagset_cache = tags
        return set(self._tagset_cache)

    def get_taglist(self):
        return [t for t in self.get_tagset()]
