from logging import Filter


class MoshiFilter(Filter):
    level = 20

    @classmethod
    def set_level(cls, lvl):
        cls.level = lvl

    def filter(self, record):
        req = record.args['request']
        res = record.args['response']
        level = record.levelno
        desired = None
        if req['hostname'].endswith(".moshi"):
            desired = req
        elif res['hostname'].endswith(".moshi"):
            desired = res
        else:
            level = 10

        #if desired is not None and 'path' in desired:
        #    if not desired['path'].startswith('/services/rest/'):
        #        level = 10

        from logging import getLevelName
        record.levelno = level
        record.levelname = getLevelName(level)
        return level >= self.level
