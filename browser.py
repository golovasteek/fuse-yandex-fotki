#!/usr/bin/python

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

class RegistrarBrowser(QWebView):
    def __init__ (self, clientId):
        self.token = ''
        QWebView.__init__(self)
        self.connect(self, SIGNAL('urlChanged(const QUrl&)'), self.urlChanged)
        self.connect(self, SIGNAL('linkClicked(const QUrl&)'), self.urlChanged)
        self.load(QUrl("https://oauth.yandex.ru/authorize?response_type=token&display=popup&client_id=" + clientId))
        self.setWindowTitle("Authorization")
        self.show()

    def urlChanged(self, url):
        if url.toString().indexOf("#access_token") > 0:
            fragment = QUrl("?" + url.fragment())
            self.token = fragment.queryItemValue("access_token")
            self.close()

def getToken(clientId):
    app = QApplication(sys.argv)
    web = RegistrarBrowser(clientId)

    app.exec_()
    return str(web.token)

if __name__ == '__main__':
    print getToken(sys.argv[1])

