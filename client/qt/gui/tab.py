import threading
import time

from PyQt5.QtWidgets import *

from common.entity.entities import NodeState
from gui.tableModel import MonitorTableModel


class MonitorTab(QWidget):
    UPDATE_TIME = 5

    def __init__(self, parent=None, sector="1", controller=None, tabIndex=0, updateIcon=None):

        QWidget.__init__(self, parent)

        self.sector = sector
        self.controller = controller
        self.parent = parent
        self.tabIndex = tabIndex
        self.updateSignal = updateIcon

        self.widgetbox = QVBoxLayout()
        self.widgetbox.setContentsMargins(10, 10, 10, 10)
        self.widgetbox.setSpacing(10)

        self.staticTableTitle = QLabel("Preconfigured BBBs:")

        self.staticTable = QTableView(parent)
        self.staticTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.staticTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.staticTable.keyPressEvent = self.keyPressStaticEvent
        self.staticTableModel = MonitorTableModel(self.staticTable)

        self.staticTable.setModel(self.staticTableModel)
        self.staticTable.verticalHeader().hide()

        self.staticTable.setMinimumHeight(400)
        self.staticTable.setMinimumWidth(200)

        self.dynamicTableTitle = QLabel("Unconfigured BBBs:")

        self.rebootButton = QPushButton("Reboot")
        self.rebootButton.pressed.connect(self.rebootNode)
        self.rebootButton.setEnabled(False)

        self.switchButton = QPushButton("Switch BBBs")
        self.switchButton.pressed.connect(self.switchNode)
        self.switchButton.setEnabled(False)

        self.dynamicTable = QTableView(parent)
        self.dynamicTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.dynamicTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.dynamicTable.keyPressEvent = self.keyPressDynamicEvent
        self.dynamicTableModel = MonitorTableModel(self.dynamicTable)

        self.dynamicTable.setModel(self.dynamicTableModel)
        self.dynamicTable.verticalHeader().hide()

        self.staticTable.horizontalHeader().setStretchLastSection(True)
        self.staticTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.dynamicTable.horizontalHeader().setStretchLastSection(True)
        self.dynamicTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.staticTable.selectionChanged = self.staticSelectionChanged
        self.dynamicTable.selectionChanged = self.dynamicSelectionChanged

        self.dynamicTable.setMaximumHeight(400)
        self.dynamicTable.setMinimumWidth(200)

        self.dynamicHeader = QWidget()
        self.dynamicHeaderLayout = QHBoxLayout()
        self.dynamicHeaderLayout.addWidget(self.dynamicTableTitle)
        self.dynamicHeaderLayout.addWidget(QWidget())
        self.dynamicHeaderLayout.addWidget(self.rebootButton)
        self.dynamicHeaderLayout.addWidget(self.switchButton)
        self.dynamicHeader.setLayout(self.dynamicHeaderLayout)

        self.widgetbox.addWidget(self.staticTableTitle)
        self.widgetbox.addWidget(self.staticTable)
        self.widgetbox.addWidget(self.dynamicHeader)
        self.widgetbox.addWidget(self.dynamicTable)

        self.setLayout(self.widgetbox)

        self.scanThread = threading.Thread(target=self.scan)
        self.scanning = True
        self.scanThread.start()

    def isInWarningStateState(self):

        for node in self.staticTableModel.nodes:
            if node.state != NodeState.CONNECTED:
                return True

        if len(self.dynamicTableModel.nodes) > 0:
            return True

        return False

    def switchNode(self):
        self.controller.switch(self.selectedNode(self.staticTable), self.selectedNode(self.dynamicTable))

    def rebootNode(self):
        node = self.selectedNode(self.staticTable)
        if node.state == NodeState.CONNECTED:
            self.controller.reboot(self.selectedNode(self.staticTable))

    def selectedNode(self, table):

        rows = table.selectionModel().selectedRows()
        if len(rows) == 0:
            return None
        return table.model().nodes[rows[0].row()]

    def updateButtons(self):

        confNode = self.selectedNode(self.staticTable)
        unconfNode = self.selectedNode(self.dynamicTable)

        if confNode is None or unconfNode is None:
            self.switchButton.setEnabled(False)
            if confNode is None or confNode.state == NodeState.DISCONNECTED:
                self.rebootButton.setEnabled(False)
            else:
                self.rebootButton.setEnabled(True)
        else:

            if confNode.state != NodeState.DISCONNECTED:
                self.rebootButton.setEnabled(True)
            else:
                self.rebootButton.setEnabled(False)

            if confNode.ipAddress == unconfNode.ipAddress:
                if confNode.state == unconfNode.state and confNode.state == NodeState.MISCONFIGURED:
                    self.switchButton.setEnabled(True)
                else:
                    self.switchButton.setEnabled(False)

            elif confNode.state == NodeState.DISCONNECTED and unconfNode.state == NodeState.CONNECTED:
                self.switchButton.setEnabled(True)
            else:
                self.switchButton.setEnabled(False)

    def staticSelectionChanged(self, selected, deselected):

        self.updateButtons()
        QTableView.selectionChanged(self.staticTable, selected, deselected)

    def dynamicSelectionChanged(self, selected, deselected):

        self.updateButtons()
        QTableView.selectionChanged(self.dynamicTable, selected, deselected)

    def scan(self):

        while self.scanning:
            self.staticTableModel.setData(self.controller.getNodesFromSector(sector=self.sector, registered=True))
            self.dynamicTableModel.setData(self.controller.getNodesFromSector(sector=self.sector, registered=False))
            self.updateSignal.emit(self.tabIndex)
            self.updateButtons()
            time.sleep(MonitorTab.UPDATE_TIME)

    def hideEvent(self, evt):
        # self.scanning = False
        pass

    def stop(self):
        self.scanning = False

    def keyPressStaticEvent(self, evt):

        if evt.key() == 16777216:
            self.staticTable.clearSelection()

        QTableView.keyPressEvent(self.staticTable, evt)

    def keyPressDynamicEvent(self, evt):

        if evt.key() == 16777216:
            self.dynamicTable.clearSelection()

        QTableView.keyPressEvent(self.dynamicTable, evt)
