#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" The models the view uses

"""

__author__ = "Christopher Espy"
__copyright__ = "Copyright (C) 2014, Christopher Espy"
__credits__ = ["Christopher Espy"]
__license__ = "GPL"
__version__ = "0.5"
__maintainer__ = "Christopher Espy"
__email__ = "christopher.espy@uni-konstanz.de"
__status__ = "Development"

import sys

from PyQt4.QtCore import (QAbstractItemModel, QModelIndex, Qt)
from PyQt4.QtGui import (QApplication, QTreeView)

from nptdms import TdmsFile

class TreeNode(object):

    def __init__(self, name, parent=None):
        self._parent = parent
        self._name = name
        self._children = []

        if parent is not None:
            parent.addChild(self)

    def addChild(self, child):
        self._children.append(child)

    def name(self):
        return self._name

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

        
class TreeModel(QAbstractItemModel):

    def __init__(self, root, parent=None):

        super(TreeModel, self).__init__(parent)
        self._rootNode = root
        self.filename = None

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent):
        return 1

    def data(self, index, role):

        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 0:
                return node.name()

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if section == 0:
                return "Channels"

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def parent(self, index):
        """
        Parameters
        ----------

        Returns
        -------
        """
        node = index.internalPointer()
        parentNode = node.parent()

        if parentNode == self._rootNode:
            return QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent):
        """
        Parameters
        ----------

        Returns
        -------
        """
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def loadFile(self, filename=None):
        """
        Load a file
        """
        if not QFileInfo(filename).exits():
            return

        tdmsFileObject = TdmsFile(filename)

        groupList = tdmsFileObject.groups()

        for group in groupList:
            groupProperties = tdmsFileObject.object(group).properties

            groupChannels = tdmsFileObject.group_channels(group)

            for chan in groupChannels:
                channelName = chan.path.split('/')[-1].strip("'")

                newChannel = Channel(channelName, device=group,
                                     meas_array=chan.data)

            #update selectors


    
def main(argv=None):

    if argv is None:
        argv = sys.argv

    app = QApplication(sys.argv)

    rootNode0 = TreeNode("")
    childNodeA = TreeNode("raw", rootNode0)
    childNode0 = TreeNode("I", childNodeA)
    childNode1 = TreeNode("V", childNodeA)
    childNode2 = TreeNode("R", childNodeA)
    childNode3 = TreeNode("dI", childNodeA)
    childNode4 = TreeNode("dV", childNodeA)
    childNode5 = TreeNode("dR", childNodeA)

    childNodeB = TreeNode("proc", rootNode0)
    childNode6 = TreeNode("I", childNodeB)
    childNode7 = TreeNode("V", childNodeB)
    childNode8 = TreeNode("R", childNodeB)
    childNode9 = TreeNode("dI", childNodeB)
    childNode10 = TreeNode("dV", childNodeB)
    childNode11 = TreeNode("dR", childNodeB)

    model = TreeModel(rootNode0)

    treeView = QTreeView()
    treeView.show()

    treeView.setModel(model)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

