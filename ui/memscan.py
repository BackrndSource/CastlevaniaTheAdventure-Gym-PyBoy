from pyboy import PyBoy
from pyboy.api.memory_scanner import ScanMode, StandardComparisonType, DynamicComparisonType

import threading
import time

from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QWidget,
    QMainWindow,
    QGridLayout,
    QLineEdit,
    QHBoxLayout,
    QSpinBox,
    QLabel,
    QVBoxLayout,
)
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QFont

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
    QButtonGroup,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHeaderView,
    QStyledItemDelegate,
)


class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter


class MemoryScanWindow(QMainWindow):
    def __init__(self, pyboy):
        super().__init__()
        self.setWindowTitle("PyBoy Memory Scanner GUI")

        self.pyboy = pyboy

        self.game_running = False
        self.game_thread = None

        self.track_running = False
        self.track_thread = None

        self._track_memory_table_current_edit_item = None

        self._init_widgets()
        # self._init_pyboy()

    def _init_widgets(self):
        """Inicia la interfaz gráfica"""

        hex_font = QFont()
        hex_font.setCapitalization(QFont.Capitalization.AllUppercase)

        pagelayout = QVBoxLayout()
        header_layout = QHBoxLayout()
        footer_layout = QHBoxLayout()

        memory_scan_layout = QHBoxLayout()
        memory_scan_form_layout = QVBoxLayout()
        memory_scan_form_input_layout = QGridLayout()
        memory_scan_form_buttons_layout = QHBoxLayout()
        memory_scan_result_layout = QVBoxLayout()
        memory_scan_result_table_layout = QVBoxLayout()
        memory_scan_result_buttons_layout = QHBoxLayout()

        memory_scan_layout.addLayout(memory_scan_form_layout)
        memory_scan_layout.addLayout(memory_scan_result_layout)
        memory_scan_form_layout.addLayout(memory_scan_form_input_layout)
        memory_scan_form_layout.addLayout(memory_scan_form_buttons_layout)
        memory_scan_result_layout.addLayout(memory_scan_result_table_layout)
        memory_scan_result_layout.addLayout(memory_scan_result_buttons_layout)

        pagelayout.addLayout(header_layout)
        pagelayout.addLayout(memory_scan_layout)
        pagelayout.addLayout(footer_layout)

        self.play_game_button = QPushButton("Start Game")
        self.play_game_button.clicked.connect(self.start_game)

        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)

        header_layout.addWidget(self.play_game_button)
        header_layout.addWidget(exit_button)

        value_input_label = QLabel("Value")
        self.value_input = QSpinBox()
        self.value_input.setFont(hex_font)
        self.value_input.setMaximum(255)

        self.value_input_hex_checkbox = QCheckBox("Hex")

        @Slot()
        def _setValueInputIntegerBase():
            self.value_input.setDisplayIntegerBase(16 if self.value_input_hex_checkbox.isChecked() else 10)

        self.value_input_hex_checkbox.checkStateChanged.connect(_setValueInputIntegerBase)

        start_addr_input_label = QLabel("Start address")
        self.start_addr_input = QLineEdit("0x0000")

        end_addr_input_label = QLabel("End address")
        self.end_addr_input = QLineEdit("0xFFFF")

        # Value type (scan mode)
        value_type_input_label = QLabel("Type")
        value_type_int = QRadioButton("Integer")
        value_type_bcd = QRadioButton("BCD")
        value_type_int.setChecked(True)

        self.value_type_input_group = QButtonGroup()
        self.value_type_input_group.addButton(value_type_int, ScanMode.INT.value)
        self.value_type_input_group.addButton(value_type_bcd, ScanMode.BCD.value)

        value_type_input_layout = QVBoxLayout()
        value_type_input_layout.addWidget(value_type_int)
        value_type_input_layout.addWidget(value_type_bcd)

        value_type_input_widget = QWidget()
        value_type_input_widget.setLayout(value_type_input_layout)

        # Standard comparisson type

        standard_comparison_type_input_label = QLabel("Scan for")
        standard_comparison_type_exact = QRadioButton("Exact")
        standard_comparison_type_gt = QRadioButton("Greather than")
        standard_comparison_type_gte = QRadioButton("Greather than or equal")
        standard_comparison_type_lt = QRadioButton("Less than")
        standard_comparison_type_lte = QRadioButton("Less than or equal")
        standard_comparison_type_exact.setChecked(True)

        self.standard_comparison_type_input_group = QButtonGroup()
        self.standard_comparison_type_input_group.addButton(
            standard_comparison_type_exact, StandardComparisonType.EXACT.value
        )
        self.standard_comparison_type_input_group.addButton(
            standard_comparison_type_gt, StandardComparisonType.GREATER_THAN.value
        )
        self.standard_comparison_type_input_group.addButton(
            standard_comparison_type_gte, StandardComparisonType.GREATER_THAN_OR_EQUAL.value
        )
        self.standard_comparison_type_input_group.addButton(
            standard_comparison_type_lt, StandardComparisonType.LESS_THAN.value
        )
        self.standard_comparison_type_input_group.addButton(
            standard_comparison_type_lte, StandardComparisonType.LESS_THAN_OR_EQUAL.value
        )

        standard_comparison_type_input_layout = QVBoxLayout()
        standard_comparison_type_input_layout.addWidget(standard_comparison_type_exact)
        standard_comparison_type_input_layout.addWidget(standard_comparison_type_gt)
        standard_comparison_type_input_layout.addWidget(standard_comparison_type_gte)
        standard_comparison_type_input_layout.addWidget(standard_comparison_type_lt)
        standard_comparison_type_input_layout.addWidget(standard_comparison_type_lte)

        standard_comparison_type_input_widget = QWidget()
        standard_comparison_type_input_widget.setLayout(standard_comparison_type_input_layout)

        # Dynamic comparisson type

        dynamic_comparison_type_input_label = QLabel("Re-scan")
        dynamic_comparison_type_match = QRadioButton("Match")
        dynamic_comparison_type_increased = QRadioButton("Increased")
        dynamic_comparison_type_decreased = QRadioButton("Decreased")
        dynamic_comparison_type_changed = QRadioButton("Changed")
        dynamic_comparison_type_unchanged = QRadioButton("Unchanged")
        dynamic_comparison_type_match.setChecked(True)

        self.dynamic_comparison_type_input_group = QButtonGroup()
        self.dynamic_comparison_type_input_group.addButton(
            dynamic_comparison_type_match, DynamicComparisonType.MATCH.value
        )
        self.dynamic_comparison_type_input_group.addButton(
            dynamic_comparison_type_increased, DynamicComparisonType.INCREASED.value
        )
        self.dynamic_comparison_type_input_group.addButton(
            dynamic_comparison_type_decreased, DynamicComparisonType.DECREASED.value
        )
        self.dynamic_comparison_type_input_group.addButton(
            dynamic_comparison_type_changed, DynamicComparisonType.CHANGED.value
        )
        self.dynamic_comparison_type_input_group.addButton(
            dynamic_comparison_type_unchanged, DynamicComparisonType.UNCHANGED.value
        )

        dynamic_comparison_type_input_layout = QVBoxLayout()
        dynamic_comparison_type_input_layout.addWidget(dynamic_comparison_type_match)
        dynamic_comparison_type_input_layout.addWidget(dynamic_comparison_type_increased)
        dynamic_comparison_type_input_layout.addWidget(dynamic_comparison_type_decreased)
        dynamic_comparison_type_input_layout.addWidget(dynamic_comparison_type_changed)
        dynamic_comparison_type_input_layout.addWidget(dynamic_comparison_type_unchanged)

        dynamic_comparison_type_input_widget = QWidget()
        dynamic_comparison_type_input_widget.setLayout(dynamic_comparison_type_input_layout)

        memory_scan_form_input_layout.addWidget(value_input_label, 0, 0)
        memory_scan_form_input_layout.addWidget(self.value_input, 0, 1)
        memory_scan_form_input_layout.addWidget(self.value_input_hex_checkbox, 0, 2)

        memory_scan_form_input_layout.addWidget(start_addr_input_label, 1, 0)
        memory_scan_form_input_layout.addWidget(self.start_addr_input, 1, 1)

        memory_scan_form_input_layout.addWidget(end_addr_input_label, 2, 0)
        memory_scan_form_input_layout.addWidget(self.end_addr_input, 2, 1)

        memory_scan_form_input_layout.addWidget(value_type_input_label, 3, 0)
        memory_scan_form_input_layout.addWidget(value_type_input_widget, 3, 1)

        memory_scan_form_input_layout.addWidget(standard_comparison_type_input_label, 4, 0)
        memory_scan_form_input_layout.addWidget(standard_comparison_type_input_widget, 4, 1)

        memory_scan_form_input_layout.addWidget(dynamic_comparison_type_input_label, 5, 0)
        memory_scan_form_input_layout.addWidget(dynamic_comparison_type_input_widget, 5, 1)

        scan_memory_button = QPushButton("New scan")
        scan_memory_button.clicked.connect(self.scan_memory)

        rescan_memory_button = QPushButton("Re-scan")
        rescan_memory_button.clicked.connect(self.rescan_memory)

        memory_scan_form_buttons_layout.addWidget(scan_memory_button)
        memory_scan_form_buttons_layout.addWidget(rescan_memory_button)

        self.scan_memory_result_table = QTableWidget(0, 3)
        self.scan_memory_result_table.setHorizontalHeaderLabels(["Address", "Value", "Value(hex)"])
        self.scan_memory_result_table.verticalHeader().hide()
        self.scan_memory_result_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.scan_memory_result_table.setColumnWidth(0, 80)
        self.scan_memory_result_table.setColumnWidth(1, 80)
        self.scan_memory_result_table.setColumnWidth(2, 80)
        self.scan_memory_result_table.setMinimumWidth(80 * 3)

        scan_memory_result_table_header = self.scan_memory_result_table.horizontalHeader()
        scan_memory_result_table_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        scan_memory_result_table_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        scan_memory_result_table_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.scan_memory_result_table.setItemDelegateForColumn(1, AlignDelegate(self.scan_memory_result_table))
        self.scan_memory_result_table.setItemDelegateForColumn(2, AlignDelegate(self.scan_memory_result_table))

        memory_scan_result_table_layout.addWidget(self.scan_memory_result_table)

        scan_memory_button = QPushButton("Track selected")
        scan_memory_button.clicked.connect(self.track_selected)

        rescan_memory_button = QPushButton("Clear")
        rescan_memory_button.clicked.connect(self.clear_scan_result)

        memory_scan_result_buttons_layout.addWidget(scan_memory_button)
        memory_scan_result_buttons_layout.addWidget(rescan_memory_button)

        self.track_memory_table = QTableWidget(0, 4)
        self.track_memory_table.setHorizontalHeaderLabels(["Address", "Value", "Value(hex)", "Comment"])
        self.track_memory_table.verticalHeader().hide()
        self.track_memory_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.track_memory_table.setColumnWidth(0, 80)
        self.track_memory_table.setColumnWidth(1, 80)
        self.track_memory_table.setColumnWidth(2, 80)
        self.track_memory_table.setColumnWidth(3, 80)

        track_memory_table_header = self.track_memory_table.horizontalHeader()
        track_memory_table_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        track_memory_table_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        track_memory_table_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        track_memory_table_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.track_memory_table.setItemDelegateForColumn(1, AlignDelegate(self.track_memory_table))
        self.track_memory_table.setItemDelegateForColumn(2, AlignDelegate(self.track_memory_table))

        self.track_memory_table.itemChanged.connect(self.on_item_changed)
        self.track_memory_table.itemPressed.connect(self.on_item_pressed)
        # self.track_memory_table.itemEntered

        footer_layout.addWidget(self.track_memory_table)

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def on_item_pressed(self, item: QTableWidgetItem):
        self._track_memory_table_current_edit_item = item

    def on_item_changed(self, item: QTableWidgetItem):
        """Función que se ejecuta solo cuando el usuario modifica manualmente una celda."""
        if item == self._track_memory_table_current_edit_item:
            self._track_memory_table_current_edit_item = None

            addr = int(self.track_memory_table.item(item.row(), 0).text(), 16)

            try:
                if item.column() == 1:
                    self.pyboy.memory[addr] = int(item.text())
                elif item.column() == 2:
                    self.pyboy.memory[addr] = int(item.text(), 16)
            except:
                pass

            print(
                f"Celda modificada manualmente - Fila: {item.row()}, Columna: {item.column()}, Nuevo Valor: {item.text()}"
            )

    # def _init_pyboy(self):
    #     """Inicia PyBoy"""
    #     self.pyboy = PyBoy("Castlevania - The Adventure (Europe).gb")

    def closeEvent(self, event):
        """Se ejecuta al cerrar la ventana principal"""
        self.pyboy.stop(False)
        super().closeEvent(event)

    def play_game(self):
        while self.pyboy.tick():
            if not self.game_running:
                break

    @Slot()
    def start_game(self):
        """Iniciar/continuar la ejecución del juego"""
        if not self.game_running:
            self.game_running = True
            self.game_thread = threading.Thread(target=self.play_game)
            self.game_thread.daemon = True  # Permite que el hilo se cierre cuando se cierra la GUI
            self.game_thread.start()

            self.play_game_button.setText("Pause Game")
            self.play_game_button.clicked.disconnect()
            self.play_game_button.clicked.connect(self.stop_game)

    @Slot()
    def stop_game(self):
        """Detener la ejecución del juego"""
        self.game_running = False
        if self.game_thread and self.game_thread.is_alive():
            self.game_thread.join()

        self.play_game_button.setText("Resume Game")
        self.play_game_button.clicked.disconnect()
        self.play_game_button.clicked.connect(self.start_game)

    @Slot()
    def clear_scan_result(self):
        self.scan_memory_result_table.setRowCount(0)

    def display_scan_result(self, scan_result):
        self.clear_scan_result()

        row = 0
        for addr in scan_result:
            value = self.pyboy.memory[addr]

            itemAddr = QTableWidgetItem(f"0x{addr:04X}")
            itemAddr.setFlags(itemAddr.flags() ^ Qt.ItemIsEditable)

            itemValue = QTableWidgetItem(f"{value}")
            itemValue.setFlags(itemValue.flags() ^ Qt.ItemIsEditable)

            itemValueHex = QTableWidgetItem(f"{value:02X}")
            itemValueHex.setFlags(itemValueHex.flags() ^ Qt.ItemIsEditable)

            self.scan_memory_result_table.insertRow(row)
            self.scan_memory_result_table.setItem(row, 0, itemAddr)
            self.scan_memory_result_table.setItem(row, 1, itemValue)
            self.scan_memory_result_table.setItem(row, 2, itemValueHex)
            row += 1

    def track_memory(self):
        while self.track_running:
            for row in range(self.track_memory_table.rowCount()):

                if (
                    self.track_memory_table.currentRow() != row
                    or self.track_memory_table.state() != QAbstractItemView.State.EditingState
                ):

                    addr = int(self.track_memory_table.item(row, 0).text(), 16)
                    value = self.pyboy.memory[addr]

                    self.track_memory_table.item(row, 1).setText(f"{value}")
                    self.track_memory_table.item(row, 2).setText(f"{value:02X}")

            time.sleep(0.05)

    @Slot()
    def start_track(self):
        """Iniciar tracking de la memoria"""
        if not self.track_running:
            self.track_running = True
            self.track_thread = threading.Thread(target=self.track_memory)
            self.track_thread.daemon = True  # Permite que el hilo se cierre cuando se cierra la GUI
            self.track_thread.start()

            # self.play_game_button.setText("Pause Game")
            # self.play_game_button.clicked.connect(self.stop_game)

    @Slot()
    def stop_track(self):
        """Detener tracking de la memoria"""
        self.track_running = False
        if self.track_thread and self.track_thread.is_alive():
            self.track_thread.join()

        # self.play_game_button.setText("Resume Game")
        # self.play_game_button.clicked.connect(self.start_game)

    @Slot()
    def track_selected(self):
        for item in self.scan_memory_result_table.selectedItems():
            if item.column() == 0:

                addr = int(item.text(), 16)
                value = int(self.scan_memory_result_table.item(item.row(), 1).text())

                itemAddr = QTableWidgetItem(f"0x{addr:04X}")
                itemAddr.setFlags(itemAddr.flags() ^ Qt.ItemIsEditable)
                itemValue = QTableWidgetItem(f"{value}")
                # itemValue.setFlags(itemValue.flags() ^ Qt.ItemIsEditable)

                itemValueHex = QTableWidgetItem(f"{value:02X}")
                # itemValueHex.setFlags(itemValueHex.flags() ^ Qt.ItemIsEditable)

                self.track_memory_table.insertRow(0)
                self.track_memory_table.setItem(0, 0, itemAddr)
                self.track_memory_table.setItem(0, 1, itemValue)
                self.track_memory_table.setItem(0, 2, itemValueHex)

        self.start_track()

    @Slot()
    def scan_memory(self):
        scan_result = self.pyboy.memory_scanner.scan_memory(
            target_value=self.value_input.value(),
            start_addr=int(self.start_addr_input.text(), 0),
            end_addr=int(self.end_addr_input.text(), 0),
            standard_comparison_type=StandardComparisonType(self.standard_comparison_type_input_group.checkedId()),
            value_type=ScanMode(self.value_type_input_group.checkedId()),
            # byte_width=self._scan_memory_byte_width,
            # byteorder=self._scan_memory_byteorder
        )
        self.display_scan_result(scan_result)

    @Slot()
    def rescan_memory(self):
        scan_result = self.pyboy.memory_scanner.rescan_memory(
            new_value=self.value_input.value(),
            dynamic_comparison_type=DynamicComparisonType(self.dynamic_comparison_type_input_group.checkedId()),
            # byteorder=self._scan_memory_byteorder
        )
        self.display_scan_result(scan_result)
