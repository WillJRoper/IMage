from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5 import QtCore, QtWidgets

from widgets.image import ImageView
from widgets.menu import MenuBar
from widgets.toolbar import ToolBar
from widgets.workspace import Workspace
from tools.utility_widgets import SideGrip


class ImageMage(QMainWindow):
    _gripSize = 8

    # Signal emitted when the window is resized
    windowResized = pyqtSignal(QSize)

    def __init__(self):
        super().__init__()

        self.setupMainWindowStyles()
        self.initUI()
        self.initSignals()

        self.sideGrips = [
            SideGrip(self, QtCore.Qt.LeftEdge),
            SideGrip(self, QtCore.Qt.TopEdge),
            SideGrip(self, QtCore.Qt.RightEdge),
            SideGrip(self, QtCore.Qt.BottomEdge),
        ]
        # corner grips should be "on top" of everything, otherwise the side grips
        # will take precedence on mouse events, so we are adding them *after*;
        # alternatively, widget.raise_() can be used
        self.cornerGrips = [QtWidgets.QSizeGrip(self) for i in range(4)]

        # Define a variable to handle mouse click events
        self.initial_click_pos = None

    def setupMainWindowStyles(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle("Modular and Customizable UI")

        # Load the window style sheet
        with open("src/styles/window.qss", "r") as f:
            self.setStyleSheet(f.read())

    def initUI(self):
        self.toolbar = ToolBar(self)
        self.addToolBar(Qt.RightToolBarArea, self.toolbar)

        # Create main workspace
        self.workspace = Workspace(self)
        self.setCentralWidget(self.workspace)

        self.image_view = ImageView(self)
        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            self.createDockWidget(self.image_view, "Image"),
        )

        self.menuBar = MenuBar(self)
        self.setMenuBar(self.menuBar)

        self.retranslateUi(self)

    def createDockWidget(self, widget, title):
        dock_widget = QtWidgets.QDockWidget(title, self)
        dock_widget.setWidget(widget)
        dock_widget.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable
            | QtWidgets.QDockWidget.DockWidgetFloatable
        )
        return dock_widget

    def initSignals(self):
        # Connect the toolSelected signal from the ToolBar to the
        # Workspace
        self.toolbar.toolSelected.connect(self.workspace.toolSelected)
        self.workspace.histChanged.connect(self.image_view.update_vlims)
        self.image_view.imgOpened.connect(self.workspace.emit_img_loaded)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "IMage"))
        self.menuBar.menuFile.setTitle(_translate("MainWindow", "File"))

    def mousePressEvent(self, event):
        # Capture the initial position when a mouse button is pressed
        self.initial_click_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.initial_click_pos is not None:
            # Calculate the movement offset
            offset = event.globalPos() - self.initial_click_pos

            # Move the window based on the offset
            self.move(self.x() + offset.x(), self.y() + offset.y())

            # Update the initial position for the next iteration
            self.initial_click_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        # Reset the initial click position when the mouse button is released
        self.initial_click_pos = None

    @property
    def gripSize(self):
        return self._gripSize

    def setGripSize(self, size):
        if size == self._gripSize:
            return
        self._gripSize = max(2, size)
        self.updateGrips()

    def updateGrips(self):
        self.setContentsMargins(*[self.gripSize] * 4)

        outRect = self.rect()
        # an "inner" rect used for reference to set the geometries of size grips
        inRect = outRect.adjusted(
            self.gripSize, self.gripSize, -self.gripSize, -self.gripSize
        )

        # top left
        self.cornerGrips[0].setGeometry(
            QtCore.QRect(outRect.topLeft(), inRect.topLeft())
        )
        # top right
        self.cornerGrips[1].setGeometry(
            QtCore.QRect(outRect.topRight(), inRect.topRight()).normalized()
        )
        # bottom right
        self.cornerGrips[2].setGeometry(
            QtCore.QRect(inRect.bottomRight(), outRect.bottomRight())
        )
        # bottom left
        self.cornerGrips[3].setGeometry(
            QtCore.QRect(
                outRect.bottomLeft(), inRect.bottomLeft()
            ).normalized()
        )

        # left edge
        self.sideGrips[0].setGeometry(
            0, inRect.top(), self.gripSize, inRect.height()
        )
        # top edge
        self.sideGrips[1].setGeometry(
            inRect.left(), 0, inRect.width(), self.gripSize
        )
        # right edge
        self.sideGrips[2].setGeometry(
            inRect.left() + inRect.width(),
            inRect.top(),
            self.gripSize,
            inRect.height(),
        )
        # bottom edge
        self.sideGrips[3].setGeometry(
            self.gripSize,
            inRect.top() + inRect.height(),
            inRect.width(),
            self.gripSize,
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.updateGrips()
        self.windowResized.emit(self.size())
