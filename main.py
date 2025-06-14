from PyQt6.QtWidgets import *
from PyQt6.QtGui import QCursor, QIcon, QPainter, QColor, QPen, QBrush, QAction
from PyQt6.QtCore import Qt, QSize, QRect, QPoint
import sys, os, json
from paths import *
from utils import get_cache_folder_for_url

from widgets import PlusButton, AddLinkWindow, CategoryCard, CategoryLinksWindow

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stashly - Smart Link Manager")
        self.resize(1400, 800)

        # Layout for main screen
        self.main_layout = QVBoxLayout(self)

        # Grid layout for category cards inside a scroll area
        self.category_grid = QGridLayout()
        self.category_grid.setSpacing(20)
        self.category_grid.setContentsMargins(20, 20, 20, 20)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_content.setLayout(self.category_grid)
        scroll_area.setWidget(scroll_content)

        self.main_layout.addWidget(scroll_area)

        # Create the plus button
        self.plus_button = PlusButton(self)
        self.update_plus_button_position()

        self.plus_button.clicked.connect(self.show_add_link_window)

        self.load_categories()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_plus_button_position()

    def update_plus_button_position(self):
        margin = 30
        x = self.width() - self.plus_button.width() - margin
        y = self.height() - self.plus_button.height() - margin
        self.plus_button.move(x, y)

    def show_add_link_window(self):
        self.add_window = AddLinkWindow()
        self.add_window.link_saved.connect(self.reload_categories)
        self.add_window.move(
            self.geometry().center() - self.add_window.rect().center()
        )
        self.add_window.show()

    def load_categories(self):
        file_path = get_data_file_path()
        if not os.path.exists(file_path):
            return

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print("Error loading categories:", e)
            return

        categories = set()
        for entry in data:
            if cat := entry.get("category", "").strip():
                categories.add(cat)

        # Populate grid
        for i, category in enumerate(sorted(categories)):
            row, col = divmod(i, 4)
            card = CategoryCard(category)  # Can add icon support later
            card.clicked.connect(self.open_category_links)
            card.rightclicked.connect(self.show_category_context_menu)
            self.category_grid.addWidget(card, row, col)
    
    def show_category_context_menu(self, category_name):
        menu = QMenu(self)

        rename_action = QAction("Rename", self)
        delete_action = QAction("Delete", self)
        icon_action = QAction("Change Icon", self)

        menu.addAction(rename_action)
        menu.addAction(delete_action)
        menu.addAction(icon_action)

        action = menu.exec(QCursor.pos())

        if action == rename_action:
            self.rename_category(category_name)
        elif action == delete_action:
            self.delete_category(category_name)
        elif action == icon_action:
            self.change_icon_for_category(category_name)

    def rename_category(self, category_name):
        new_name, ok = QInputDialog.getText(self, "Rename Category", "Enter new name:", text=category_name)
        
        if not (ok and new_name and new_name.strip()):
            return  # Cancelled or invalid
        
        if new_name == category_name:
            return
        
        # === Step 1: Update data file ===
        file_path = get_data_file_path()
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", "Data file not found")
            return
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            updated = False
            for entry in data:
                if entry.get("category") == category_name:
                    entry["category"] = new_name
                    updated = True
            
            if updated:
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rename category: {e}")
            return
        
        # === Step 2: Update icon mapping ===
        icon_mapping = load_icon_mapping()
        if category_name in icon_mapping:
            icon_path = icon_mapping[category_name]
            icon_mapping[new_name] = icon_path
            del icon_mapping[category_name]
            save_icon_mapping(icon_mapping)
        
        # === Step 3: Rename copied icon file if needed ===
        icon_dir = get_icons_dir()
        for ext in [".png", ".jpg", ".jpeg", ".webp"]:
            old_icon_file = os.path.join(icon_dir, f"{slugify(category_name)}{ext}")
            if os.path.exists(old_icon_file):
                new_icon_file = os.path.join(icon_dir, f"{slugify(new_name)}{ext}")
                try:
                    os.rename(old_icon_file, new_icon_file)
                    # Update icon mapping to new path
                    icon_mapping[new_name] = new_icon_file
                    save_icon_mapping(icon_mapping)
                except Exception as e:
                    print("Warning: Couldn't rename icon file:", e)
                break

        
        # === Step 4: Reload UI ===
        self.reload_categories()

        QMessageBox.information(self, "Category Renamed", f"'{category_name}' was renamed to '{new_name}' successfully.")

    def delete_category(self, category_name):
        confirm = QMessageBox.question(self, "Delete Category",
            f"Are you sure you want to delete '{category_name}'?\nAll links under this category will be removed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        # === Step 1: Delete from data file ===
        file_path = get_data_file_path()
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Get URLs of links to be deleted
                links_to_delete = [entry for entry in data if entry.get("category") == category_name]
                new_data = [entry for entry in data if entry.get("category") != category_name]

                # Delete cache for each URL
                for link in links_to_delete:
                    url = link.get("url", "")
                    cache_folder = get_cache_folder_for_url(url)
                    if os.path.exists(cache_folder):
                        try:
                            shutil.rmtree(cache_folder)
                        except Exception as e:
                            print(f"Warning: Failed to delete cache for {url}: {e}")

                with open(file_path, 'w') as f:
                    json.dump(new_data, f, indent=2)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete category from data: {e}")
                return

        # === Step 2: Remove icon from mapping ===
        icon_mapping = load_icon_mapping()
        icon_path = None
        if category_name in icon_mapping:
            icon_path = icon_mapping.pop(category_name)
            save_icon_mapping(icon_mapping)

        # === Step 3: Delete copied icon file (from .stashly/icons) ===
        icon_dir = get_icons_dir()
        deleted_icon = False

        for ext in [".png", ".jpg", ".jpeg", ".webp"]:
            icon_file = os.path.join(icon_dir, f"{slugify(category_name)}{ext}")
            if os.path.exists(icon_file):
                try:
                    os.remove(icon_file)
                    deleted_icon = True
                    break
                except Exception as e:
                    print(f"Warning: Failed to delete icon file: {e}")

        # === Step 4: Reload UI ===
        self.reload_categories()

        # === Step 5: Show confirmation ===
        QMessageBox.information(
            self,
            "Category Deleted",
            f"Category '{category_name}' and its links {'and icon' if deleted_icon or icon_path else ''} have been deleted."
        )

    def change_icon_for_category(self, category_name):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            icon_dir = get_icons_dir()
            mapping = load_icon_mapping()

            ext = os.path.splitext(file_path)[1]
            icon_filename = f"{slugify(category_name)}{ext}"
            destination = os.path.join(icon_dir, icon_filename)

            try:
                shutil.copyfile(file_path, destination)
                mapping[category_name] = destination
                save_icon_mapping(mapping)
                QMessageBox.information(self, "Success", f"Icon updated for '{category_name}'.")

                # Trigger UI reload
                self.reload_categories()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to set icon: {str(e)}")


    def reload_categories(self):
        # Step 1: Clear current category list
        for i in reversed(range(self.category_grid.count())):
            widget = self.category_grid.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Step 2: Re-load categories from disk
        self.load_categories()

    def open_category_links(self, category_name):
        self.link_window = CategoryLinksWindow(category_name)
        self.link_window.show()

if __name__ == "__main__":

    get_cache_dir()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
