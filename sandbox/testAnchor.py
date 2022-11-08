#!/usr/bin/python
"""
ZetCode PySide tutorial

This example shows an icon
in the titlebar of the window.

author: Jan Bodnar
website: zetcode.com
"""

from PySide2 import QtCore, QtGui, QtWidgets
import sys

class Example(QtWidgets.QWidget):

    def __init__(self):
        super(Example, self).__init__()
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        self.initUI()

    def initUI(self):

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QtGui.QIcon('web.png'))

        self.lay = QtWidgets.QGraphicsAnchorLayout()
        self.setLayout(self.lay)

        self.show()

def main():

    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    # help(QtWidgets.QGraphicsAnchorLayout)
    main()