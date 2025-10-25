import sys
import os
import subprocess
import json
import zipfile
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton, 
                             QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
                             QMessageBox, QFileDialog)
from PyQt6.QtGui import QPixmap, QFont, QCursor, QIcon # Adicionada a importação de QIcon
from PyQt6.QtCore import QSize, Qt

class SubrosaLauncher(QMainWindow):
    def __init__(self):
        super().__init__()

        self.maps_path = "instances"
        self.maps_data = {}

        self.init_ui()
        self.load_styles()
        self.populate_map_list()

    def init_ui(self):
        self.setWindowTitle("Sub Rosa Launcher")
        self.setFixedSize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        try:
            logo_pixmap = QPixmap(os.path.join("assets", "subrosa_logo.png"))
            logo_label = QLabel()
            logo_label.setPixmap(logo_pixmap.scaled(230, 150, Qt.AspectRatioMode.KeepAspectRatio))
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            left_layout.addWidget(logo_label)
        except Exception as e:
            print(f"Aviso: Não foi possível carregar o logo: {e}")

        self.map_list_widget = QListWidget()
        self.map_list_widget.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.map_list_widget.currentItemChanged.connect(self.on_map_select)
        left_layout.addWidget(self.map_list_widget)

        self.import_button = QPushButton("Importar Mapa")
        self.import_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.import_button.setObjectName("importButton")
        self.import_button.clicked.connect(self.import_map_file)
        left_layout.addWidget(self.import_button)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.map_name_label = QLabel("Nome do Mapa")
        self.map_name_label.setObjectName("mapNameLabel")

        self.map_desc_label = QLabel("Selecione um mapa na lista à esquerda para ver seus detalhes.")
        self.map_desc_label.setWordWrap(True)
        self.map_desc_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.map_tags_label = QLabel("")
        self.map_tags_label.setObjectName("mapTagsLabel")
        
        right_layout.addWidget(self.map_name_label)
        right_layout.addWidget(self.map_desc_label, 1)
        right_layout.addWidget(self.map_tags_label)

        button_layout = QHBoxLayout()
        self.options_button = QPushButton("Opções")
        self.options_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.options_button.clicked.connect(self.open_options_file)

        self.delete_button = QPushButton("Deletar Mapa")
        self.delete_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_map)

        self.play_button = QPushButton("Jogar")
        self.play_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.launch_game)
        
        button_layout.addWidget(self.options_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.play_button)
        
        right_layout.addLayout(button_layout)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

    def load_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QLabel {
                color: #FFFFFF;
                font-family: Helvetica;
                font-size: 11pt;
            }
            QLabel#mapNameLabel {
                font-size: 20pt;
                font-weight: bold;
                padding-bottom: 10px;
            }
            QLabel#mapTagsLabel {
                color: grey;
                font-style: italic;
            }
            QListWidget {
                background-color: #000000;
                border: none;
                font-size: 12pt;
            }
            QListWidget:focus {
                outline: none;
            }
            QListWidget::item {
                color: #FFFFFF;
                padding: 8px;
                text-align: center;
            }
            QListWidget::item:hover {
                background-color: #1c1c1c;
            }
            QListWidget::item:selected {
                background-color: #2a2a2a;
                outline: none;
            }
            QPushButton {
                background-color: #1a1a1a;
                color: #FFFFFF;
                border: none;
                padding: 10px 25px;
                font-family: Helvetica;
                font-size: 12pt;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
            }
            QPushButton:focus {
                outline: none;
            }
            QPushButton:disabled {
                background-color: #111111;
                color: #555555;
            }
            QPushButton#importButton {
                font-size: 11pt;
                padding: 8px;
                margin-top: 10px;
            }
            QPushButton#deleteButton {
                background-color: #4d1a1a;
                font-size: 10pt;
            }
            QPushButton#deleteButton:hover {
                background-color: #6e2626;
            }
        """)
    
    def reset_details_panel(self):
        self.map_name_label.setText("Nome do Mapa")
        self.map_desc_label.setText("Selecione um mapa na lista à esquerda para ver seus detalhes.")
        self.map_tags_label.setText("")
        self.play_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def refresh_map_list(self):
        self.map_list_widget.clear()
        self.maps_data.clear()
        self.populate_map_list()
        self.reset_details_panel()

    def delete_map(self):
        current_item = self.map_list_widget.currentItem()
        if not current_item: return

        map_name = current_item.data(Qt.ItemDataRole.UserRole)
        folder = self.maps_data[map_name]["folder"]
        map_dir_path = os.path.join(self.maps_path, folder)

        reply = QMessageBox.question(self, "Confirmar Exclusão", f"Tem certeza que deseja deletar permanentemente o mapa '{map_name}'?\n\nEsta ação não pode ser desfeita.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                shutil.rmtree(map_dir_path)
                QMessageBox.information(self, "Sucesso", f"O mapa '{map_name}' foi deletado.")
                self.refresh_map_list()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível deletar o mapa: {e}")

    def import_map_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Mapa para Importar", "", "Mapas de Subrosa (*.srmap)")
        if not file_path: return
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                if not file_list:
                    QMessageBox.warning(self, "Erro de Importação", "O arquivo .srmap está vazio.")
                    return
                root_folder = file_list[0]
                if not (root_folder.startswith("sr_") and root_folder.endswith('/')):
                    QMessageBox.warning(self, "Erro de Importação", "O arquivo .srmap não tem uma pasta 'sr_*' na raiz.")
                    return
                map_folder_name = os.path.dirname(root_folder)
                destination_path = os.path.join(self.maps_path, map_folder_name)
                if os.path.exists(destination_path):
                    reply = QMessageBox.question(self, "Mapa Existente", f"O mapa '{map_folder_name}' já existe. Deseja substituí-lo?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No: return
                zip_ref.extractall(self.maps_path)
                QMessageBox.information(self, "Sucesso", f"O mapa '{map_folder_name}' foi importado com sucesso!")
                self.refresh_map_list()
        except zipfile.BadZipFile:
            QMessageBox.critical(self, "Erro de Importação", "O arquivo selecionado não é um .srmap válido ou está corrompido.")
        except Exception as e:
            QMessageBox.critical(self, "Erro Inesperado", f"Ocorreu um erro durante a importação: {e}")
    
    def on_map_select(self, current_item, previous_item):
        if not current_item:
            self.reset_details_panel()
            return
        map_name = current_item.data(Qt.ItemDataRole.UserRole)
        map_info = self.maps_data[map_name]
        self.map_name_label.setText(map_name)
        self.map_desc_label.setText(map_info.get("description", "Sem descrição."))
        tags = map_info.get("tags", [])
        tags_text = "Tags: " + (", ".join(tags) if tags else "Nenhuma")
        self.map_tags_label.setText(tags_text)
        self.play_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def populate_map_list(self):
        if not os.path.exists(self.maps_path):
            os.makedirs(self.maps_path)
        map_folders = sorted([d for d in os.listdir(self.maps_path) if os.path.isdir(os.path.join(self.maps_path, d)) and d.startswith("sr_")])
        for folder_name in map_folders:
            json_path = os.path.join(self.maps_path, folder_name, "map.json")
            if not os.path.exists(json_path): continue
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                map_name = data.get("name", folder_name)
                self.maps_data[map_name] = {"folder": folder_name, **data}
                item = QListWidgetItem(map_name)
                item.setData(Qt.ItemDataRole.UserRole, map_name) 
                self.map_list_widget.addItem(item)
    
    def launch_game(self):
        current_item = self.map_list_widget.currentItem()
        if not current_item: return
        map_name = current_item.data(Qt.ItemDataRole.UserRole)
        folder = self.maps_data[map_name]["folder"]
        map_path = os.path.join(self.maps_path, folder)
        executable_path = os.path.join(map_path, "subrosa.exe")
        if os.path.exists(executable_path):
            subprocess.Popen(executable_path, cwd=map_path)
            self.close()
        else:
            QMessageBox.critical(self, "Erro", f"'subrosa.exe' não encontrado em '{map_path}'.")

    def open_options_file(self):
        try:
            home_dir = os.path.expanduser('~')
            config_path = os.path.join(home_dir, 'Documents', 'Sub Rosa', 'conf24.txt')
            if os.path.exists(config_path):
                if sys.platform == "win32": os.startfile(config_path)
                elif sys.platform == "darwin": subprocess.call(["open", config_path])
                else: subprocess.call(["xdg-open", config_path])
            else:
                QMessageBox.critical(self, "Erro", f"Arquivo de configuração não encontrado:\n{config_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível abrir o arquivo: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # --- ADICIONADO: Lógica do Ícone ---
    try:
        icon_path = os.path.join("assets", "icon.png")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        else:
            print("Aviso: 'assets/icon.png' não encontrado. Usando ícone padrão.")
    except Exception as e:
        print(f"Não foi possível carregar o ícone: {e}")
    # ------------------------------------

    window = SubrosaLauncher()
    window.show()
    sys.exit(app.exec())
