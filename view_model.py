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
from PyQt4.QtGui import (QApplication, QTreeView, QStringListModel)

from ChannelModel import ChannelRegistry

class TreeNode(object):
    """A node in the groups/channels tree view model.

    Parameters
    ----------
    name : str
        The name of the node
    parent : TreeNode, optional
        The possible name of the parent node

    Methods
    -------
    addChild(child : TreeNode):
        Add a child to the node.
    name():
        Get the name of the node.
    child(row : int):
        Return the child node in the row-th position.
    childCount():
        Return the number of children the node has.
    parent():
        Return the node's parent.
    row():
        Return the node's row index in its parent node.


    """

    def __init__(self, name, parent=None):
        self._parent = parent
        self._name = name
        self._children = []

        if parent is not None:
            parent.addChild(self)

    def addChild(self, child):
        """Add a child to the node.

        Parameters
        ----------
        child : TreeNode
            A TreeNode object to add as a child to the current node.

        """
        self._children.append(child)

    def name(self):
        """Get the name of the node.

        Returns
        -------
        _name : str
            The name of the current node.

        """
        return self._name

    def child(self, row):
        """Return the child node in the row-th position.

        Parameters
        ----------
        row : int
            The position of the child node you want to know.

        Returns
        -------
        children[row] : TreeNode
            The child node object at row position in the current node.

        """
        return self._children[row]

    def childCount(self):
        """Return the number of children the node has.

        Returns
        -------
        len(_children) : int
            The number of children the current node has.

        """
        return len(self._children)

    def parent(self):
        """Return the node's parent.

        Returns
        -------
        _parent : TreeNode
            The node object of the parent of the current node.

        """
        return self._parent

    def row(self):
        """Return the node's row index in its parent node.

        Returns
        ------
        row : int
            The index of the current node in its parent node.

        """
        if self._parent is not None:
            return self._parent._children.index(self)


class TreeModel(QAbstractItemModel):

    def __init__(self, root, parent=None):

        super(TreeModel, self).__init__(parent)
        self._rootNode = root
        self.filename = None
        self.channels = ChannelRegistry()

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

class MyListModel(QStringListModel):
    pass

def print_clicked(msg=None):
    if isinstance(msg, QModelIndex):
        if not msg.data() in ['proc', 'raw']:
            selectedItemName = msg.data()
            selectedItemParent = msg.parent().data()
            print('Item {0}/{1} was clicked.'.format(selectedItemParent, selectedItemName))

def main(argv=None):

    if argv is None:
        argv = sys.argv

    app = QApplication(sys.argv)

    testfile01 = "/home/chris/Documents/PhD/root/raw-data/sio2al149/CryoMeasurement/2014-02-14T14-39-08-First-Cooldown.tdms"
    testfile02 = "/home/chris/Espy/MeasData/HelioxTesting/2014-04-09T10-48-33-Cool-Down.tdms"

    chanReg = ChannelRegistry()
    chanReg.loadFromFile(testfile02)

    rootNode0 = TreeNode("")
    raw = 'raw'
    proc = 'proc'
    rawNode = TreeNode(raw, rootNode0)
    procNode = TreeNode(proc, rootNode0)
    for k, v in chanReg.items():
        if raw in k:
            childNode = TreeNode(v.name, rawNode)
        elif proc in k:
            childNode = TreeNode(v.name, procNode)

    model = TreeModel(rootNode0)

    treeView = QTreeView()
    treeView.show()

    treeView.setModel(model)

    treeView.clicked.connect(print_clicked)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

