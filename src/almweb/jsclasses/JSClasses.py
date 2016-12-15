import PyV8


class Window(PyV8.JSClass):
    _mUrl = None

    def open(self, url, p1, p2, p3):
        self._mUrl = url

    def getUrl(self):
        return self._mUrl

class Global(PyV8.JSClass):
    def __init__(self):
        self.window = Window()

    def getWindow(self):
        return self.window