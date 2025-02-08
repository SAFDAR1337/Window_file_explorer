# File Explorer GUI using PyQt5

## Overview
This Python script creates a file explorer application using PyQt5. It allows users to navigate directories, search for files, copy and move files via drag-and-drop, and open directories or files using the system's default file manager.

## Features
- Displays directories, subdirectories, and files.
- Allows searching within directories.
- Opens files and folders using the system's file manager.
- Supports right-click context menus with copy functionality.
- Enables drag-and-drop file movement and copying.

## Installation
### Prerequisites
Ensure you have Python installed (Python 3 recommended). Install the required dependencies:
```sh
pip install pyqt5
```

## How to Run
```sh
Window_file_explorer.py
```

## Code Explanation

### Importing Required Modules
```python
import sys
import os
import subprocess
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QFileSystemModel, QVBoxLayout, QWidget, QLabel, QMenu, QAction, QMessageBox, QFileDialog, QLineEdit
from PyQt5.QtCore import Qt, QPoint, QMimeData
from PyQt5.QtGui import QDrag
```
- `sys, os, subprocess`: Handle system operations like opening files.
- `shutil`: Enables file operations like copy/move.
- `PyQt5`: GUI framework to create the file explorer interface.

### Creating the File Explorer Window
```python
class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
```
- Defines `FileExplorer` as a subclass of `QMainWindow`.
- Calls the `super()` constructor to initialize the main window.

### Setting Up the GUI
```python
        self.setWindowTitle("Safdar Orders")
        self.setGeometry(100, 100, 1000, 600)
```
- Sets the title and size of the window.

### Directory Trees and Labels
```python
        self.left_label = QLabel("Directories")
        self.middle_label = QLabel("Subdirectories")
        self.right_label = QLabel("Files & Inner Subdirectories")
```
- Adds labels for three sections of the explorer: directories, subdirectories, and files.

### File System Models
```python
        self.left_model = QFileSystemModel()
        self.left_model.setRootPath("")  
```
- `QFileSystemModel` provides a data model to interact with the file system.
- The root path is set to an empty string initially.

### Tree View Setup
```python
        self.left_tree = QTreeView()
        self.left_tree.setModel(self.left_model)
        self.left_tree.setRootIndex(self.left_model.index("E:/Orders"))
        self.left_tree.clicked.connect(self.load_subdirectories)
        self.left_tree.doubleClicked.connect(self.open_path)
```
- Creates a tree view to show directories.
- Clicking loads subdirectories, and double-clicking opens paths.

### Search Functionality
```python
        self.left_search = QLineEdit()
        self.left_search.setPlaceholderText("Search Directories...")
        self.left_search.textChanged.connect(self.filter_left_tree)
```
- Adds a search box that filters directories based on input.

### Filtering Function
```python
    def filter_tree(self, tree, model, filter_text):
        root_index = tree.rootIndex()
        for row in range(model.rowCount(root_index)):
            index = model.index(row, 0, root_index)
            item_name = model.fileName(index).lower()
            tree.setRowHidden(row, root_index, filter_text not in item_name)
```
- Iterates through items in the directory tree and hides rows that do not match the search query.

### Opening Files and Directories
```python
    def open_path(self, index):
        path = self.sender().model().filePath(index)
        try:
            if os.path.isdir(path):
                if sys.platform == "win32":
                    subprocess.run(["explorer", os.path.abspath(path)], shell=True)
            elif os.path.isfile(path):
                if sys.platform == "win32":
                    os.startfile(os.path.abspath(path))
        except Exception as e:
            print(f"Error opening: {e}")
```
- Opens directories and files using the system's default application.

### Context Menu for File Copying
```python
    def show_context_menu(self, position: QPoint):
        index = self.right_tree.indexAt(position)
        if not index.isValid():
            return

        path = self.right_model.filePath(index)
        menu = QMenu(self)

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(lambda: self.copy_item(path))
        menu.addAction(copy_action)

        menu.exec_(self.right_tree.viewport().mapToGlobal(position))
```
- Adds a right-click menu for copying files.

### Drag and Drop Functionality
```python
    def dropEvent(self, event):
        target_index = self.right_tree.indexAt(event.pos())
        if not target_index.isValid():
            return

        target_path = self.right_model.filePath(target_index)
        source_path = event.mimeData().text()

        if os.path.isdir(target_path):
            shutil.move(source_path, target_path)
        else:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            shutil.copy(source_path, desktop_path)
        event.accept()
```
- Allows users to move files by dragging them.

## Usage Guide
1. **Run the script**: Execute `Window_file_explorer.py`.
2. **Navigate directories**: Click to expand folders.
3. **Search files**: Use search bars to filter files.
4. **Open files**: Double-click a file to open it.
5. **Right-click to copy**: Copy files using the context menu.
6. **Drag-and-drop files**: Move files between directories.

## Conclusion
This script provides a simple yet powerful file explorer using PyQt5, allowing users to manage files efficiently.

