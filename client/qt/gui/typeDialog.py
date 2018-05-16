import threading
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from common.entity.entities import Type
from gui.tableModel import TypeTableModel


class TypeDialog(QDialog):
    DIALOG_WIDTH = 1200
    DIALOG_HEIGHT = 600

    UPDATE_TIME = 5

    def __init__(self, parent=None, controller=None):

        super(TypeDialog, self).__init__(parent)

        self.controller = controller

        self.input = QWidget()

        self.inputLayout = QFormLayout()
        self.inputLayout.setContentsMargins(0, 0, 0, 0)

        self.input.setLayout(self.inputLayout)

        self.namelabel = QLabel("Name:")
        self.name = QLineEdit()

        self.descriptionLabel = QLabel("Description:")
        self.description = QTextEdit()
        self.description.setMinimumHeight(85)

        self.urlRcLocalLabel = QLabel("Rc Local URL:")
        self.urlRcLocal = QLineEdit()

        self.buttons = QWidget()
        self.buttonsLayout = QGridLayout()
        self.buttonsLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonsLayout.setSpacing(10)

        self.colorButton = QPushButton("Choose color")
        self.colorButton.setAutoFillBackground(True)
        self.colorButton.pressed.connect(self.selectColor)

        self.submit = QPushButton("+")
        self.submit.pressed.connect(self.appendType)

        self.buttonsLayout.addWidget(QWidget(), 0, 0, 1, 5)
        self.buttonsLayout.addWidget(self.colorButton, 0, 5, 1, 1)
        self.buttonsLayout.addWidget(self.submit, 0, 6, 1, 1)

        self.buttons.setLayout(self.buttonsLayout)

        self.outerLayout = QVBoxLayout()
        self.outerLayout.setContentsMargins(10, 10, 10, 10)
        self.outerLayout.setSpacing(10)

        self.typeTable = QTableView(parent)
        self.typeTable.selectionChanged = self.selectionChanged
        self.typeTable.keyPressEvent = self.keyPressEvent
        self.typeTable.resizeRowsToContents()
        self.typeTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.typeTable.setSelectionMode(QAbstractItemView.SingleSelection)

        self.typeTableModel = TypeTableModel(self.typeTable, data=self.controller.fetchTypes())
        self.typeTable.setModel(self.typeTableModel)

        self.typeTable.horizontalHeader().setStretchLastSection (True)
        self.typeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.typeTable.setMinimumHeight(800)
        self.typeTable.setMinimumWidth(500)

        self.labelTable = QLabel("Available types: (press [DEL] to remove)")

        self.inputLayout.addWidget(self.namelabel)
        self.inputLayout.addWidget(self.name)
        self.inputLayout.addWidget(self.urlRcLocalLabel)
        self.inputLayout.addWidget(self.urlRcLocal)
        self.inputLayout.addWidget(self.descriptionLabel)
        self.inputLayout.addWidget(self.description)

        self.outerLayout.addWidget(self.input)
        self.outerLayout.addWidget(self.buttons)
        self.outerLayout.addWidget(self.labelTable)
        self.outerLayout.addWidget(self.typeTable)

        self.setLayout(self.outerLayout)

        self.setGeometry(500, 500, TypeDialog.DIALOG_WIDTH, TypeDialog.DIALOG_HEIGHT)

        self.setWindowTitle("Types Management")

        self.cdialog = QColorDialog(QColor(255, 255, 0), self)

        self.scanThread = threading.Thread(target=self.scan)
        self.scanning = True
        self.scanThread.start()

    def keyPressEvent(self, evt):

        # Del
        if evt.key() == 16777223 and len(self.typeTable.selectedIndexes()) > 0:

            selectedRow = self.typeTable.selectedIndexes()[0].row()
            typeName = self.typeTableModel.data(self.typeTableModel.index(selectedRow, 0), Qt.DisplayRole)

            self.controller.removeType(typeName)
            self.typeTableModel.setData(self.controller.fetchTypes())
            self.typeTable.clearSelection()

        elif evt.key() == 16777216:

            self.name.clear()
            self.description.clear()
            self.typeTable.clearSelection()
            self.cdialog.setCurrentColor(QColor(255, 255, 0))

        QTableView.keyPressEvent(self.typeTable, evt)

    def selectionChanged(self, selected, deselected):

        if len(selected.indexes()) > 0:
            selectedRow = selected.indexes()[0].row()
            typeObject = self.typeTableModel.types[selectedRow]

            self.name.setText(typeObject.name)
            self.description.setPlainText(typeObject.description)
            self.cdialog.setCurrentColor(QColor(typeObject.color[0], typeObject.color[1], typeObject.color[2]))

        QTableView.selectionChanged(self.typeTable, selected, deselected)

    def selectColor(self):

        self.cdialog.open()

    def appendType(self):

        selectedColor = self.cdialog.currentColor()

        newType = Type(name=self.name.displayText(), description=self.description.toPlainText(),
                       color=(selectedColor.red(), selectedColor.green(), selectedColor.blue()))

        success = self.controller.appendType(newType)

        self.typeTableModel.setData(self.controller.fetchTypes())
        self.typeTable.clearSelection()

    def scan(self):

        while self.scanning:
            self.typeTableModel.setData(self.controller.fetchTypes())
            time.sleep(TypeDialog.UPDATE_TIME)

    def closeEvent(self, args):

        self.scanning = False

        QDialog.closeEvent(self, args)
