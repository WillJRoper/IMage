import numpy as np
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
)
from PyQt5.QtCore import QPoint, pyqtSignal

from ..tools.hist import HistogramWidget
from ..tools.zoom import ZoomWidget


class Workspace(QFrame):
    # Create signals to emit emit changes to the image.
    histChanged = pyqtSignal(float, float)
    imgOpened = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super(Workspace, self).__init__(parent)

        self.resize(
            int(0.5 * self.parent().size().width()),
            self.parent().size().height(),
        )

        # Attach the grid and attach its properties
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(5)
        self.gridLayout.setVerticalSpacing(5)
        self.col_count = 100
        self.col_width = int(self.size().width() / self.col_count)
        self.row_count = 100
        self.row_height = int(self.size().height() / self.row_count)

        # Define a variable to hold the currently selected tool
        self.selected_tool = None

        # Define the next available top-left corner for a widget.
        self.next_widget_pos = QPoint(0, 0)

        # Connect the window's resize event to a slot
        self.parent().windowResized.connect(self.handleResize)

    def toolSelected(self, tool_name):
        print(f"Tool selected: {tool_name}")
        self.selected_tool = tool_name
        widget = self.createWidget(tool_name)
        self.addWidget(widget)

    def createWidget(self, tool_name):
        match tool_name:
            case "Histogram":
                return HistogramWidget(self, preview=True)
            case "ZoomView":
                return QLabel("Zoom Widget")
                return ZoomWidget()
            case _:
                return QLabel("Placeholder Widget")

    def addWidget(self, widget):
        # Calculate the column and row span
        row_span = int(widget.size().height() / self.row_height)
        col_span = int(widget.size().width() / self.col_width)

        # Resize the widget to the grid
        widget.resize(col_span * self.col_width, row_span * self.row_height)

        # Add the widget to the layout
        self.gridLayout.addWidget(
            widget,
            self.next_widget_pos.y(),
            self.next_widget_pos.x(),
            row_span,
            col_span,
        )

        # Update the next available position for the next widget
        self.nextWidgetPosition(widget.size())

        # Connect any signals we need to propagate up.
        if isinstance(widget, HistogramWidget):
            widget.histChanged.connect(self.emit_hist_signal)
            self.imgOpened.connect(widget.set_img_data)

    def emit_hist_signal(self, low, high):
        self.histChanged.emit(low, high)

    def emit_img_loaded(self, img_arr):
        self.imgOpened.emit(img_arr)

    def nextWidgetPosition(self, size):
        column_span = int(size.width() / self.col_width)
        row_span = int(size.height() / self.row_height)

        # Get the current grid cell coordinates
        x = self.next_widget_pos.x()
        y = self.next_widget_pos.y()

        # What would the new coordinates be if we don't need to wrap?
        new_x = x + column_span
        new_y = y

        # Do we need to wrap?
        if new_x > self.col_count:
            new_x = 0
            new_y += row_span

        self.next_widget_pos.setX(new_x)
        self.next_widget_pos.setY(new_y)
        print(self.gridLayout.columnCount(), self.gridLayout.rowCount())

    def handleResize(self, size):
        print("Handling resize:", size)
        # Resize the workspace
        self.resize(int(0.5 * size.width()), size.height())

        # Resort the widgets onto the grid
        self.update_grid_pos()

    def update_grid_pos(self):
        # Clear the layout and get the widgets
        widgets = self.clearLayout()

        # Calculate the new column and row counts based on the updated size
        self.col_count = int(self.size().width() / self.col_width)
        self.row_count = int(self.size().height() / self.row_height)

        # Reset the next position
        self.next_widget_pos = QPoint(0, 0)

        # Re-add the widgets
        for widget in widgets:
            self.addWidget(widget)

    def clearLayout(self):
        # Remove and delete all widgets in the layout
        widgets = []
        while self.gridLayout.count():
            item = self.gridLayout.takeAt(0)
            widgets.append(item.widget())
        return widgets
