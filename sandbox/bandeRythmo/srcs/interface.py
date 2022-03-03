import sys
from PySide2 import QtCore, QtGui, QtWidgets

app = QtWidgets.QApplication(sys.argv)

win = QtWidgets.QWidget()

win.resize(320, 240)
win.setWindowTitle("Cappella reader")
win.show()

sys.exit(app.exec_())