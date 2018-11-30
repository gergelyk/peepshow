from peepshow.pager.pager import Pager

class TooManyInitialIterations(StopIteration): pass

class PagedCache:

    def __init__(self, content, str_func=str):
        self.iterator = content.__iter__()
        self.index = 0
        self.offset = 0
        self.cache = []
        self.str_func = str_func

    def iterate(self, times):
        for i in range(times):
            next(self.iterator)
            self.offset += 1
            self.index += 1

    def __iter__(self):
        while True:
            try:
                obj = next(self.iterator)
            except StopIteration:
                break
            line = self.str_func(obj)
            self.cache.append(obj)
            yield f'[{self.index:>5}] {line}'
            self.index += 1

    def clear_cache(self):
        self.offset += len(self.cache)
        self.cache[:] = []

    def __getitem__(self, index):
        cache_index =  index - self.offset
        if not cache_index >= 0 or not cache_index < len(self.cache):
            raise IndexError("You can use only indices visible on the screen.")

        return self.cache[cache_index]

    def recall_cache(self):
        def content_gen():
            for index, entry in enumerate(self.cache):
                key, obj = entry
                line = self.str_func(entry)
                index_ = index + self.offset
                yield f'[{index_:>5}] {line}'
        p = Pager(numeric=True)
        p.page(content_gen())

def page(content, str_func=str, offset=0):
    cache = PagedCache(content, str_func)
    try:
        cache.iterate(offset)
    except StopIteration as ex:
        raise TooManyInitialIterations(f'Only {cache.index} iterations possible.') from ex
    pager = Pager( (PagedCache.clear_cache, cache), numeric=True )
    pager.page(cache)
    return cache
