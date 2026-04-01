import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox,
                             QHBoxLayout)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
from styles import STYLE_SHEET
from product_list import ProductListWindow

def trap_errors(exctype, value, traceback):
    print(f"Критическая ошибка: {value}")
    sys.__excepthook__(exctype, value, traceback)
    sys.exit(1)

sys.excepthook = trap_errors

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ООО «Обувь» — Авторизация")
        self.setFixedSize(350, 450)
        self.setStyleSheet(STYLE_SHEET)

        # Главный виджет и слой
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Установка иконки приложения
        self.setWindowIcon(
            QIcon("data/Icon.png"))  # Проверьте название файла иконки

        # Логотип
        self.logo_label = QLabel()
        # Используем путь к вашему логотипу
        pixmap = QPixmap("data/Icon.png")
        if not pixmap.isNull():
            # Масштабируем, сохраняя пропорции (требование ТЗ)
            self.logo_label.setPixmap(
                pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation))
        else:
            self.logo_label.setText("ЛОГОТИП (файл не найден)")

        layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        # Поля ввода
        layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        layout.addWidget(self.login_input)

        layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        # Кнопки
        self.btn_login = QPushButton("Войти")
        self.btn_login.clicked.connect(self.auth)
        layout.addWidget(self.btn_login)

        self.btn_guest = QPushButton("Войти как гость")
        self.btn_guest.clicked.connect(self.enter_as_guest)
        layout.addWidget(self.btn_guest)

    def auth(self):
        login = self.login_input.text()
        password = self.password_input.text()

        conn = sqlite3.connect('shoe_store.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT users.fio, roles.name 
            FROM users 
            JOIN roles ON users.role_id = roles.id 
            WHERE login = ? AND password = ?
        ''', (login, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            fio, role = user
            self.product_win = ProductListWindow(fio, role)
            self.product_win.show()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def enter_as_guest(self):
        self.product_win = ProductListWindow("Гость", "Гость")
        self.product_win.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        window = LoginWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Критическая ошибка: {e}")
