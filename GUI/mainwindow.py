from PyQt5.QtCore import QFile, QIODevice, Qt, QItemSelectionModel
from PyQt5.QtWidgets import QMainWindow, QApplication

from GUI.mainwindow_ui import Ui_MainWindow
from Models.tree_model import TreeModel

import Resources.editabletreemodel_rc


class MainWindow(QMainWindow, Ui_MainWindow):
    # Конструктор класса
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        # Создание формы и Ui (наш дизайн)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        headers: list[str] = ['Title', 'Description']

        file = QFile(':/default.txt')

        file.open(QIODevice.ReadOnly)
        model = TreeModel(headers, file.readAll())
        file.close()

        self.ui.view.setModel(model)

        for column in range(model.columnCount()):
            self.ui.view.resizeColumnToContents(column)

        self.ui.exitAction.triggered.connect(QApplication.instance().quit)

        self.ui.view.selectionModel().selectionChanged.connect(self.updateActions)

        self.ui.actionsMenu.aboutToShow.connect(self.updateActions)
        self.ui.insertRowAction.triggered.connect(self.insertRow)
        self.ui.insertColumnAction.triggered.connect(self.insertColumn)
        self.ui.removeRowAction.triggered.connect(self.removeRow)
        self.ui.removeColumnAction.triggered.connect(self.removeColumn)
        self.ui.insertChildAction.triggered.connect(self.insertChild)

        self.updateActions()

    def insertChild(self):
        index = self.ui.view.selectionModel().currentIndex()
        model = self.ui.view.model()

        if model.columnCount(index) == 0:
            if not model.insertColumn(0, index):
                return

        if not model.insertRow(0, index):
            return

        for column in range(model.columnCount(index)):
            child = model.index(0, column, index)
            model.setData(child, "[No data]", Qt.EditRole)
            if model.headerData(column, Qt.Horizontal) is None:
                model.setHeaderData(column, Qt.Horizontal, "[No header]",
                                    Qt.EditRole)

        self.ui.view.selectionModel().setCurrentIndex(model.index(0, 0, index),
                                                      QItemSelectionModel.ClearAndSelect)
        self.updateActions()

    def insertColumn(self):
        model = self.ui.view.model()
        column = self.ui.view.selectionModel().currentIndex().column()

        changed = model.insertColumn(column + 1)
        if changed:
            model.setHeaderData(column + 1, Qt.Horizontal, "[No header]",
                                Qt.EditRole)

        self.updateActions()

        return changed

    def insertRow(self):
        index = self.ui.view.selectionModel().currentIndex()
        model = self.ui.view.model()

        if not model.insertRow(index.row() + 1, index.parent()):
            return

        self.updateActions()

        for column in range(model.columnCount(index.parent())):
            child = model.index(index.row() + 1, column, index.parent())
            model.setData(child, "[No data]", Qt.EditRole)

    def removeColumn(self):
        model = self.ui.view.model()
        column = self.ui.view.selectionModel().currentIndex().column()

        changed = model.removeColumn(column)
        if changed:
            self.updateActions()

        return changed

    def removeRow(self):
        index = self.ui.view.selectionModel().currentIndex()
        model = self.ui.view.model()

        if model.removeRow(index.row(), index.parent()):
            self.updateActions()

    def updateActions(self):
        hasSelection = not self.ui.view.selectionModel().selection().isEmpty()
        self.ui.removeRowAction.setEnabled(hasSelection)
        self.ui.removeColumnAction.setEnabled(hasSelection)

        hasCurrent = self.ui.view.selectionModel().currentIndex().isValid()
        self.ui.insertRowAction.setEnabled(hasCurrent)
        self.ui.insertColumnAction.setEnabled(hasCurrent)

        if hasCurrent:
            self.ui.view.closePersistentEditor(self.ui.view.selectionModel().currentIndex())

            row = self.ui.view.selectionModel().currentIndex().row()
            column = self.ui.view.selectionModel().currentIndex().column()
            if self.ui.view.selectionModel().currentIndex().parent().isValid():
                self.statusBar().showMessage("Position: (%d,%d)" % (row, column))
            else:
                self.statusBar().showMessage("Position: (%d,%d) in top level" % (row, column))
