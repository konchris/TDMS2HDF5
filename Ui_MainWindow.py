# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created: Tue Sep  2 16:09:34 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1213, 846)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/science-icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(9, 9, 1191, 791))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.mainLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.mainLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.mainLayout.setMargin(0)
        self.mainLayout.setObjectName(_fromUtf8("mainLayout"))
        self.ySelectorLayout = QtGui.QVBoxLayout()
        self.ySelectorLayout.setObjectName(_fromUtf8("ySelectorLayout"))
        self.ySelectorLabel = QtGui.QLabel(self.horizontalLayoutWidget)
        self.ySelectorLabel.setObjectName(_fromUtf8("ySelectorLabel"))
        self.ySelectorLayout.addWidget(self.ySelectorLabel)
        self.ySelectorView = QtGui.QTreeView(self.horizontalLayoutWidget)
        self.ySelectorView.setObjectName(_fromUtf8("ySelectorView"))
        self.ySelectorLayout.addWidget(self.ySelectorView)
        self.mainLayout.addLayout(self.ySelectorLayout)
        self.centralLayout = QtGui.QVBoxLayout()
        self.centralLayout.setObjectName(_fromUtf8("centralLayout"))
        self.xSelectorLayout = QtGui.QHBoxLayout()
        self.xSelectorLayout.setObjectName(_fromUtf8("xSelectorLayout"))
        self.xSelectorLabel = QtGui.QLabel(self.horizontalLayoutWidget)
        self.xSelectorLabel.setObjectName(_fromUtf8("xSelectorLabel"))
        self.xSelectorLayout.addWidget(self.xSelectorLabel)
        self.xSelectorView = QtGui.QListView(self.horizontalLayoutWidget)
        self.xSelectorView.setObjectName(_fromUtf8("xSelectorView"))
        self.xSelectorLayout.addWidget(self.xSelectorView)
        self.centralLayout.addLayout(self.xSelectorLayout)
        self.mainLayout.addLayout(self.centralLayout)
        self.rightLayout = QtGui.QVBoxLayout()
        self.rightLayout.setObjectName(_fromUtf8("rightLayout"))
        self.offsetDisplayLayout = QtGui.QVBoxLayout()
        self.offsetDisplayLayout.setObjectName(_fromUtf8("offsetDisplayLayout"))
        self.offsetLabel = QtGui.QLabel(self.horizontalLayoutWidget)
        self.offsetLabel.setObjectName(_fromUtf8("offsetLabel"))
        self.offsetDisplayLayout.addWidget(self.offsetLabel)
        self.offsetSpinBox = QtGui.QDoubleSpinBox(self.horizontalLayoutWidget)
        self.offsetSpinBox.setObjectName(_fromUtf8("offsetSpinBox"))
        self.offsetDisplayLayout.addWidget(self.offsetSpinBox)
        self.offsetDisplayButtonLayout = QtGui.QHBoxLayout()
        self.offsetDisplayButtonLayout.setObjectName(_fromUtf8("offsetDisplayButtonLayout"))
        self.offsetPreviewCheckBox = QtGui.QCheckBox(self.horizontalLayoutWidget)
        self.offsetPreviewCheckBox.setObjectName(_fromUtf8("offsetPreviewCheckBox"))
        self.offsetDisplayButtonLayout.addWidget(self.offsetPreviewCheckBox)
        self.offsetShowButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.offsetShowButton.setObjectName(_fromUtf8("offsetShowButton"))
        self.offsetDisplayButtonLayout.addWidget(self.offsetShowButton)
        self.offsetSaveButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.offsetSaveButton.setEnabled(False)
        self.offsetSaveButton.setObjectName(_fromUtf8("offsetSaveButton"))
        self.offsetDisplayButtonLayout.addWidget(self.offsetSaveButton)
        self.offsetDisplayLayout.addLayout(self.offsetDisplayButtonLayout)
        self.rightLayout.addLayout(self.offsetDisplayLayout)
        self.attributesLabel = QtGui.QLabel(self.horizontalLayoutWidget)
        self.attributesLabel.setObjectName(_fromUtf8("attributesLabel"))
        self.rightLayout.addWidget(self.attributesLabel)
        self.attributesTableView = QtGui.QTableView(self.horizontalLayoutWidget)
        self.attributesTableView.setObjectName(_fromUtf8("attributesTableView"))
        self.rightLayout.addWidget(self.attributesTableView)
        self.saveChannelCheckBox = QtGui.QCheckBox(self.horizontalLayoutWidget)
        self.saveChannelCheckBox.setObjectName(_fromUtf8("saveChannelCheckBox"))
        self.rightLayout.addWidget(self.saveChannelCheckBox)
        self.mainLayout.addLayout(self.rightLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1213, 20))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName(_fromUtf8("menu_File"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_TDMS_File = QtGui.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen_TDMS_File.setIcon(icon1)
        self.actionOpen_TDMS_File.setObjectName(_fromUtf8("actionOpen_TDMS_File"))
        self.action_Export_to_HDF5 = QtGui.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/export.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Export_to_HDF5.setIcon(icon2)
        self.action_Export_to_HDF5.setObjectName(_fromUtf8("action_Export_to_HDF5"))
        self.action_Quit = QtGui.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/exit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Quit.setIcon(icon3)
        self.action_Quit.setObjectName(_fromUtf8("action_Quit"))
        self.actionOpen_Recent = QtGui.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/open_recent.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen_Recent.setIcon(icon4)
        self.actionOpen_Recent.setObjectName(_fromUtf8("actionOpen_Recent"))
        self.menu_File.addAction(self.actionOpen_TDMS_File)
        self.menu_File.addAction(self.actionOpen_Recent)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Export_to_HDF5)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Quit)
        self.menubar.addAction(self.menu_File.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.action_Quit, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.close)
        QtCore.QObject.connect(self.offsetPreviewCheckBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.offsetSaveButton.setEnabled)
        QtCore.QObject.connect(self.offsetPreviewCheckBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.offsetShowButton.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "TDMS to HDF5 Viewer and Converter", None))
        self.ySelectorLabel.setText(_translate("MainWindow", "Y-Axis Channel", None))
        self.xSelectorLabel.setText(_translate("MainWindow", "X-Axis Channel", None))
        self.offsetLabel.setText(_translate("MainWindow", "Channel Offset", None))
        self.offsetPreviewCheckBox.setText(_translate("MainWindow", "Preview", None))
        self.offsetShowButton.setText(_translate("MainWindow", "Show", None))
        self.offsetSaveButton.setText(_translate("MainWindow", "Save", None))
        self.attributesLabel.setText(_translate("MainWindow", "Channel Attributes", None))
        self.saveChannelCheckBox.setText(_translate("MainWindow", "Save Channel", None))
        self.menu_File.setTitle(_translate("MainWindow", "&File", None))
        self.actionOpen_TDMS_File.setText(_translate("MainWindow", "Open &TDMS File", None))
        self.actionOpen_TDMS_File.setShortcut(_translate("MainWindow", "Ctrl+O", None))
        self.action_Export_to_HDF5.setText(_translate("MainWindow", "&Export to HDF5", None))
        self.action_Export_to_HDF5.setShortcut(_translate("MainWindow", "Ctrl+E", None))
        self.action_Quit.setText(_translate("MainWindow", "&Quit", None))
        self.action_Quit.setShortcut(_translate("MainWindow", "Ctrl+Q", None))
        self.actionOpen_Recent.setText(_translate("MainWindow", "Open Recent", None))

import resources_rc

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, f)

        self.setupUi(self)

