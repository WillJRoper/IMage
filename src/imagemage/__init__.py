import os

from imagemage._version import __version__

# Get the package root directory
package_source = os.path.dirname(os.path.abspath(__file__)) + "/../"

# Define some useful paths
styles_dir = package_source + "styles/"
icons_dir = package_source + "icons/"

# Make them available within all modules
__all__ = ["__version__", "styles_dir", "icons_dir"]
