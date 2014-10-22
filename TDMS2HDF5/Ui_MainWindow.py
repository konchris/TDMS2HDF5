# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow_noRightSide.ui'
#
# Created: Wed Oct 22 20:41:58 2014
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
        MainWindow.resize(1324, 899)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/science-icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.mainLayout.setObjectName(_fromUtf8("mainLayout"))
        self.ySelectorLayout = QtGui.QVBoxLayout()
        self.ySelectorLayout.setObjectName(_fromUtf8("ySelectorLayout"))
        self.ySelectorLabel = QtGui.QLabel(self.centralwidget)
        self.ySelectorLabel.setObjectName(_fromUtf8("ySelectorLabel"))
        self.ySelectorLayout.addWidget(self.ySelectorLabel)
        self.ySelectorView = QtGui.QTreeView(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ySelectorView.sizePolicy().hasHeightForWidth())
        self.ySelectorView.setSizePolicy(sizePolicy)
        self.ySelectorView.setObjectName(_fromUtf8("ySelectorView"))
        self.ySelectorLayout.addWidget(self.ySelectorView)
        self.mainLayout.addLayout(self.ySelectorLayout)
        self.centralLayout = QtGui.QVBoxLayout()
        self.centralLayout.setObjectName(_fromUtf8("centralLayout"))
        self.xSelectorLayout = QtGui.QHBoxLayout()
        self.xSelectorLayout.setObjectName(_fromUtf8("xSelectorLayout"))
        self.xSelectorLabel = QtGui.QLabel(self.centralwidget)
        self.xSelectorLabel.setObjectName(_fromUtf8("xSelectorLabel"))
        self.xSelectorLayout.addWidget(self.xSelectorLabel)
        self.xSelectorView = QtGui.QListView(self.centralwidget)
        self.xSelectorView.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.xSelectorView.sizePolicy().hasHeightForWidth())
        self.xSelectorView.setSizePolicy(sizePolicy)
        self.xSelectorView.setMaximumSize(QtCore.QSize(16777215, 42))
        self.xSelectorView.setObjectName(_fromUtf8("xSelectorView"))
        self.xSelectorLayout.addWidget(self.xSelectorView)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.saveChannelCheckBox = QtGui.QCheckBox(self.centralwidget)
        self.saveChannelCheckBox.setObjectName(_fromUtf8("saveChannelCheckBox"))
        self.horizontalLayout.addWidget(self.saveChannelCheckBox)
        self.allChannels = QtGui.QPushButton(self.centralwidget)
        self.allChannels.setObjectName(_fromUtf8("allChannels"))
        self.horizontalLayout.addWidget(self.allChannels)
        self.noChannels = QtGui.QPushButton(self.centralwidget)
        self.noChannels.setObjectName(_fromUtf8("noChannels"))
        self.horizontalLayout.addWidget(self.noChannels)
        self.xSelectorLayout.addLayout(self.horizontalLayout)
        self.centralLayout.addLayout(self.xSelectorLayout)
        self.mainLayout.addLayout(self.centralLayout)
        self.gridLayout.addLayout(self.mainLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1324, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
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

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.action_Quit, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "TDMS to HDF5 Viewer and Converter", None))
        self.ySelectorLabel.setText(_translate("MainWindow", "Y-Axis Channel", None))
        self.xSelectorLabel.setText(_translate("MainWindow", "X-Axis Channel", None))
        self.saveChannelCheckBox.setText(_translate("MainWindow", "Save Channel", None))
        self.allChannels.setText(_translate("MainWindow", "All", None))
        self.noChannels.setText(_translate("MainWindow", "None", None))
        self.actionOpen_TDMS_File.setText(_translate("MainWindow", "Open &TDMS File", None))
        self.actionOpen_TDMS_File.setShortcut(_translate("MainWindow", "Ctrl+O", None))
        self.action_Export_to_HDF5.setText(_translate("MainWindow", "&Export to HDF5", None))
        self.action_Export_to_HDF5.setShortcut(_translate("MainWindow", "Ctrl+E", None))
        self.action_Quit.setText(_translate("MainWindow", "&Quit", None))
        self.action_Quit.setShortcut(_translate("MainWindow", "Ctrl+Q", None))
        self.actionOpen_Recent.setText(_translate("MainWindow", "Open Recent", None))

from .resources_rc import *
