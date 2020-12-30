def check(string):
    reUrl = "(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+"
    url = re.match(reUrl, string)
    print(url)
    return not url

class Ui_MainWindow(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.defaultUrl = QtCore.QUrl("https://www.google.com")
        self.searchUrl = "https://www.google.com/?#q="

    def goToUrl(self):
        url = QtCore.QUrl(self.le_urlAddress.text())
        if check(url.toString()):
            url = QtCore.QUrl(self.searchUrl + self.le_urlAddress.text())
        else:
            if url.toString() == "":
                self.webEngineView.load(self.defaultUrl)
            if url.scheme() == "":
                url.setScheme("http")
        self.webEngineView.load(url)

    def homepg(self):
        self.webEngineView.load(self.defaultUrl)

    def updatedUrl(self):
        self.le_urlAddress.setText(self.webEngineView.url().url())

    def openFile(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open file", "", "Hypertext Markup Language (*.htm *.html);;", "All files (*.*)")
        if filename:
            with open(filename, 'r') as f:
                html = f.read()
        self.webEngineView.setHtml(html)
        self.le_urlAddress.setText(filename)

    def saveFile(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Page As", "", "Hypertext Markup Language (*.htm *html);;", "All files (*.*)")
        if filename:
            html = self.webEngineView.page().toHtml()
            with open(filename, 'w') as f:
                f.write(html)