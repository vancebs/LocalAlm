import time

from src.Util import Util


class ImParam(object):


    @staticmethod
    def multi(*params):
        return ' '.join(params)

    @staticmethod
    def sort_by_field(field, desc = False):
        if desc:
            return '--sortField="%s" %s' % (field, '--nosortAscending')
        else:
            return '--sortField="%s" %s' % (field, '--sortAscending')

    @staticmethod
    def field_delim(delim):
        return '--fieldsDelim="%s"' % delim

    @staticmethod
    def fields(*fields):
        s = '","'.join(fields)
        return '--fields="%s"' % s

    @staticmethod
    def define(define):
        return '--queryDefinition="%s"' % define

    @staticmethod
    def define_not(condition):
        return '(not "%s")' % condition

    @staticmethod
    def define_and(*conditions):
        cond = ' and '.join(conditions)
        return '(%s)' % cond

    @staticmethod
    def define_or(*conditions):
        cond = ' or '.join(conditions)
        return '(%s)' % cond

    @staticmethod
    def define_versioned():
        return 'item.versioned'

    @staticmethod
    def define_field(name, *values):
        v = ','.join(values)
        return '(field[%s]=%s)' % (name, v)

    @staticmethod
    def define_field_time_between(name, from_time, to_time):
        return '(field[%s] between time %s and %s)' % (name, Util.format_time_to_str(from_time), Util.format_time_to_str(to_time))

    @staticmethod
    def define_field_time_from(name, from_time):
        return ImParam.define_field_time_between(name, from_time, time.localtime())