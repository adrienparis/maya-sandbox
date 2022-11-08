from PySide2 import QtCore, QtGui, QtWidgets
import sys

class Button(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.func = lambda x:x

    def clickEventRegister(self, func):
        self.func = func

    def mousePressEvent(self, event):
        self.func()

class ActivityLine(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

class Custom(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        # self.setWindowOpacity(0.9)
        self.setWindowFlags(QtCore.Qt.Popup|QtCore.Qt.FramelessWindowHint)
        self.setWindowTitle('Custom')


        radius = 10.0
        path = QtGui.QPainterPath()
        self.resize(440,220)
        path.addRoundedRect(QtCore.QRectF(self.rect()), radius, radius)
        mask = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)
        self.move(QtGui.QCursor.pos())


        # self.quitButton = Button(self)
        # self.quitButton.clickEventRegister(self.closeEvent)

    def closeEvent(self, event):
        event.accept()
        sys.exit(app.exec_())

    def mousePressEvent(self, event):
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Custom()
    w.show()
    sys.exit(app.exec_())