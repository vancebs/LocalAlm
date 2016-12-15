from im.ImParam import ImParam
from im.Im import Im
from db.Database import Database
from Util import Util
import re
from cfg.ProjectConfig import ProjectConfig
from src.im.ImHandler import ImHandler


class LocalDbManager(object):
    _DELIM = '==***=='
    _EARLY_FROM_TIME = Util.format_time('2015-1-1 00:00:00')
    _FROM_TIME_SHIFT = 30 * 60  # 30 min
    _COMMIT_THRESHOLD_FOR_RAW = 200
    _REG_MATCH_FIELD_NAME = re.compile('([\s\S]+?):([\s\S]*)')
    _SYNC_FREQUENCY = 24 * 60 * 60 # 1 day

    _SQL_REPLACE_BUGS = (
        'REPLACE INTO '
            + Database.TABLE_BUGS + '('
                + Database.COL_BUGS_BUG_ID
                + ',' + Database.COL_BUGS_MODIFIED_TIME
                + ',' + Database.COL_BUGS_DIRTY
        + ') VALUES (?,?,?)'
    )

    _SQL_QUERY_BUGS_DIRTY = (
        'SELECT '
            + Database.COL_BUGS_BUG_ID
            + ',' + Database.COL_BUGS_MODIFIED_TIME
        + ' FROM '
            + Database.TABLE_BUGS
        + ' WHERE '
            + Database.COL_BUGS_DIRTY + '=1'
    )

    _SQL_UPDATE_BUGS_DIRTY = (
        'UPDATE '
        + Database.TABLE_BUGS
        + ' SET '
        + Database.COL_BUGS_DIRTY + '=?'
        + ' WHERE '
        + Database.COL_BUGS_BUG_ID + "=?"
    )

    _SQL_REPLACE_RAW = (
        'REPLACE INTO '
        + Database.TABLE_RAW + '('
        + Database.COL_RAW_BUG_ID
        + ',' + Database.COL_RAW_MODIFIED_TIME
        + ',' + Database.COL_RAW_DATA
        + ',' + Database.COL_RAW_DIRTY
        + ') VALUES (?,?,?,?)'
    )

    _SQL_CHECK_BUGS_DIRTY = (
        'UPDATE '
        + Database.TABLE_BUGS
        + ' SET '
        + Database.COL_BUGS_DIRTY + '=0'
        + ' WHERE '
        + Database.TABLE_BUGS + '.' + Database.COL_BUGS_BUG_ID + '=('
        + ' SELECT '
        + Database.COL_RAW_BUG_ID
        + ' FROM '
        + Database.TABLE_RAW
        + ' WHERE '
        + Database.TABLE_RAW + '.' + Database.COL_RAW_BUG_ID
        + '='
        + Database.TABLE_BUGS + '.' + Database.COL_BUGS_BUG_ID
        + ' AND '
        + Database.TABLE_RAW + '.' + Database.COL_RAW_MODIFIED_TIME
        + '='
        + Database.TABLE_BUGS + '.' + Database.COL_BUGS_MODIFIED_TIME
        + ')'
    )

    _SQL_QUERY_RAW_DIRTY = (
        'SELECT '
        + Database.COL_RAW_BUG_ID
        + ',' + Database.COL_RAW_DATA
        + " FROM "
        + Database.TABLE_RAW
        + ' WHERE '
        + Database.COL_RAW_DIRTY + '=1'
    )

    _SQL_REPLACE_DATA = (
        'REPLACE INTO ' + Database.TABLE_DATA + ' ('
        + Database.COL_DATA_BUG_ID
        + ',' + Database.COL_DATA_NAME
        + ',' + Database.COL_DATA_VALUE
        + ') VALUES (?,?,?)'
    )

    _SQL_INSERT_DATA = (
        'INSERT INTO ' + Database.TABLE_DATA + ' ('
        + Database.COL_DATA_BUG_ID
        + ',' + Database.COL_DATA_NAME
        + ',' + Database.COL_DATA_VALUE
        + ') VALUES (?,?,?)'
    )

    _SQL_UPDATE_DATA = (
        'UPDATE '
            + Database.TABLE_DATA
        + ' SET '
            + Database.COL_DATA_VALUE + '=?'
        + ' WHERE '
            + Database.COL_DATA_BUG_ID + '=?'
            + ' AND '
            + Database.COL_DATA_NAME + '=?'
    )

    _SQL_DELETE_DATA = (
        'DELETE FROM '
            + Database.TABLE_DATA
        + ' WHERE '
            + Database.COL_DATA_BUG_ID + '=?'
            + ' AND '
            + Database.COL_DATA_NAME + '=?'
    )

    _SQL_QUERY_DATA_WITH_ALM_ID = (
        'SELECT '
            + Database.COL_DATA_NAME
            + ',' + Database.COL_DATA_VALUE
        + ' FROM '
            + Database.TABLE_DATA
        + ' WHERE '
            + Database.COL_DATA_BUG_ID + '=?'
    )

    _SQL_UPDATE_RAW_DIRTY = (
        'UPDATE '
        + Database.TABLE_RAW
        + ' SET '
        + Database.COL_RAW_DIRTY + '=?'
        + ' WHERE '
        + Database.COL_RAW_BUG_ID + "=?"
    )

    _SQL_REPLACE_FIELDS = (
        'REPLACE INTO '
        + Database.TABLE_FIELDS + '('
        + Database.COL_FIELDS_NAME
        + ',' + Database.COL_FIELDS_DISPLAY_NAME
        + ',' + Database.COL_FIELDS_TYPE
        + ') VALUES (?,?,?)'
    )

    _SQL_QUERY_FIELDS = (
        'SELECT '
        + Database.COL_FIELDS_NAME
        + ',' + Database.COL_FIELDS_TYPE
        + ',' + Database.COL_FIELDS_DISPLAY_NAME
        + ' FROM '
        + Database.TABLE_FIELDS
    )

    _SQL_REPLACE_USERS = (
        'REPLACE INTO '
        + Database.TABLE_USERS + '('
        + Database.COL_USERS_NAME
        + ',' + Database.COL_USERS_EMAIL
        + ',' + Database.COL_USERS_FULLNAME
        + ',' + Database.COL_USERS_ASSIGNED_USER_NAME
        + ') VALUES (?,?,?,?)'
    )

    _SQL_QUERY_USERS = (
        'SELECT '
        + Database.COL_USERS_ASSIGNED_USER_NAME
        + ',' + Database.COL_USERS_EMAIL
        + ' FROM '
        + Database. TABLE_USERS
    )

    _mProject = None
    _mDictFieldDisplayName2Type = None
    _mDictFieldDisplayName2Name = None
    _mDictUsersAssignedUserName2Email = None

    def __init__(self, project):
        self._mProject = project

    def sync(self, total_fetch=False):
        self.sync_fields()
        (self._mDictFieldDisplayName2Type, self._mDictFieldDisplayName2Name) = self._get_fields_dict()
        self.sync_users()
        self._mDictUsersAssignedUserName2Email = self._get_users_dict()
        self.sync_bugs(total_fetch)
        self.sync_raw()
        self.sync_data()

    def sync_bugs(self, total_fetch=False):
        print ('sync bugs ...')

        # save query time
        query_time = Util.current_time()

        # get sync from time
        sync_from_time = None
        if total_fetch:
            sync_from_time = LocalDbManager._EARLY_FROM_TIME
        else:
            with self._open_database() as db:
                sync_from_time = ProjectConfig.get_bugs_last_update_time(db, LocalDbManager._EARLY_FROM_TIME)

        print ('fetch bug from last modified time [%s]' % Util.format_time_to_str(sync_from_time))

        with self._open_database() as db:
            # query from im
            (result, count) = ImHandler.sync_bugs(
                self._mProject, sync_from_time,
                lambda bug_id, modified_time: db.execute(
                    self._SQL_REPLACE_BUGS,
                    (bug_id, Util.format_time_to_long(modified_time), 1)))

            # check result
            if result:
                print ('[%d] bugs updated.' % count)
                last_modified_time = Util.time_sub(query_time, LocalDbManager._FROM_TIME_SHIFT)
                ProjectConfig.set_bugs_last_update_time(db, last_modified_time)
            else:
                print ('fetch bugs failed')

        print ('done')
        return result

    def sync_raw(self):
        print ('sync raw ...')

        with self._open_database() as db:
            # check dirty bugs in table [bugs]. And set not dirty if it is not really dirty
            db.execute(self._SQL_CHECK_BUGS_DIRTY)

            # query dirty bugs
            c = db.cursor()
            c.execute(self._SQL_QUERY_BUGS_DIRTY)

            # fetch detail for each dirty bugs
            count = 0
            row = c.fetchone()
            while row:
                count += 1
                alm_id = row[0]
                modified_time = row[1]
                print('fetching bug# [%d] id: %s, modified: %s' % (count, alm_id, modified_time))

                # fetch issue detail
                if not self.fetch_raw(alm_id, db, modified_time):
                    db.commit()
                    return False

                # commit to free memory
                if count % LocalDbManager._COMMIT_THRESHOLD_FOR_RAW == 0:
                    db.commit()

                # next row
                row = c.fetchone()

            print ('[%d] raw bug info fetched' % count)

            # close db
            c.close()
            db.commit()

        print ('done')
        return True

    def sync_data(self):
        print ('sync data ...')

        with self._open_database() as db:
            c = db.cursor()
            c.execute(self._SQL_QUERY_RAW_DIRTY)

            count = 0
            l_name = None
            l_value = []
            row = c.fetchone()
            while row:
                count += 1
                bug_id = row[0]
                data = row[1]

                # get new & old data
                new_data = self._parse_raw_data(data)
                old_data = LocalDbManager._read_old_data(bug_id, db)

                # compare new & old data. find out fields should be inserted, updated, deleted
                to_insert = []
                to_update = []
                to_delete = old_data.keys()
                for key in new_data.keys():
                    if old_data.has_key(key):
                        to_update.append(key)
                    else:
                        to_insert.append(key)
                    try:
                        to_delete.remove(key)
                    except ValueError,e:
                        # key not found in to_delete. it's OK
                        pass

                print('parsing from raw# [%d] ID: %s, insert: %d, update: %d, delete: %d' %
                      (count, bug_id, len(to_insert), len(to_update), len(to_delete)))

                # update db
                for name in to_insert:
                    db.execute(self._SQL_INSERT_DATA, (bug_id, name, new_data[name]))
                for name in to_update:
                    db.execute(self._SQL_UPDATE_DATA, (new_data[name], bug_id, name))
                for name in to_delete:
                    db.execute(self._SQL_DELETE_DATA, (bug_id, name))

                # mark not dirty
                db.execute(self._SQL_UPDATE_RAW_DIRTY, (0, bug_id))

                # commit to free memory
                if count % LocalDbManager._COMMIT_THRESHOLD_FOR_RAW == 0:
                    db.commit()

                row = c.fetchone()

            print('[%d] parser from raw finished.' % count)

            # close cursor & db
            c.close()
            db.commit()

        print ('done')

    def _parse_raw_data(self, raw):
        # check parameter raw
        if isinstance(raw, buffer):
            raw = str(raw)
        elif isinstance(raw, str):
            # unnecessary to convert
            pass
        else:
            raise TypeError('Invalid type of parameter raw')

        # parser lines
        data = dict()
        l_name = None
        l_value = []
        lines = raw.splitlines(False)
        for line in lines:
            line = line.strip()
            if len(line) <= 0:
                # ignore empty lines
                continue

            # try get field name
            (name, value) = self._parse_line_field(line)
            if name is None:
                l_value.append(line)
            else:
                # we get a new field name. save last one first
                if l_name is not None and len(l_value) > 0:
                    # save into data dict if value is not empty
                    data[l_name] = '\n'.join(l_value)

                # save name to l_name & reset l_value
                l_name = name
                l_value = []

                # save value into l_value if exists
                if value is not None:
                    l_value.append(value)

        if l_name is not None and len(l_value) > 0:
            data[l_name] = '\n'.join(l_value)

        return data

    @staticmethod
    def _read_old_data(alm_id, db):
        data = dict()

        # query from db
        c = db.cursor()
        c.execute(LocalDbManager._SQL_QUERY_DATA_WITH_ALM_ID, (alm_id,))
        row = c.fetchone()
        while row:
            data[row[0]] = row[1]
            row = c.fetchone()

        # close cursor
        c.close()

        return data

    def _insert_data_field(self, db, bug_id, name, value):
        if len(value) <= 0:
            # skip fields without value
            return

        # print ('name: %s, value: %s' % (name, '\n'.join(value)))
        # insert field
        db.execute(self._SQL_REPLACE_DATA, (bug_id, name, '\n'.join(value)))

    def _parse_line_field(self, line):
        r = LocalDbManager._REG_MATCH_FIELD_NAME.match(line)
        if r is None:
            return None, None
        else:
            groups = r.groups()
            if len(groups) <= 0:
                return None, None
            else:
                field_name = groups[0].strip()
                if self._mDictFieldDisplayName2Type.has_key(field_name):
                    if len(groups) == 1:
                        return field_name, None
                    else:
                        field_value = groups[1].strip()
                        if len(field_value) <= 0:
                            field_value = None
                        return field_name, field_value
                else:
                    return None, None

    def fetch_raw(self, alm_id, db, modified_time=0):
        # fetch bug detail from im
        (code, out, err) = Im.execute('im viewissue --showRichContent %s' % alm_id)

        # insert bug detail into db
        if code == 0:  # im command success
            # mark bug not dirty
            db.execute(self._SQL_UPDATE_BUGS_DIRTY, (0, alm_id))

            # insert or update bug detail
            db.execute(self._SQL_REPLACE_RAW, (alm_id, modified_time, buffer(Util.str_to_utf8(out)), 1))
        else:
            print('failed to fetch bug %s' % alm_id)
            return False

        return True

    def sync_fields(self, force_update=False):
        print ('sync fields ...')
        current_time = None

        # check force update
        if not force_update:
            # check frequency
            current_time = Util.current_time()
            with self._open_database() as db:
                last_updated_time = ProjectConfig.get_fields_last_update_time(db, LocalDbManager._EARLY_FROM_TIME)
                delta_time = Util.time_sub(current_time, last_updated_time)
                if Util.format_time_to_long(delta_time) < LocalDbManager._SYNC_FREQUENCY:
                    # unnecessary to sync if duration is less than frequency
                    print ('canceled. unnecessary to sync.')
                    return

        # sync
        with self._open_database() as db:
            (result, count) = ImHandler.sync_fields(
                lambda name, display_name, field_type: db.execute(
                    self._SQL_REPLACE_FIELDS,
                    (name, display_name, field_type)))

            # check result
            if result:
                print ('[%d] fields updated.' % count)

                # update last sync time
                ProjectConfig.set_fields_last_update_time(db, current_time)
            else:
                print ('fetch fields failed')

        print ('done')
        return result

    def sync_users(self, force_update=False):
        print ('sync users ...')
        current_time = None

        # check force update
        if not force_update:
            # check frequency
            current_time = Util.current_time()
            with self._open_database() as db:
                last_updated_time = ProjectConfig.get_users_last_update_time(db, LocalDbManager._EARLY_FROM_TIME)
                delta_time = Util.time_sub(current_time, last_updated_time)
                if Util.format_time_to_long(delta_time) < LocalDbManager._SYNC_FREQUENCY:
                    # unnecessary to sync if duration is less than frequency
                    print ('canceled. unnecessary to sync.')
                    return

        # sync
        with self._open_database() as db:
            (result, count) = ImHandler.sync_users(
                lambda name, email, fullname, assigned_user_name: db.execute(
                    self._SQL_REPLACE_USERS,
                    (name, email, fullname, assigned_user_name)))

            # check result
            if result:
                print ('[%d] users updated.' % count)

                # update last sync time
                ProjectConfig.set_users_last_update_time(db, current_time)
            else:
                print ('fetch users failed')

        print ('done')
        return result

    def _open_database(self):
        return Database.open_project_database(self._mProject)

    def _get_fields_dict(self):
        with self._open_database() as db:
            c = db.cursor()
            c.execute(LocalDbManager._SQL_QUERY_FIELDS)
            row = c.fetchone()
            name_type = dict()
            name_display_name = dict()
            while row:
                r_name = row[0]
                r_type = row[1]
                r_display_name = row[2]
                name_type[r_display_name] = r_type
                name_display_name[r_display_name] = r_name
                row = c.fetchone()

            c.close()

        return name_type, name_display_name

    def _get_users_dict(self):
        with self._open_database() as db:
            c = db.cursor()
            c.execute(LocalDbManager._SQL_QUERY_USERS)
            row = c.fetchone()
            assigned_email = dict()
            while row:
                assigned = row[0]
                email = row[1]
                assigned_email[assigned] = email
                row = c.fetchone()

            c.close()

        return assigned_email

