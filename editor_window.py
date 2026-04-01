import sqlite3
import random
import string
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QDoubleSpinBox, QSpinBox,
                             QPushButton, QComboBox, QTextEdit, QMessageBox)


class ProductEditorWindow(QDialog):
    def __init__(self, p_id=None):
        super().__init__()
        self.p_id = p_id
        self.setWindowTitle(
            "Редактирование товара" if p_id else "Добавление нового товара")
        self.setFixedWidth(450)

        # Хранилища для ID из комбобоксов
        self.categories = []
        self.manufacturers = []
        self.suppliers = []

        self.init_ui()
        self.load_lists()  # Сначала загружаем списки для выбора

        if self.p_id:
            self.load_product_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 1. Наименование (Что такое)
        layout.addWidget(QLabel("Наименование товара (Что такое):"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # 2. Категория (Какая обувь)
        layout.addWidget(QLabel("Категория (Какая обувь):"))
        self.cat_combo = QComboBox()
        layout.addWidget(self.cat_combo)

        # 3. Описание
        layout.addWidget(QLabel("Описание товара:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        layout.addWidget(self.desc_input)

        # 4. Производитель
        layout.addWidget(QLabel("Производитель:"))
        self.man_combo = QComboBox()
        layout.addWidget(self.man_combo)

        # 5. Поставщик
        layout.addWidget(QLabel("Поставщик:"))
        self.sup_combo = QComboBox()
        layout.addWidget(self.sup_combo)

        # Слой для цифровых данных (Цена, Скидка, Кол-во)
        nums_layout = QHBoxLayout()

        v1 = QVBoxLayout()
        v1.addWidget(QLabel("Цена:"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1000000)
        v1.addWidget(self.price_input)
        nums_layout.addLayout(v1)

        v2 = QVBoxLayout()
        v2.addWidget(QLabel("Скидка (%):"))
        self.disc_input = QSpinBox()
        v2.addWidget(self.disc_input)
        nums_layout.addLayout(v2)

        v3 = QVBoxLayout()
        v3.addWidget(QLabel("На складе:"))
        self.qty_input = QSpinBox()
        self.qty_input.setRange(0, 10000)
        self.qty_input.setValue(0)  # По умолчанию 0, как ты просила
        v3.addWidget(self.qty_input)
        nums_layout.addLayout(v3)

        layout.addLayout(nums_layout)

        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.setStyleSheet("background-color: #7FFF00; font-weight: bold;")
        save_btn.clicked.connect(self.save)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def load_lists(self):
        """Загружает данные в выпадающие списки из БД"""
        conn = sqlite3.connect('shoe_store.db')
        cur = conn.cursor()

        # Загружаем категории
        cur.execute("SELECT id, name FROM categories")
        self.categories = cur.fetchall()
        self.cat_combo.addItems([c[1] for c in self.categories])

        # Загружаем производителей
        cur.execute("SELECT id, name FROM manufacturers")
        self.manufacturers = cur.fetchall()
        self.man_combo.addItems([m[1] for m in self.manufacturers])

        # Загружаем поставщиков
        cur.execute("SELECT id, name FROM suppliers")
        self.suppliers = cur.fetchall()
        self.sup_combo.addItems([s[1] for s in self.suppliers])

        conn.close()

    @staticmethod
    def generate_article():
        letter1 = random.choice(string.ascii_uppercase)
        digits = "".join(random.choices(string.digits, k=3))
        letter2 = random.choice(string.ascii_uppercase)
        last_digit = random.choice(string.digits)
        return f"{letter1}{digits}{letter2}{last_digit}"

    def save(self):
        # Получаем выбранные ID
        cat_id = self.categories[self.cat_combo.currentIndex()][0]
        man_id = self.manufacturers[self.man_combo.currentIndex()][0]
        sup_id = self.suppliers[self.sup_combo.currentIndex()][0]

        name = self.name_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        price = self.price_input.value()
        disc = self.disc_input.value()
        qty = self.qty_input.value()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Нужно хотя бы название!")
            return

        try:
            conn = sqlite3.connect('shoe_store.db')
            cur = conn.cursor()

            if self.p_id:
                cur.execute("""UPDATE products SET 
                               name=?, description=?, price=?, discount=?, quantity=?,
                               category_id=?, manufacturer_id=?, supplier_id=?
                               WHERE id=?""",
                            (name, desc, price, disc, qty, cat_id, man_id,
                             sup_id, self.p_id))
            else:
                new_art = self.generate_article()
                cur.execute("""INSERT INTO products 
                               (article, name, description, price, discount, quantity, 
                                category_id, manufacturer_id, supplier_id) 
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (new_art, name, desc, price, disc, qty, cat_id,
                             man_id, sup_id))

            conn.commit()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не спасли товар: {e}")

    def load_product_data(self):
        """Загрузка существующих данных товара для редактирования"""
        try:
            conn = sqlite3.connect('shoe_store.db')
            cur = conn.cursor()

            # Достаем все нужные поля по ID
            cur.execute("""SELECT name, description, price, discount, quantity, 
                                  category_id, manufacturer_id, supplier_id 
                           FROM products WHERE id=?""", (self.p_id,))
            res = cur.fetchone()
            conn.close()

            if res:
                # 1. Заполняем простые поля
                self.name_input.setText(str(res[0]))
                self.desc_input.setPlainText(str(res[1]))
                self.price_input.setValue(float(res[2]))
                self.disc_input.setValue(int(res[3]))
                self.qty_input.setValue(int(res[4]))

                # 2. Устанавливаем значения в комбобоксах
                # Ищем индекс ID в наших списках, которые мы загрузили в load_lists
                cat_idx = next(
                    (i for i, c in enumerate(self.categories) if c[0] == res[5]),
                    0)
                self.cat_combo.setCurrentIndex(cat_idx)

                man_idx = next((i for i, m in enumerate(self.manufacturers) if
                                m[0] == res[6]), 0)
                self.man_combo.setCurrentIndex(man_idx)

                sup_idx = next(
                    (i for i, s in enumerate(self.suppliers) if s[0] == res[7]),
                    0)
                self.sup_combo.setCurrentIndex(sup_idx)

        except Exception as e:
            print(f"Ошибка при загрузке данных товара: {e}")