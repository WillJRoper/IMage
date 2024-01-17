"""A module defining the toolbar for the main window."""
import os

from PyQt5.QtWidgets import QToolBar, QAction
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal, Qt


from ..tools.hist import HistogramWidget


class ToolBar(QToolBar):
    """
    A tool bar containing various tools for use in the workspace.
    """

    # Define a signal to handle the selection of a tool
    toolSelected = pyqtSignal(str)

    def __init__(self, main_window):
        super(ToolBar, self).__init__("Tools", main_window)

        # Load the style sheet
        with open("src/styles/tools.qss", "r") as f:
            self.setStyleSheet(f.read())

        # Create tools
        image_open_action = self.createActionWithIcon(
            "image.png", "Open Image File"
        )
        self.addAction(image_open_action)
        histogram_action = self.createActionWithIcon(
            "histogram.png", "Histogram"
        )
        self.addAction(histogram_action)
        zoom_action = self.createActionWithIcon("magnifying-glass.png", "Zoom")
        self.addAction(zoom_action)

        # And handle the triggers for the tools
        image_open_action.triggered.connect(
            lambda: self.emitToolSelected("ImageOpen")
        )
        histogram_action.triggered.connect(
            lambda: self.emitToolSelected("Histogram")
        )
        zoom_action.triggered.connect(
            lambda: self.emitToolSelected("ZoomView")
        )

    def createActionWithIcon(self, icon_path, text):
        action = QAction(self)
        action.setIcon(QIcon(os.path.join("src/icons", icon_path)))
        action.setText(text)
        return action

    def emitToolSelected(self, tool_name):
        print(f"Emiting: {tool_name}")
        self.toolSelected.emit(tool_name)

    def createResizedIcon(self, path, size):
        pixmap = QPixmap(path).scaled(
            size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        return QIcon(pixmap)
