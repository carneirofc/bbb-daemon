from PyQt4.QtGui import QDialog, QLabel, QPushButton, QTableView, QAbstractItemView,\
                        QLineEdit, QTextEdit, QHBoxLayout, QVBoxLayout, QMessageBox, QColorDialog, QGridLayout
from PyQt4.QtCore import *
from PyQt4.Qt import QWidget

import gui.table
import threading
import time

class TypeDialog (QDialog):

    DIALOG_WIDTH = 900
    DIALOG_HEIGHT = 600

    def __init__ (self, parent = None, controller = None):

        super (TypeDialog, self).__init__ (parent)

        self.controller = controller

        self.input = QWidget ()

        self.inputLayout = QHBoxLayout()
        self.inputLayout.setContentsMargins (0, 0, 0, 0)

        self.namelabel = QLabel ("Name:")
        self.text = QLineEdit ()

        self.inputLayout.addWidget (self.namelabel)
        self.inputLayout.addWidget (self.text)

        self.input.setLayout (self.inputLayout)

        self.descriptionLabel = QLabel ("Description:")
        self.description = QTextEdit ()
        self.description.setMinimumHeight (85)

        self.buttons = QWidget ()
        self.buttonsLayout = QGridLayout()
        self.buttonsLayout.setContentsMargins (0, 0, 0, 0)
        self.buttonsLayout.setSpacing (10)

        self.colorButton = QPushButton ("Choose color")
        self.colorButton.setAutoFillBackground (True)
        self.colorButton.pressed.connect (self.selectColor)

        self.submit = QPushButton ("+")
        self.submit.pressed.connect (self.appendType)

        self.buttonsLayout.addWidget (QWidget (), 0, 0, 1, 5)
        self.buttonsLayout.addWidget (self.colorButton, 0, 5, 1, 1)
        self.buttonsLayout.addWidget (self.submit, 0, 6, 1, 1)

        self.buttons.setLayout (self.buttonsLayout)

        self.outerLayout = QVBoxLayout ()
        self.outerLayout.setContentsMargins (10, 10, 10, 10)
        self.outerLayout.setSpacing (10)

        self.typeTable = QTableView (parent)
        self.typeTable.selectionChanged = self.selectionChanged
        self.typeTable.keyPressEvent = self.keyPressEvent
        self.typeTable.resizeRowsToContents ();
        self.typeTable.setSelectionBehavior (QAbstractItemView.SelectRows)
        self.typeTable.setSelectionMode (QAbstractItemView.SingleSelection);

        self.typeTableModel = gui.table.TypeTableModel (self.typeTable, data = self.controller.fetchTypes ())
        self.typeTable.setModel (self.typeTableModel)
        self.typeTable.setColumnWidth(0, TypeDialog.DIALOG_WIDTH / 4);
        self.typeTable.setColumnWidth(1, 3 * TypeDialog.DIALOG_WIDTH / 3);

        self.typeTable.setMinimumHeight (800)
        self.typeTable.setMinimumWidth (500)

        self.labelTable = QLabel ("Available types: (press [DEL] to remove)")

        self.outerLayout.addWidget (self.input)
        self.outerLayout.addWidget (self.descriptionLabel)
        self.outerLayout.addWidget (self.description)
        self.outerLayout.addWidget (self.buttons)
        self.outerLayout.addWidget (self.labelTable)
        self.outerLayout.addWidget (self.typeTable)

        self.setLayout (self.outerLayout)

        self.setGeometry (500, 500, TypeDialog.DIALOG_WIDTH, TypeDialog.DIALOG_HEIGHT)

        self.setWindowTitle ("Types Management")

        self.cdialog = QColorDialog (self)

        self.scanThread = threading.Thread (target = self.scan)

        self.scanning = True
        self.scanThread.start ()

    def keyPressEvent (self, evt):

        # Del
        if evt.key () == 16777223 and len(self.typeTable.selectedIndexes ()) > 0:

            selectedRow = self.typeTable.selectedIndexes ()[0].row ()
            self.controller.removeType (self.controller.typeList ()[selectedRow])
            self.typeTableModel.setData (self.controller.fetchTypes ())
            self.typeTable.clearSelection ()

        QTableView.keyPressEvent (self.typeTable, evt)

    def selectionChanged (self, selected, deselected):

        if len(selected.indexes ()) > 0:
                selectedRow = selected.indexes ()[0].row ()

        QTableView.selectionChanged (self.typeTable, selected, deselected)

    def selectColor (self):

        self.cdialog.open ()

    def appendType (self):

        selectedColor = self.cdialog.selectedColor ()

        success = self.controller.appendType ({"name" : self.text.displayText() , \
                                               "description" : self.description.toPlainText (), \
                                               "color" : (selectedColor.red (), selectedColor.green (), selectedColor.blue ())})

        if not success:
            QMessageBox (QMessageBox.Warning, "Failed!", "This type already exists!", QMessageBox.Ok, self).open ()

        self.typeTableModel.setData (self.controller.fetchTypes ())
        self.typeTable.clearSelection ()

    def scan (self):

        while self.scanning:

            self.typeTableModel.setData (self.controller.fetchTypes ())
            time.sleep (1)

    def resizeEvent (self, args):

        self.typeTable.setColumnWidth(0, self.typeTable.size ().width () / 4 - 5);
        self.typeTable.setColumnWidth(1, 3 * self.typeTable.size ().width () / 4);

        QDialog.resizeEvent (self, args)

    def closeEvent (self, args):

        self.scanning = False

        QDialog.closeEvent (self, args)
