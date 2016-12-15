from src.im.Im import Im
from src.im.ImParam import ImParam
from src.Util import Util


class ImHandler(object):
    _DELIM = '==***=='

    _COL_USER_NAME = 0
    _COL_USER_EMAIL = 1
    _COL_USER_FULLNAME = 2

    _COL_FIELD_NAME = 0
    _COL_FIELD_DISPLAY_NAME = 1
    _COL_FIELD_TYPE = 2

    _COL_BUG_ID = 0
    _COL_BUG_MODIFIED_TIME = 1

    @staticmethod
    def query(im_cmd, on_line, param=None):
        count = 0
        (code, out, err) = Im.execute(im_cmd)
        if code == 0:
            # insert lines
            lines = Util.str_to_utf8(out).split("\n")
            for line in lines:
                count += 1
                line = line.strip()
                if len(line) <= 0:
                    continue

                # on line callback
                on_line(line, param)

                # print ('%d item queried' % count)
        else:
            print ('fetch users failed')
            return False, count

        return True, count

    @staticmethod
    def sync_users(on_user_fetched):
        # im command
        cmd = 'im users --fields=name,email,fullname --fieldsDelim="' + ImHandler._DELIM + '"'

        # query from im
        return ImHandler.query(cmd, ImHandler._on_sync_user_get_line, on_user_fetched)

    @staticmethod
    def _on_sync_user_get_line(line, cb):
        parts = line.split(ImHandler._DELIM)
        name = parts[ImHandler._COL_USER_NAME]
        fullname = parts[ImHandler._COL_USER_FULLNAME]
        cb(
            name,
            parts[ImHandler._COL_USER_EMAIL],
            fullname,
            '%s (%s)' % (fullname, name))  # generate assigned user name

    @staticmethod
    def sync_fields(on_field_fetched):
        # im command
        cmd = 'im fields --fields name,displayName,type --fieldsDelim="' + ImHandler._DELIM + '"'

        # query from im
        return ImHandler.query(cmd, ImHandler._on_sync_user_get_line, on_field_fetched)

    @staticmethod
    def _on_sync_field_get_line(line, cb):
        parts = line.split(ImHandler._DELIM)
        cb(
            parts[ImHandler._COL_FIELD_NAME],
            parts[ImHandler._COL_FIELD_DISPLAY_NAME],
            parts[ImHandler._COL_FIELD_TYPE])

    @staticmethod
    def sync_bugs(project, sync_from_time, on_bug_fetched):
        # generate parameters
        params = ImParam.multi(
            ImParam.fields('ID', 'Modified Date'),
            ImParam.sort_by_field('ID', False),
            ImParam.field_delim(ImHandler._DELIM),
            ImParam.define(
                ImParam.define_and(
                    ImParam.define_not(ImParam.define_versioned()),
                    ImParam.define_field('Project', project),
                    ImParam.define_field('Type', 'Defect', 'Stability Defect', 'General FR'),  # TODO config later
                    ImParam.define_field_time_from('Modified Date', Util.format_time_to_str(sync_from_time))
                )
            )
        )

        # im command
        cmd = 'im issues %s' % params

        # query from im
        return ImHandler.query(cmd, ImHandler._on_sync_bug_get_line, on_bug_fetched)

    @staticmethod
    def _on_sync_bug_get_line(line, cb):
        parts = line.split(ImHandler._DELIM)
        cb(parts[ImHandler._COL_BUG_ID], parts[ImHandler._COL_BUG_MODIFIED_TIME])

