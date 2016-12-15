import sqlite3
import os
import re


class Database(object):
    _VERSION = 1
    _DB_DIR = 'database'

    TABLE_BUGS = 'bugs'
    TABLE_RAW = 'raw'
    TABLE_DATA = 'data'
    TABLE_FIELDS = 'fields'
    TABLE_USERS = 'users'
    TABLE_CONFIG = 'config'

    INDEX_DATA_ID_NAME = 'data_id_name_index'
    INDEX_FIELDS_NAME = 'fields_name_index'
    INDEX_USERS_NAME = 'users_name_index'
    INDEX_CONFIG_NAME = 'config_name_index'

    COL_BUGS_BUG_ID = 'bug_id'
    COL_BUGS_MODIFIED_TIME = 'modified_time'
    COL_BUGS_DIRTY = 'dirty'

    COL_RAW_BUG_ID = 'bug_id'
    COL_RAW_MODIFIED_TIME = 'modified_time'
    COL_RAW_DATA = 'data'
    COL_RAW_DIRTY = 'dirty'

    COL_DATA_ID = 'id'
    COL_DATA_BUG_ID = 'bug_id'
    COL_DATA_NAME = 'name'
    COL_DATA_VALUE = 'value'

    COL_FIELDS_ID = 'id'
    COL_FIELDS_NAME = 'name'
    COL_FIELDS_DISPLAY_NAME = 'display_name'
    COL_FIELDS_TYPE = 'type'

    COL_USERS_ID = 'id'
    COL_USERS_NAME = 'name'
    COL_USERS_FULLNAME = 'fullname'
    COL_USERS_EMAIL = 'email'
    COL_USERS_ASSIGNED_USER_NAME = 'assigned_user_name'

    COL_CONFIG_ID = 'id'
    COL_CONFIG_NAME = 'name'
    COL_CONFIG_VALUE = 'value'

    @staticmethod
    def _get_project_db_path(project_name):
        return '%s/%s.db' % (Database._DB_DIR, project_name)

    @staticmethod
    def remove_project_database( project):
        db_path = Database._get_project_db_path(project)
        if os.path.exists(db_path):
            os.remove(db_path)

    @staticmethod
    def open_project_database(project):
        # get db path & dir
        db_path = Database._get_project_db_path(project)
        path_dir = re.compile(r'([\s\S]*)[/\\]').search(db_path).group(1)

        # make dirs if not exists
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)

        # open db
        new_db = not os.path.exists(db_path)
        con = sqlite3.connect(db_path)
        con.text_factory = str
        if new_db:
            # init db for created
            Database._on_init_project_db(con, project)
            ver = 0  # version 0 for new db
        else:
            # get version from db
            ver = Database._get_project_db_version(con, project)

        # check for update
        if ver < Database._VERSION:
            Database._on_upgrade_project_db(ver, con)

        return con

    @staticmethod
    def _on_init_project_db(con, project):
        con.execute('CREATE TABLE version (ver INTEGER)')
        con.execute('INSERT INTO version (ver) VALUES (0)')
        con.commit()

    @staticmethod
    def _get_project_db_version(con, project):
        cursor = con.cursor()
        cursor.execute('SELECT ver from version')
        row = cursor.fetchone()
        return row[0]  # return db version

    @staticmethod
    def _on_upgrade_project_db(version, con):
        # 0 => 1
        if version == 0:
            # init database
            con.execute('CREATE TABLE ' + Database.TABLE_BUGS + ' ('
                            + Database.COL_BUGS_BUG_ID + ' TEXT PRIMARY KEY,'
                            + Database.COL_BUGS_MODIFIED_TIME + ' INTEGER,'
                            + Database.COL_BUGS_DIRTY + ' INTEGER'
                        + ')')
            con.execute('CREATE TABLE ' + Database.TABLE_RAW + ' ('
                            + Database.COL_RAW_BUG_ID + ' TEXT PRIMARY KEY,'
                            + Database.COL_RAW_MODIFIED_TIME + ' INTEGER,'
                            + Database.COL_RAW_DATA + ' BLOB,'
                            + Database.COL_RAW_DIRTY + ' INTEGER'
                        + ')')
            con.execute('CREATE TABLE ' + Database.TABLE_DATA + ' ('
                            + Database.COL_DATA_ID + ' INTEGER PRIMARY KEY AUTOINCREMENT,'
                            + Database.COL_DATA_BUG_ID + ' TEXT,'
                            + Database.COL_DATA_NAME + ' TEXT,'
                            + Database.COL_DATA_VALUE + ' TEXT'
                        + ')')
            con.execute('CREATE UNIQUE INDEX ' + Database.INDEX_DATA_ID_NAME + ' ON '
                            + Database.TABLE_DATA + '('
                                + Database.COL_DATA_BUG_ID
                                + ',' + Database.COL_DATA_NAME
                            + ')')
            con.execute('CREATE TABLE ' + Database.TABLE_FIELDS + ' ('
                            + Database.COL_FIELDS_ID + ' INTEGER PRIMARY KEY AUTOINCREMENT,'
                            + Database.COL_FIELDS_NAME + ' TEXT,'
                            + Database.COL_FIELDS_DISPLAY_NAME + ' TEXT,'
                            + Database.COL_FIELDS_TYPE + ' TEXT'
                        + ')')
            con.execute('CREATE UNIQUE INDEX ' + Database.INDEX_FIELDS_NAME + ' ON '
                            + Database.TABLE_FIELDS + '('
                                +Database.COL_FIELDS_NAME
                            + ')')
            con.execute('CREATE TABLE ' + Database.TABLE_USERS + ' ('
                            + Database.COL_USERS_ID + ' INTEGER PRIMARY KEY AUTOINCREMENT,'
                            + Database.COL_USERS_NAME + ' TEXT,'
                            + Database.COL_USERS_EMAIL + ' TEXT,'
                            + Database.COL_USERS_FULLNAME + ' TEXT,'
                            + Database.COL_USERS_ASSIGNED_USER_NAME + ' TEXT'
                        + ')')
            con.execute('CREATE UNIQUE INDEX ' + Database.INDEX_USERS_NAME + ' ON '
                            + Database.TABLE_USERS + '('
                                +Database.COL_USERS_NAME
                            + ')')
            con.execute('CREATE TABLE ' + Database.TABLE_CONFIG + ' ('
                            + Database.COL_CONFIG_ID + ' INTEGER PRIMARY KEY AUTOINCREMENT,'
                            + Database.COL_CONFIG_NAME + ' TEXT,'
                            + Database.COL_CONFIG_VALUE + ' TEXT'
                        + ')')
            con.execute('CREATE UNIQUE INDEX ' + Database.INDEX_CONFIG_NAME + ' ON '
                            + Database.TABLE_CONFIG + '('
                                + Database.COL_CONFIG_NAME
                            + ')')
            con.commit()
            version += 1

        # update version
        con.execute('UPDATE version set ver=%d' % version)
        con.commit()
