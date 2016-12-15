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

    @staticmethod
    def get_config(db, key, default):
        result = default

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

    @staticmethod
    def set_config(db, key, value):
        db.execute('REPLACE INTO '
                    + Database.TABLE_CONFIG + ' ('
                    + Database.COL_CONFIG_NAME
                    + ',' + Database.COL_CONFIG_VALUE
                    + ') VALUES (?,?)', (key, value))
        db.commit()

    @staticmethod
    def get_bugs_last_update_time(db, default):
        return Util.format_time(ProjectConfig.get_config(db, ProjectConfig.CFG_KEY_BUG_LAST_UPDATE_TIME, default))

    @staticmethod
    def set_bugs_last_update_time(db, value):
        ProjectConfig.set_config(db, ProjectConfig.CFG_KEY_BUG_LAST_UPDATE_TIME, Util.format_time_to_str(value))

    @staticmethod
    def get_fields_last_update_time(db, default):
        return Util.format_time(ProjectConfig.get_config(db, ProjectConfig.CFG_KEY_FIELDS_LAST_UPDATE_TIME, default))

    @staticmethod
    def set_fields_last_update_time(db, value):
        ProjectConfig.set_config(db, ProjectConfig.CFG_KEY_FIELDS_LAST_UPDATE_TIME, Util.format_time_to_str(value))

    @staticmethod
    def get_users_last_update_time(db, default):
        return Util.format_time(ProjectConfig.get_config(db, ProjectConfig.CFG_KEY_USERS_LAST_UPDATE_TIME, default))

    @staticmethod
    def set_users_last_update_time(db, value):
        ProjectConfig.set_config(db, ProjectConfig.CFG_KEY_USERS_LAST_UPDATE_TIME, Util.format_time_to_str(value))
