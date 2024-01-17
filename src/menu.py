from PyQt5.QtWidgets import QMenuBar, QMenu, QAction
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5 import QtCore


class MenuBar(QMenuBar):
    def __init__(self, main_window):
        super(MenuBar, self).__init__(main_window)

        font = QFont()
        font.setFamily("Hack Nerd Font Mono")

        self.setFont(font)
        self.setDefaultUp(False)

        self.setNativeMenuBar(True)

        self.setObjectName("menubar")

        self.menuFile = QMenu(self)
        self.menuFile.setTitle("File")
        self.menuFile.setFont(font)
        self.menuFile.setObjectName("menuFile")
        self.addAction(self.menuFile.menuAction())

        QtCore.QMetaObject.connectSlotsByName(self)

        # Enable opening of image files
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.parent().image_view.open_image)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        self.menuFile.addAction(open_action)

        # Add a separator
        self.menuFile.addSeparator()

        # Add a "Close" action to the menu
        close_action = QAction("Close", self)
        close_action.triggered.connect(main_window.close)
        self.menuFile.addAction(close_action)
