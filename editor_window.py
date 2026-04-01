import random
import sqlite3
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QDoubleSpinBox, QSpinBox,
                             QPushButton, QComboBox, QTextEdit, QMessageBox,
                             QFileDialog)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class ProductEditorWindow(QDialog):
    def __init__(self, p_id=None):
        super().__init__()
        self.p_id = p_id
        self.setWindowTitle(
            "Редактирование товара" if p_id else "Добавление товара")
        self.setFixedWidth(500)

        # Пути
        self.image_dir = "data"
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

        self.current_photo_name = None
        self.new_photo_path = None
        self.old_photo_to_delete = None

        # Данные для комбобоксов
        self.categories = []
        self.manufacturers = []
        self.suppliers = []

        self.init_ui()
        self.load_lists()

        if self.p_id:
            self.load_product_data()
        else:
            self.id_label.hide()
            self.id_input.hide()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # ID
        self.id_label = QLabel("ID товара:")
        self.id_input = QLineEdit()
        self.id_input.setReadOnly(True)
        layout.addWidget(self.id_label)
        layout.addWidget(self.id_input)

        # Фото и кнопка
        img_layout = QHBoxLayout()
        self.img_preview = QLabel()
        self.img_preview.setFixedSize(300, 200)
        self.img_preview.setStyleSheet("border: 1px solid gray;")
        self.img_preview.setPixmap(QPixmap("data/picture.png").scaled(300, 200,
                                                                      Qt.AspectRatioMode.KeepAspectRatio))

        btn_img = QPushButton("Выбрать фото\n(300x200)")
        btn_img.clicked.connect(self.select_image)

        img_layout.addWidget(self.img_preview)
        img_layout.addWidget(btn_img)
        layout.addLayout(img_layout)

        # Поля
        layout.addWidget(QLabel("Наименование:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Категория:"))
        self.cat_combo = QComboBox()
        layout.addWidget(self.cat_combo)

        layout.addWidget(QLabel("Описание:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(70)
        layout.addWidget(self.desc_input)

        layout.addWidget(QLabel("Производитель:"))
        self.man_combo = QComboBox()
        layout.addWidget(self.man_combo)

        layout.addWidget(QLabel("Поставщик:"))
        self.sup_combo = QComboBox()
        layout.addWidget(self.sup_combo)

        # Числовые поля
        nums = QHBoxLayout()

        v1 = QVBoxLayout();
        v1.addWidget(QLabel("Цена:"));
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 999999);
        nums.addLayout(v1);
        v1.addWidget(self.price_input)

        v2 = QVBoxLayout();
        v2.addWidget(QLabel("Скидка %:"));
        self.disc_input = QSpinBox()
        self.disc_input.setRange(0, 100);
        nums.addLayout(v2);
        v2.addWidget(self.disc_input)

        v3 = QVBoxLayout();
        v3.addWidget(QLabel("Склад:"));
        self.qty_input = QSpinBox()
        self.qty_input.setRange(0, 99999);
        nums.addLayout(v3);
        v3.addWidget(self.qty_input)

        layout.addLayout(nums)

        layout.addWidget(QLabel("Единица измерения:"))
        self.unit_input = QLineEdit("шт.")
        layout.addWidget(self.unit_input)

        # Кнопки
        btns = QHBoxLayout()
        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_save);
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

    def load_lists(self):
        conn = sqlite3.connect('shoe_store.db')
        cur = conn.cursor()

        cur.execute("SELECT id, name FROM categories")
        self.categories = cur.fetchall()
        self.cat_combo.addItems([c[1] for c in self.categories])

        cur.execute("SELECT id, name FROM manufacturers")
        self.manufacturers = cur.fetchall()
        self.man_combo.addItems([m[1] for m in self.manufacturers])

        cur.execute("SELECT id, name FROM suppliers")
        self.suppliers = cur.fetchall()
        self.sup_combo.addItems([s[1] for s in self.suppliers])
        conn.close()

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение",
                                                   "",
                                                   "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.new_photo_path = file_path
            pix = QPixmap(file_path).scaled(300, 200,
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
            self.img_preview.setPixmap(pix)

    def load_product_data(self):
        conn = sqlite3.connect('shoe_store.db')
        cur = conn.cursor()
        cur.execute("""SELECT name, category_id, description, manufacturer_id, supplier_id, 
                              price, discount, quantity, photo_path, id FROM products WHERE id=?""",
                    (self.p_id,))
        res = cur.fetchone()
        conn.close()

        if res:
            self.name_input.setText(res[0])
            self.id_input.setText(str(res[9]))
            # Установка индексов в комбобоксах
            self.cat_combo.setCurrentIndex(next(
                (i for i, c in enumerate(self.categories) if c[0] == res[1]), 0))
            self.desc_input.setPlainText(res[2])
            self.man_combo.setCurrentIndex(next(
                (i for i, m in enumerate(self.manufacturers) if m[0] == res[3]),
                0))
            self.sup_combo.setCurrentIndex(
                next((i for i, s in enumerate(self.suppliers) if s[0] == res[4]),
                     0))
            self.price_input.setValue(float(res[5] if res[5] else 0))

            self.disc_input.setValue(int(res[6] if res[6] else 0))
            self.qty_input.setValue(int(res[7] if res[7] else 0))
            self.current_photo_name = res[8]

            if self.current_photo_name:
                path = f"data/{self.current_photo_name}"
                if os.path.exists(path):
                    self.img_preview.setPixmap(QPixmap(path).scaled(300, 200,
                                                                    Qt.AspectRatioMode.KeepAspectRatio))

    def save(self):
        # Валидация
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Заполните название!")
            return

        # Обработка изображения
        final_photo_name = self.current_photo_name
        if self.new_photo_path:
            ext = os.path.splitext(self.new_photo_path)[1]
            final_photo_name = f"prod_{random.randint(1000, 9999)}{ext}"
            new_dest = os.path.join(self.image_dir, final_photo_name)

            pix = QPixmap(self.new_photo_path).scaled(300, 200,
                                                      Qt.AspectRatioMode.IgnoreAspectRatio,
                                                      Qt.TransformationMode.SmoothTransformation)
            pix.save(new_dest)

            if self.current_photo_name:
                self.old_photo_to_delete = os.path.join(self.image_dir,
                                                        self.current_photo_name)

        # Сохранение в БД
        try:
            conn = sqlite3.connect('shoe_store.db')
            cur = conn.cursor()

            cat_id = self.categories[self.cat_combo.currentIndex()][0]
            man_id = self.manufacturers[self.man_combo.currentIndex()][0]
            sup_id = self.suppliers[self.sup_combo.currentIndex()][0]

            if self.p_id:
                cur.execute("""UPDATE products SET name=?, category_id=?, description=?, 
                               manufacturer_id=?, supplier_id=?, price=?, discount=?, 
                               quantity=?, photo_path=? WHERE id=?""",
                            (self.name_input.text(), cat_id,
                             self.desc_input.toPlainText(),
                             man_id, sup_id, self.price_input.value(),
                             self.disc_input.value(),
                             self.qty_input.value(), final_photo_name,
                             self.p_id))
            else:
                from random import choice
                from string import ascii_uppercase, digits
                art = f"{choice(ascii_uppercase)}{''.join(choice(digits) for _ in range(3))}{choice(ascii_uppercase)}{choice(digits)}"

                cur.execute("""INSERT INTO products (article, name, category_id, description, 
                               manufacturer_id, supplier_id, price, discount, quantity, photo_path) 
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (art, self.name_input.text(), cat_id,
                             self.desc_input.toPlainText(),
                             man_id, sup_id, self.price_input.value(),
                             self.disc_input.value(),
                             self.qty_input.value(), final_photo_name))

            conn.commit()
            conn.close()

            # Удаляем старое фото, если оно было заменено
            if self.old_photo_to_delete and os.path.exists(
                    self.old_photo_to_delete):
                try:
                    os.remove(self.old_photo_to_delete)
                except:
                    pass

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Критическая ошибка БД: {e}")