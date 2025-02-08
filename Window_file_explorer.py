import sys
import os
import subprocess
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QFileSystemModel, QVBoxLayout, QWidget, QLabel, QMenu, QAction, QMessageBox, QFileDialog, QLineEdit
from PyQt5.QtCore import Qt, QPoint, QMimeData
from PyQt5.QtGui import QDrag

class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Safdar Orders")
        self.setGeometry(100, 100, 1000, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        self.left_search = QLineEdit()
        self.left_search.setPlaceholderText("Search Directories...")
        self.left_search.textChanged.connect(self.filter_left_tree)
        
        self.middle_search = QLineEdit()
        self.middle_search.setPlaceholderText("Search Subdirectories...")
        self.middle_search.textChanged.connect(self.filter_middle_tree)

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
        self.right_tree.setDragEnabled(True)
        self.right_tree.setAcceptDrops(True)
        self.right_tree.viewport().setAcceptDrops(True)
        self.right_tree.setDropIndicatorShown(True)

        self.copied_path = None  
        self.copy_mode = None  

        layout.addWidget(self.left_label)
        layout.addWidget(self.left_search)
        layout.addWidget(self.left_tree)
        layout.addWidget(self.middle_label)
        layout.addWidget(self.middle_search)
        layout.addWidget(self.middle_tree)
        layout.addWidget(self.right_label)
        layout.addWidget(self.right_tree)

    def filter_left_tree(self):
        filter_text = self.left_search.text().lower()
        self.left_tree.setRootIndex(self.left_model.index("E:/Orders"))
        self.filter_tree(self.left_tree, self.left_model, filter_text)

    def filter_middle_tree(self):
        filter_text = self.middle_search.text().lower()
        self.filter_tree(self.middle_tree, self.middle_model, filter_text)

    def filter_tree(self, tree, model, filter_text):
        root_index = tree.rootIndex()
        for row in range(model.rowCount(root_index)):
            index = model.index(row, 0, root_index)
            item_name = model.fileName(index).lower()
            tree.setRowHidden(row, root_index, filter_text not in item_name)

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

        menu.exec_(self.right_tree.viewport().mapToGlobal(position))

    def copy_item(self, path):
        self.copied_path = path
        self.copy_mode = "file" if os.path.isfile(path) else "folder"
        print(f"Copied: {path}")  

    def startDrag(self, event):
        index = self.right_tree.currentIndex()
        if not index.isValid():
            return

        path = self.right_model.filePath(index)
        mime_data = QMimeData()
        mime_data.setText(path)

        drag = QDrag(self.right_tree)
        drag.setMimeData(mime_data)
        drag.exec_(Qt.CopyAction)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        target_index = self.right_tree.indexAt(event.pos())
        if not target_index.isValid():
            return
        
        target_path = self.right_model.filePath(target_index)
        source_path = event.mimeData().text()

        if os.path.isdir(target_path):
            shutil.move(source_path, target_path)
            QMessageBox.information(self, "Success", f"Moved {os.path.basename(source_path)} to {target_path}")
        else:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            shutil.copy(source_path, desktop_path)
            QMessageBox.information(self, "Success", f"Copied {os.path.basename(source_path)} to Desktop")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileExplorer()
    window.show()
    sys.exit(app.exec_())
