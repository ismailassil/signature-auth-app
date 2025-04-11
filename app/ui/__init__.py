"""
User Interface components

Includes:
- DashboardScreen: Main application screen with camera and results
- GuideScreen: User instructions and documentation
"""

__all__ = ["DashboardScreen", "GuideScreen"]

from .dashboard import DashboardScreen
from .guide import GuideScreen

# Kivy builder imports
from kivy.lang import Builder
import os

# Load KV language templates
# Builder.load_file(os.path.join(os.path.dirname(__file__), 'ui.kv'))