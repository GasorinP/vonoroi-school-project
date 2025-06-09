from PyQt5.QtWidgets import QApplication

from controller import MainWindow_controller

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow_controller()
    window.show()
    sys.exit(app.exec_())