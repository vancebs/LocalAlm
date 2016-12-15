from HttpHelper import HttpHelper
from jsclasses.JSClasses import Global
import PyV8
import re


class AlmClient(object):
    _AUTH_USERNAME = "fan.hu"
    _AUTH_PASSWORD = "93059hf"
    _LOGIN_URL = "https://alm.tclcom.com:7003/im"
    _ROOT_URL = "https://alm.tclcom.com:7003"
    _mUrl = None
    _mHttp = HttpHelper()
    _mCommandRunnerId = None
    _mSessionId = None
    _mUserID = None
    _mTimeZoneLabel = None

    def login(self):
        self._mHttp.add_password(None, self._LOGIN_URL, self._AUTH_USERNAME, self._AUTH_PASSWORD)
        content = self._mHttp.get("https://alm.tclcom.com:7003/im")

        # find javascript code
        script = re.compile("(<script [\s\S]*?>)([\s\S]*)(</script>)").search(content).group(2)

        # run javascript
        js_global = Global()
        with PyV8.JSContext(js_global) as js:
            js.eval(script)
            js.locals.doTimeZone()

        # get url
        self._mUrl = self._ROOT_URL + js_global.window.getUrl()
        print(self._mUrl)

    def open_session(self):
        content = self._mHttp.get(self._mUrl)

        self._mCommandRunnerId = re.compile('(window.commandRunnerID\s*?=\s*?)(\d*?)(;)').search(content).group(2)
        self._mSessionId = re.compile('(window.sessionID\s*?=\s*?")([0-9A-Fa-f]*?)(")').search(content).group(2)
        self._mUserID = re.compile('(window.userID\s*?=\s*?")([\s\S]*?)(")').search(content).group(2)
        self._mTimeZoneLabel = re.compile('(window.timeZoneLabel\s*?=\s*?")(\w*?)(")').search(content).group(2)

        print(self._mCommandRunnerId)
        print(self._mSessionId)
        print(self._mUserID)
        print(self._mTimeZoneLabel)

        with open("res.html", mode='wb') as f:
            f.write(content)

    def get_jsonrpc_script(self):
        content = self._mHttp.get(self._ROOT_URL + "/scripts/json/jsonrpc.js")
        with open("jsonrpc.js", mode='wb') as f:
            f.write(content)

    def get_mks_script(self):
        content = self._mHttp.get(self._ROOT_URL + "/scripts/qooxdoo/script/mks_webkit.js")
        with open("mks.js", mode='wb') as f:
            f.write(content)
