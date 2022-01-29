import sys

from PyQt5.QtCore import QLockFile, QDir
from PyQt5.QtWidgets import QApplication, QMessageBox

from GUI.mainwindow import MainWindow


def main():
    app = QApplication([])

    lock_file = QLockFile(QDir.temp().absoluteFilePath('TreeViewApp.lock'))

    if not lock_file.tryLock(100):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText('Приложение уже запущено.\n'
                        'Разрешено запускать только один экземпляр приложения.')
        msg_box.setWindowTitle('Ошибка')
        msg_box.exec_()
        return 1

    widget = MainWindow()
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
