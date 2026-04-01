import sqlite3
from PyQt6.QtWidgets import (QScrollArea, QLineEdit,
                             QComboBox)

from styles import STYLE_SHEET
from editor_window import ProductEditorWindow

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QWidget, \
    QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class ProductWidget(QFrame):
    def __init__(self, product_data, role, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.role = role

        # Распаковка (ID, Артикул, Название, Описание, Цена, Скидка, Кол-во, Фото, Категория, Производитель)
        (self.p_id, self.art, self.name, self.desc, self.price,
         self.discount, self.quantity, self.photo, self.cat_name,
         self.man_name, self.sup_name) = product_data

        self.setObjectName("productCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMinimumHeight(180)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)

        # Фото
        self.img_label = QLabel()
        self.img_label.setFixedSize(130, 130)
        pix = QPixmap(f"data/{self.photo}") if self.photo else QPixmap(
            "data/picture.png")
        if pix.isNull(): pix = QPixmap("data/picture.png")
        self.img_label.setPixmap(
            pix.scaled(130, 130, Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation))
        main_layout.addWidget(self.img_label)

        # Информация
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Категория и Наименование
        info_layout.addWidget(QLabel(
            f"<span style='color: #555'>{self.cat_name}</span> | <b>{self.name}</b>"))

        # Описание
        desc_lbl = QLabel(f"<b>Описание товара:</b> {self.desc}")
        desc_lbl.setWordWrap(True)
        info_layout.addWidget(desc_lbl)

        # Производитель и Поставщик
        info_layout.addWidget(QLabel(f"<b>Производитель:</b> {self.man_name}"))
        info_layout.addWidget(QLabel(
            f"<b>Поставщик:</b> {self.sup_name if self.sup_name else 'Не указан'}"))

        # Цена
        self.price_label = QLabel()
        if self.discount > 0:
            new_price = self.price * (1 - self.discount / 100)
            self.price_label.setText(
                f"<b>Цена:</b> <span style='color: red; text-decoration: line-through;'>{self.price:.2f} руб.</span> "
                f"<b>{new_price:.2f} руб.</b>"
            )
        else:
            self.price_label.setText(f"<b>Цена:</b> {self.price:.2f} руб.")
        info_layout.addWidget(self.price_label)

        # Единица измерения и Количество
        info_layout.addWidget(QLabel(
            f"<b>Единица измерения:</b> шт. | <b>Количество на складе:</b> {self.quantity}"))

        main_layout.addWidget(info_container, stretch=1)

        # Скидка слева
        self.discount_box = QLabel(f"{self.discount}%")
        self.discount_box.setFixedSize(60, 60)
        self.discount_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.discount_box.setStyleSheet(
            "border: 1px solid black; font-weight: bold; font-size: 16px;")
        main_layout.addWidget(self.discount_box)

        # Кнопки админа
        if self.role == "Администратор":
            btns = QVBoxLayout()
            btn_edit = QPushButton("✎")
            btn_edit.setFixedSize(35, 35)
            btn_edit.clicked.connect(
                lambda: self.parent_window.open_editor(self.p_id))

            btn_del = QPushButton("✕")
            btn_del.setFixedSize(35, 35)
            btn_del.setStyleSheet("background-color: #00FA9A;")
            btn_del.clicked.connect(self.delete_product)

            btns.addWidget(btn_edit)
            btns.addWidget(btn_del)
            main_layout.addLayout(btns)

        self.apply_styles()

    def apply_styles(self):
        if self.quantity == 0:
            self.setStyleSheet("background-color: #ADD8E6;")
        elif self.discount > 15:
            self.setStyleSheet("background-color: #2E8B57; color: white;")
            self.price_label.setStyleSheet("color: white;")
            self.discount_box.setStyleSheet(
                "border: 1px solid white; color: white; font-weight: bold;")

    def delete_product(self):
        """Удаление товара"""
        import sqlite3
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(self, 'Удаление',
                                     f"Вы действительно хотите удалить {self.name}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect('shoe_store.db')
                cur = conn.cursor()

                cur.execute(
                    "SELECT COUNT(*) FROM order_items WHERE product_id = ?",
                    (self.p_id,))
                if cur.fetchone()[0] > 0:
                    QMessageBox.warning(self, "Ошибка",
                                        "Нельзя удалить товар, так как он есть в заказах!")
                else:
                    cur.execute("DELETE FROM products WHERE id = ?",
                                (self.p_id,))
                    conn.commit()
                    QMessageBox.information(self, "Успех",
                                            "Товар успешно удален.")
                    self.parent_window.load_products()

                conn.close()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД",
                                     f"Произошла ошибка при удалении: {e}")


class ProductListWindow(QWidget):
    def __init__(self, user_fio="Гость", role_name="Гость"):
        super().__init__()
        self.role = role_name
        self.setWindowTitle(f"ООО «Обувь» — {role_name}")
        self.resize(1000, 750)
        self.setStyleSheet(STYLE_SHEET)

        main_layout = QVBoxLayout(self)

        # Шапка (Выход, Добавление, ФИО)
        header = QHBoxLayout()
        btn_back = QPushButton("Выход")
        btn_back.clicked.connect(self.go_back)
        header.addWidget(btn_back)

        if self.role == "Администратор":
            btn_add = QPushButton("Добавить товар")
            btn_add.setObjectName("primaryButton")
            btn_add.clicked.connect(lambda: self.open_editor())
            header.addWidget(btn_add)

        header.addStretch()
        header.addWidget(
            QLabel(f"Пользователь: <b>{user_fio}</b> ({role_name})"))
        main_layout.addLayout(header)

        # Пануль управления
        self.controls_layout = QHBoxLayout()

        if self.role in ["Менеджер", "Администратор"]:
            lbl_search = QLabel("Поиск:")
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Поиск по названию...")
            self.search_input.textChanged.connect(self.load_products)

            lbl_sort = QLabel("Сортировка:")
            self.sort_combo = QComboBox()
            self.sort_combo.addItems(
                ["Без сортировки", "Кол-во (возр.)", "Кол-во (убыв.)"])
            self.sort_combo.currentIndexChanged.connect(self.load_products)

            lbl_filter = QLabel("Производитель:")
            self.filter_combo = QComboBox()
            self.fill_manufacturers()
            self.filter_combo.currentIndexChanged.connect(self.load_products)

            self.controls_layout.addWidget(lbl_search)
            self.controls_layout.addWidget(self.search_input)
            self.controls_layout.addWidget(lbl_sort)
            self.controls_layout.addWidget(self.sort_combo)
            self.controls_layout.addWidget(lbl_filter)
            self.controls_layout.addWidget(self.filter_combo)
        else:
            self.search_input = QLineEdit()
            self.sort_combo = QComboBox()
            self.filter_combo = QComboBox()

        main_layout.addLayout(self.controls_layout)

        # Список товаров
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)

        self.load_products()

    def fill_manufacturers(self):
        """Заполняет выпадающий список производителями из БД"""
        self.filter_combo.clear()
        self.filter_combo.addItem("Все производители")
        try:
            conn = sqlite3.connect('shoe_store.db')
            cur = conn.cursor()
            cur.execute("SELECT name FROM manufacturers")
            for row in cur.fetchall():
                self.filter_combo.addItem(row[0])
            conn.close()
        except Exception as e:
            print(f"Ошибка загрузки производителей: {e}")

    def load_products(self):
        """Загрузка данных с учетом Поиска, Фильтра и Сортировки"""
        # Очистка текущего списка
        for i in reversed(range(self.list_layout.count())):
            widget = self.list_layout.itemAt(i).widget()
            if widget: widget.setParent(None)

        try:
            try:
                conn = sqlite3.connect('shoe_store.db')
                cur = conn.cursor()

                # Базовый запрос
                query = '''SELECT p.id, p.article, p.name, p.description, p.price, 
                                      p.discount, p.quantity, p.photo_path, 
                                      c.name, m.name, s.name 
                               FROM products p
                               LEFT JOIN categories c ON p.category_id = c.id
                               LEFT JOIN manufacturers m ON p.manufacturer_id = m.id
                               LEFT JOIN suppliers s ON p.supplier_id = s.id
                               WHERE 1=1'''

                params = []

                # Логика поиска
                search_text = self.search_input.text().strip()
                if self.role in ["Менеджер", "Администратор"] and search_text:
                    query += " AND (LOWER(p.name) LIKE LOWER(?) OR LOWER(p.description) LIKE LOWER(?) OR LOWER(p.article) LIKE LOWER(?))"
                    term = f"%{search_text}%"
                    params.extend([term, term, term])

                # Логика фильтрации
                if self.role in ["Менеджер",
                                 "Администратор"] and self.filter_combo.currentText() != "Все производители":
                    query += " AND m.name = ?"
                    params.append(self.filter_combo.currentText())

                # Логика сортировки
                if self.role in ["Менеджер", "Администратор"]:
                    if self.sort_combo.currentIndex() == 1:
                        query += " ORDER BY p.quantity ASC"
                    elif self.sort_combo.currentIndex() == 2:
                        query += " ORDER BY p.quantity DESC"

                cur.execute(query, params)
                rows = cur.fetchall()

                # Очищаем список перед отрисовкой
                for i in reversed(range(self.list_layout.count())):
                    widget = self.list_layout.itemAt(i).widget()
                    if widget: widget.setParent(None)

                for p in rows:
                    self.list_layout.addWidget(ProductWidget(p, self.role, self))

                conn.close()

            except Exception as e:
                print(f"Ошибка load_products: {e}")
        except Exception as e:
            print(f"Ошибка load_products: {e}")

    def open_editor(self, p_id=None):
        dlg = ProductEditorWindow(p_id)
        if dlg.exec():
            self.load_products()

    def go_back(self):
        from main import LoginWindow

        self.login_win = LoginWindow()
        self.login_win.show()

        self.close()
