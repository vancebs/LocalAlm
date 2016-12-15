from src.Util import Util

from src.db.Database import Database


class ProjectConfig(object):
    CFG_KEY_BUG_LAST_UPDATE_TIME = 'bug_last_update_time'
    CFG_KEY_FIELDS_LAST_UPDATE_TIME = 'fields_last_update_time'
    CFG_KEY_USERS_LAST_UPDATE_TIME = 'users_last_update_time'

    _mProject = None

    def __init__(self, project):
        self._mProject = project

    def _open_database(self):
        return Database.open_project_database(self._mProject)

    def get_config(self, key, default):
        result = default

        with self._open_database() as db:
            # read from db
            c = db.cursor()
            c.execute('SELECT '
                        + Database.COL_CONFIG_VALUE
                      + ' FROM '
                        + Database.TABLE_CONFIG
                      + ' WHERE ' + Database.COL_CONFIG_NAME + '=?', (key,))
            rows = c.fetchall()
            if len(rows) > 0:
                result = rows[0][0]

            # close cursor
            c.close()

        return result

    def set_config(self, key, value):
        with self._open_database() as db:
            db.execute('REPLACE INTO '
                        + Database.TABLE_CONFIG + ' ('
                        + Database.COL_CONFIG_NAME
                        + ',' + Database.COL_CONFIG_VALUE
                        + ') VALUES (?,?)', (key, value))
            db.commit()

    def get_bugs_last_update_time(self, default):
        return Util.format_time(self.get_config(ProjectConfig.CFG_KEY_BUG_LAST_UPDATE_TIME, default))

    def set_bugs_last_update_time(self, value):
        self.set_config(ProjectConfig.CFG_KEY_BUG_LAST_UPDATE_TIME, Util.format_time_to_str(value))

    def get_fields_last_update_time(self, default):
        return Util.format_time(self.get_config(ProjectConfig.CFG_KEY_FIELDS_LAST_UPDATE_TIME, default))

    def set_fields_last_update_time(self, value):
        self.set_config(ProjectConfig.CFG_KEY_FIELDS_LAST_UPDATE_TIME, Util.format_time_to_str(value))

    def get_users_last_update_time(self, default):
        return Util.format_time(self.get_config(ProjectConfig.CFG_KEY_USERS_LAST_UPDATE_TIME, default))

    def set_users_last_update_time(self, value):
        self.set_config(ProjectConfig.CFG_KEY_USERS_LAST_UPDATE_TIME, Util.format_time_to_str(value))

