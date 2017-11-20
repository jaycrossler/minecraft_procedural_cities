class Map(dict):
    """
    From: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    Mods (Extend and Copy) by Jay

    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        v = Map(v)
                    if isinstance(v, list):
                        self.__convert(v)
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    v = Map(v)
                elif isinstance(v, list):
                    self.__convert(v)
                self[k] = v

    def __convert(self, v):
        for elem in xrange(0, len(v)):
            if isinstance(v[elem], dict):
                v[elem] = Map(v[elem])
            elif isinstance(v[elem], list):
                self.__convert(v[elem])

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]

    def extend (self, **new_keys):
        for key in new_keys:
            self[key] = new_keys[key]
        return self

    def copy (self, **new_keys):
        item = Map({})
        for key in self:
            item[key] = self[key]
        for key in new_keys:
            item[key] = new_keys[key]
        return item
