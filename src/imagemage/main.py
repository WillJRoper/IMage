"""The main function from which runs the IMage GUI.

All functionality for IMage is contained within the module files or extension
files. This is the entry point function from which IMage is called on the
command line.

Example usage:

    py-image --hdf5 image_file.hdf5
"""
import sys
from PyQt5.QtWidgets import QApplication

from mage import ImageMage


def main():
    """
    Run IMage.

    This simply instantiates the app window and then closes when the
    application exits.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("IMage")
    main_win = ImageMage()
    main_win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
