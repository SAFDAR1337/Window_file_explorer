import sys
import os
import subprocess
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QFileSystemModel, QVBoxLayout, QWidget, QLabel, QMenu, QAction, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QPoint

class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Safdar Orders")
        self.setGeometry(100, 100, 1000, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        self.left_label = QLabel("Directories")
        self.middle_label = QLabel("Subdirectories")
        self.right_label = QLabel("Files & Inner Subdirectories")

        self.left_model = QFileSystemModel()
        self.left_model.setRootPath("")  
        self.middle_model = QFileSystemModel()
        self.middle_model.setRootPath("")
        self.right_model = QFileSystemModel()
        self.right_model.setRootPath("")

        self.left_tree = QTreeView()
        self.left_tree.setModel(self.left_model)
        self.left_tree.setRootIndex(self.left_model.index("E:/Orders"))  
        self.left_tree.clicked.connect(self.load_subdirectories)
        self.left_tree.doubleClicked.connect(self.open_path)  

        self.middle_tree = QTreeView()
        self.middle_tree.setModel(self.middle_model)
        self.middle_tree.clicked.connect(self.load_inner_subdirectories)
        self.middle_tree.doubleClicked.connect(self.open_path)  

        self.right_tree = QTreeView()
        self.right_tree.setModel(self.right_model)
        self.right_tree.doubleClicked.connect(self.open_path)  
        self.right_tree.setContextMenuPolicy(Qt.CustomContextMenu)  
        self.right_tree.customContextMenuRequested.connect(self.show_context_menu)

        self.copied_path = None  
        self.copy_mode = None  

        layout.addWidget(self.left_label)
        layout.addWidget(self.left_tree)
        layout.addWidget(self.middle_label)
        layout.addWidget(self.middle_tree)
        layout.addWidget(self.right_label)
        layout.addWidget(self.right_tree)

    def load_subdirectories(self, index):
        path = self.left_model.filePath(index)
        if os.path.isdir(path):
            self.middle_tree.setRootIndex(self.middle_model.index(path))

    def load_inner_subdirectories(self, index):
        path = self.middle_model.filePath(index)
        if os.path.isdir(path):
            self.right_tree.setRootIndex(self.right_model.index(path))

    def open_path(self, index):
        path = self.sender().model().filePath(index)
        try:
            if os.path.isdir(path):  
                if sys.platform == "win32":
                    subprocess.run(["explorer", os.path.abspath(path)], shell=True)  
                elif sys.platform == "darwin":
                    subprocess.run(["open", os.path.abspath(path)])  
                else:
                    subprocess.run(["xdg-open", os.path.abspath(path)])  
            elif os.path.isfile(path):  
                if sys.platform == "win32":
                    os.startfile(os.path.abspath(path))  
                elif sys.platform == "darwin":
                    subprocess.run(["open", os.path.abspath(path)])  
                else:
                    subprocess.run(["xdg-open", os.path.abspath(path)])
        except Exception as e:
            print(f"Error opening: {e}")

    def show_context_menu(self, position: QPoint):
        index = self.right_tree.indexAt(position)
        if not index.isValid():
            return

        path = self.right_model.filePath(index)
        menu = QMenu(self)

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(lambda: self.copy_item(path))
        menu.addAction(copy_action)

        paste_action = QAction("Paste (Anywhere)", self)
        paste_action.setEnabled(self.copied_path is not None)  
        paste_action.triggered.connect(self.paste_item_anywhere)
        menu.addAction(paste_action)

        menu.exec_(self.right_tree.viewport().mapToGlobal(position))

    def copy_item(self, path):
        """Copy file or folder to clipboard."""
        self.copied_path = path
        self.copy_mode = "file" if os.path.isfile(path) else "folder"
        print(f"Copied: {path}")  

    def paste_item_anywhere(self):
        """Paste copied file/folder to any location selected by the user."""
        if not self.copied_path:
            QMessageBox.warning(self, "Paste Error", "Nothing copied to paste!")
            return  

        target_directory = QFileDialog.getExistingDirectory(self, "Select Folder to Paste")
        if not target_directory:
            return  

        try:
            item_name = os.path.basename(self.copied_path)
            target_path = os.path.join(target_directory, item_name)

            if os.path.exists(target_path):
                QMessageBox.warning(self, "Paste Error", f"{item_name} already exists in the target folder!")
                return  

            if self.copy_mode == "file":
                shutil.copy2(self.copied_path, target_path)  
            else:
                shutil.copytree(self.copied_path, target_path)  

            QMessageBox.information(self, "Success", f"Copied {item_name} to {target_directory}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy: {e}")

        self.copied_path = None  

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileExplorer()
    window.show()
    sys.exit(app.exec_())
