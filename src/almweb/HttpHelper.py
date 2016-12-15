import urllib2


class HttpHelper(object):
    _mPasswordMgr = None
    _mHeaders = {}
    _USER_AGENT = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'

    def add_password(self, realm, uri, username, password):
        if self._mPasswordMgr is None:
            self._mPasswordMgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        self._mPasswordMgr.add_password(realm, uri, username, password)

    def get(self, url):
        return self.post(url, None)

    def post(self, url, data):
        auth_handler = urllib2.HTTPBasicAuthHandler(self._mPasswordMgr)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)

        req = urllib2.Request(url, data, self._mHeaders)

        return urllib2.urlopen(req).read()
