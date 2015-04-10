#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" The models the view uses

This was copied from somewhere on the internet, but I don't know where!

"""

__author__ = "Christopher Espy"
__copyright__ = "Copyright (C) 2014, Christopher Espy"
__credits__ = ["Christopher Espy"]
__license__ = "GPL"
__version__ = "0.5"
__maintainer__ = "Christopher Espy"
__email__ = "christopher.espy@uni-konstanz.de"
__status__ = "Development"

from PyQt4.QtCore import (QAbstractItemModel, QModelIndex, Qt)
from PyQt4.QtGui import (QApplication, QTreeView, QStringListModel)

from TDMS2HDF5.ChannelModel import ChannelRegistry


class TreeNode(object):
    """A node in the groups/channels tree view model.

    Parameters
    ----------
    name : str
        The name of the node
    parent : TreeNode, optional
        The name of the parent node

    Methods
    -------
    addChild(child : TreeNode):
        Add a child to the node.
    name():
        Get the name of the node.
    child(row : int):
        Return the child node with the index row.
    childCount():
        Return the number of children the node has.
    parent():
        Return the node's parent node.
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
    """The Tree Model.

    Parameters
    ----------
    root : TreeNode
       The root node of the tree
    parent : QObject, optional
       The optional PyQt object

    Methods
    -------
    rowCount(parent : QModelIndex):
        Returns the number of rows under the given /parent/.
    columnCount(parent : QModelIndex):
        Returns the number of columns for the children of the given /parent/.
    data(index : QModelIndex, role : Qt.DisplayRole):
        Returns the data stored under the given /role/ for the item referred to
        by the /index/.
    headerData(section : int, orientation : Qt.Orientation,
               role : QtDisplayRole):
        Returns the data for the given /role/ and /section/ in the header with
        with the specified /orientation/.
    flags(index : QModelIndex):
        Returns the item flags for the given /index/.
    parent(index : QModelIndex):
        Returns the parent of the model item with the given /index/.
    index(row : int, column : int, parent : QModexIndex):
        Returns the index of the item in the model specified by the given
        /row/, /column/ and /parent/ index.


    """

    def __init__(self, root, parent=None):

        super(TreeModel, self).__init__(parent)
        self._rootNode = root

    def rowCount(self, parent):
        """Returns the number of rows under the given /parent/.

        When the parent is valied it means that rowCount is returning the
        number of children of parent.

        Paramters
        ---------
        parent : view_model.TreeNode
            The parent node of the current node.

        Returns
        -------
        row_count : int
            The number of children of the parent node.

        """
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent):
        """Returns the number of columns for the children of the given /parent/.

        Paramters
        ---------
        parent : view_model.TreeNode
            The parent node of the current node.

        Returns
        -------
        column_count : int
            The number of columns of the parent node.
            This just returns "1" because we only use one column.

        """
        return 1

    def data(self, index, role):
        """Returns the data stored under the given /role/ for the item
        referred to by the /index/.

        Parameters
        ----------
        index : QModelIndex
            The index of the node in question.
        role : Qt.DisplayRole
            The display role of the data to be retuned.

        Returns
        -------
        node_name : QVariant
            The name of the node at the given index

        """
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 0:
                return node.name()

    def headerData(self, section, orientation, role):
        """Returns the data for the given /role/ and /section/ in the header
        with the specified /orientation/.

        Parameters
        ----------
        section : int
            The section to be queried.
        orientation : Qt.Orientation
        role : Qt.DisplayRole
            The display role.

        Returns
        -------
        header_data : QVariant
            The header data. In this case it is always "Channels"

        """
        if role == Qt.DisplayRole:
            if section == 0:
                return "Channels"

    def flags(self, index):
        """Returns the item flags for the given /index/.

        Parameters
        ----------
        index : QModelIndex
            The index of the item whose flags are to be returned.

        Returns
        -------
        flags : Qt.ItemFlags

        """
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def parent(self, index):
        """Returns the parent of the model item with the given /index/.

        Parameters
        ----------
        index : QModelIndex
            The index of the item whose parent is returned.

        Returns
        -------
        parent : QModelIndex


        """
        node = index.internalPointer()
        parentNode = node.parent()

        if parentNode == self._rootNode:
            return QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent):
        """Returns the index of the item in the model specified by the given
        /row/, /column/ and /parent/ index.

        Parameters
        ----------
        row : int
        column : int
        parent : QModelIndex

        Returns
        -------
        index : QModelIndex


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
    """Subclassed QStringListModel for a simple list."""

    def __init__(self, parent=None):

        super(MyListModel, self).__init__(parent)


def main(argv=None):
    """The main function when running module standalone."""

    import os
    import sys

    if argv is None:
        argv = sys.argv

    def print_clicked(msg=None):
        """Print a short message when an Item is clicked.

        Parameters
        ----------
        msg : QModelIndex, optional

        """
        if isinstance(msg, QModelIndex):
            if not msg.data() in ['proc', 'raw']:
                selectedItemName = msg.data()
                selectedItemParent = msg.parent().data()
                print('Item {0}/{1} was clicked.'.format(selectedItemParent,
                                                         selectedItemName))

    app = QApplication(sys.argv)

    testfile01 = os.path.join("/home/chris/Documents/PhD/root/raw-data",
                              "sio2al149/CryoMeasurement",
                              "2014-02-14T14-39-08-First-Cooldown.tdms")
    testfile02 = os.path.join("/home/chris/Espy/MeasData/HelioxTesting",
                              "2014-04-09T10-48-33-Cool-Down.tdms")

    chanReg = ChannelRegistry()
    chanReg.loadFromFile(testfile01)

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
