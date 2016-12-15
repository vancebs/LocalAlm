import time


class Util(object):
    _DATETIME_FORMAT_CHINESE = '%Y-%m-%d %H:%M:%S'
    _DATETIME_FORMAT_ENGLISH = '%b %d, %Y %I:%M:%S %p'
    _DATETIME_FORMAT_TARGET = _DATETIME_FORMAT_ENGLISH
    _DATETIME_FORMATS = (_DATETIME_FORMAT_CHINESE, _DATETIME_FORMAT_ENGLISH)
    _CODEC_CHECK_LIST = (
        'GBK',
        'ascii',
        'ISO-8859-2',
        'windows-1252',
        'GB2312'
    )

    @staticmethod
    def format_time(time_src):
        time_formatted = None
        if isinstance(time_src, str):
            for f in Util._DATETIME_FORMATS:
                try:
                    time_formatted = time.strptime(time_src, f)
                    break
                except ValueError, e:
                    pass

            if time_formatted is None:
                print('unknown format: ' + time_src)
                raise ValueError('unknown format: ' + time_src)
        elif isinstance(time_src, time.struct_time):
            time_formatted = time_src
        elif isinstance(time_src, long):
            time_formatted = time.localtime(time_src)
        elif isinstance(time_src, int):  # treat int as long
            time_formatted = time.localtime(time_src)

        # return time
        return time_formatted

    @staticmethod
    def format_time_to_str(time_src):
        return time.strftime(Util._DATETIME_FORMAT_TARGET, Util.format_time(time_src))

    @staticmethod
    def format_time_to_long(time_src):
        return long(time.mktime(Util.format_time(time_src)))

    @staticmethod
    def str_to_utf8(str_src):
        # try decode with known types
        for codec in Util._CODEC_CHECK_LIST:
            # print('try codec: %s' % codec)
            try:
                return str_src.decode(codec).encode('utf-8')
            except UnicodeDecodeError, e:
                pass
        raise UnicodeDecodeError('cannot detect codec')

    @staticmethod
    def current_time():
        return time.localtime()

    @staticmethod
    def time_add(time_src, add):
        t = Util.format_time_to_long(time_src)
        a = Util.format_time_to_long(add)
        return Util.format_time(t + a)

    @staticmethod
    def time_sub(time_src, sub):
        t = Util.format_time_to_long(time_src)
        s = Util.format_time_to_long(sub)
        return Util.format_time(t - s)