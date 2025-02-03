import tkinter as tk
from tkinter import ttk, N, S, E, W

from pyboy import PyBoy
from pyboy.api.memory_scanner import ScanMode, StandardComparisonType, DynamicComparisonType

import threading
import time

class MemoryScannerGUI:
    def __init__(self, root, pyboy_instance):
        self.root = root
        self.root.title("Memory Scanner for PyBoy")

        self.pyboy = pyboy_instance

        self.running = False
        self.scan_thread = None

        self.game_running = False
        self.game_thread = None

        self._scan_memory_target_value = 0
        self._scan_memory_start_addr = 0x0000
        self._scan_memory_end_addr = 0xFFFF
        self._scan_memory_standard_comparison_type = tk.IntVar(value=StandardComparisonType.EXACT.value)
        self._scan_memory_dynamic_comparison_type = tk.IntVar(value=DynamicComparisonType.MATCH.value)
        self._scan_memory_value_type = tk.IntVar(value=ScanMode.INT.value)
        self._scan_memory_byte_width = 1
        self._scan_memory_byteorder = "little"


     # Crear la tabla
        self.create_widgets()

    def create_widgets(self):


        self.header_frame = ttk.Frame(self.root)
        self.header_frame.pack(pady=5, fill=tk.X)
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        self.footer_frame = ttk.Frame(self.root)
        self.footer_frame.pack(pady=5, fill=tk.X)

        self.left_aside_frame = ttk.Frame(self.main_frame)
        self.left_aside_frame.grid(row=0, column=0, padx=5, sticky=W)
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=0, column=1, padx=5, sticky=N+S+E+W)



        # Start game button
        self.game_button = ttk.Button(self.header_frame, text="Start Game", command=self.start_game)
        self.game_button.pack()




        self.scan_input_frame = ttk.Frame(self.left_aside_frame)
        self.scan_input_frame.pack(pady=5)

        # Target value
        ttk.Label(self.scan_input_frame, text="Value").grid(row=0, column=0, pady=5, sticky=W)
        self.target_value_entry = ttk.Entry(self.scan_input_frame)
        self.target_value_entry.grid(row=0, column=1, padx=5, pady=5, sticky=W)

        # Start address
        ttk.Label(self.scan_input_frame, text="Start address").grid(row=1, column=0, pady=5, sticky=W)
        self.start_addr_entry = ttk.Entry(self.scan_input_frame)
        self.start_addr_entry.insert(0, hex(self._scan_memory_start_addr))
        self.start_addr_entry.grid(row=1, column=1, padx=5, pady=5, sticky=W)

        # End address
        ttk.Label(self.scan_input_frame, text="End address").grid(row=2, column=0, pady=5, sticky=W)
        self.end_addr_entry = ttk.Entry(self.scan_input_frame)
        self.end_addr_entry.insert(0, hex(self._scan_memory_end_addr))
        self.end_addr_entry.grid(row=2, column=1, padx=5, pady=5, sticky=W)

        # Type value 
        ttk.Label(self.scan_input_frame, text="Type").grid(row=3, column=0, columnspan=2, pady=5, sticky=W)
        ttk.Radiobutton(self.scan_input_frame, text="Integer", variable=self._scan_memory_value_type, value=ScanMode.INT.value).grid(row=3, column=1, pady=2, sticky=W)
        ttk.Radiobutton(self.scan_input_frame, text="BCD", variable=self._scan_memory_value_type, value=ScanMode.BCD.value).grid(row=4, column=1, pady=2, sticky=W)

        # Standard Comparison Type value 
        ttk.Label(self.scan_input_frame, text="Scan for").grid(row=5, column=0, columnspan=2, pady=5, sticky=W)
        ttk.Radiobutton(self.scan_input_frame, text="Exact", variable=self._scan_memory_standard_comparison_type, value=StandardComparisonType.EXACT.value).grid(row=5, column=1, pady=2, sticky=W)
        ttk.Radiobutton(self.scan_input_frame, text="Greather than", variable=self._scan_memory_standard_comparison_type, value=StandardComparisonType.GREATER_THAN.value).grid(row=6, column=1, pady=2, sticky=W)
        ttk.Radiobutton(self.scan_input_frame, text="Greather than or equal", variable=self._scan_memory_standard_comparison_type, value=StandardComparisonType.GREATER_THAN_OR_EQUAL.value).grid(row=7, column=1, pady=2, sticky=W)
        ttk.Radiobutton(self.scan_input_frame, text="Less than", variable=self._scan_memory_standard_comparison_type, value=StandardComparisonType.LESS_THAN.value).grid(row=8, column=1, pady=2, sticky=W)
        ttk.Radiobutton(self.scan_input_frame, text="Less than or equal", variable=self._scan_memory_standard_comparison_type, value=StandardComparisonType.LESS_THAN_OR_EQUAL.value).grid(row=9, column=1, pady=2, sticky=W)


        # Dynamic Comparison Type value 
        ttk.Label(self.scan_input_frame, text="Re-scan").grid(row=10, column=0, columnspan=2, pady=5, sticky=W)
        ttk.Radiobutton(self.scan_input_frame, text="Match", variable=self._scan_memory_dynamic_comparison_type, value=DynamicComparisonType.MATCH.value).grid(row=10, column=1, pady=2, sticky=W)
        ttk.Radiobutton(self.scan_input_frame, text="Increased", variable=self._scan_memory_dynamic_comparison_type, value=DynamicComparisonType.INCREASED.value).grid(row=11, column=1, pady=2, sticky=W)
        ttk.Radiobutton(self.scan_input_frame, text="Decreased", variable=self._scan_memory_dynamic_comparison_type, value=DynamicComparisonType.DECREASED.value).grid(row=12, column=1, pady=2, sticky=W)
        ttk.Radiobutton(self.scan_input_frame, text="Changed", variable=self._scan_memory_dynamic_comparison_type, value=DynamicComparisonType.CHANGED.value).grid(row=13, column=1, pady=2, sticky=W)
        ttk.Radiobutton(self.scan_input_frame, text="Unchanged", variable=self._scan_memory_dynamic_comparison_type, value=DynamicComparisonType.UNCHANGED.value).grid(row=14, column=1, pady=2, sticky=W)

        # Nueva Búsqueda
        self.scan_button = ttk.Button(self.scan_input_frame, text="New Scan", command=self.scan_memory)
        self.scan_button.grid(row=15, column=0, pady=10)

        # Búsqueda sobre resultados anteriores
        self.rescan_button = ttk.Button(self.scan_input_frame, text="Re-scan", command=self.rescan_memory)
        self.rescan_button.grid(row=15, column=1, pady=10)

        
        # Tabla de resultados de busqueda en memoria
        # Crear frame para la tabla
        frame_scan_results_table = tk.Frame(self.content_frame)
        frame_scan_results_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Crear la tabla (tree)
        self.search_result_tree = ttk.Treeview(frame_scan_results_table, columns=("address", "value", "value_hex"), show="headings")
        # Configurar las columnas
        self.search_result_tree.heading("address", text="Address")
        self.search_result_tree.heading("value", text="Value")
        self.search_result_tree.heading("value_hex", text="Value (hex)")
        self.search_result_tree.column("address", width=150, anchor="center")
        self.search_result_tree.column("value", width=150, anchor="center")
        self.search_result_tree.column("value_hex", width=150, anchor="center")
        # Scrollbar para el eje Y
        scan_results_table_scrollbar_y = ttk.Scrollbar(frame_scan_results_table, orient=tk.VERTICAL, command=self.search_result_tree.yview)
        self.search_result_tree.configure(yscrollcommand=scan_results_table_scrollbar_y.set)
        # Ubicar tabla y scrollbar
        self.search_result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scan_results_table_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Boton track address
        self.track_button = ttk.Button(self.content_frame, text="Track selected", command=self.track_selected)
        self.track_button.pack(pady=5)

        # Botón para vaciar todos los datos de la tabla
        self.clear_button = ttk.Button(self.content_frame, text="Clear", command=self.clear_search_results)
        self.clear_button.pack(pady=5)

                
        # Tabla de tracking
        # Crear frame para la tabla
        frame_tracking_table = tk.Frame(self.root)
        frame_tracking_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Crear la tabla (tree)
        self.tracking_table = ttk.Treeview(frame_tracking_table, columns=("address", "value", "value_hex", "comment"), show="headings")
        # Configurar las columnas
        self.tracking_table.heading("address", text="Address")
        self.tracking_table.heading("value", text="Value")
        self.tracking_table.heading("value_hex", text="Value (hex)")
        self.tracking_table.heading("comment", text="Comment")
        self.tracking_table.column("address", width=150, anchor="center")
        self.tracking_table.column("value", width=150, anchor="center")
        self.tracking_table.column("value_hex", width=150, anchor="center")
        self.tracking_table.column("comment", width=150, anchor="center")
        # Scrollbar para el eje Y
        tracking_table_scrollbar_y = ttk.Scrollbar(frame_tracking_table, orient=tk.VERTICAL, command=self.tracking_table.yview)
        self.tracking_table.configure(yscrollcommand=tracking_table_scrollbar_y.set)
        # Ubicar tabla y scrollbar
        self.tracking_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tracking_table_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)


    def clear_search_results(self):
        """Vaciar todos los datos de la tabla"""
        self.search_result_tree.delete(*self.search_result_tree.get_children())  # Eliminar cada fila de la tabla

    def update_memory_display(self):
        """Actualizar la visualización de la memoria en la GUI"""
        memory = self.pyboy.memory  # Acceder a la memoria de PyBoy

        self.clear_search_results()

        # Leer un bloque de memoria (ejemplo de dirección 0xC000 a 0xC100)
        for i in range(0xC000, 0xC100):
            # Mostrar los valores de memoria en la tabla
            self.search_result_tree.insert("", "end", values=(hex(i), memory[i], None))

    def display_scan_result(self, scan_result):
        self.clear_search_results()
        for addr in scan_result:
            value = self.pyboy.memory[addr]
            self.search_result_tree.insert("", "end", values=(hex(addr), value, "%0.2X" % value))

    def scan_memory(self):
        scan_result = self.pyboy.memory_scanner.scan_memory(
            target_value=int(self.target_value_entry.get(), 0),
            start_addr=int(self.start_addr_entry.get(), 0),
            end_addr=int(self.end_addr_entry.get(), 0),
            standard_comparison_type=StandardComparisonType(self._scan_memory_standard_comparison_type.get()),
            value_type=ScanMode(self._scan_memory_value_type.get()),
            byte_width=self._scan_memory_byte_width,
            byteorder=self._scan_memory_byteorder
        )
        self.display_scan_result(scan_result)

    def rescan_memory(self):
        scan_result = self.pyboy.memory_scanner.rescan_memory(
            new_value=int(self.target_value_entry.get(), 0),
            dynamic_comparison_type=DynamicComparisonType(self._scan_memory_dynamic_comparison_type.get()),
            byteorder=self._scan_memory_byteorder
        )
        self.display_scan_result(scan_result)

    # def scan_memory(self):
    #     """Escanear la memoria en un hilo independiente para no bloquear la interfaz"""
    #     while self.running:
    #         self.update_memory_display()  # Actualizar la visualización
    #         time.sleep(0.1)  # Pausa corta entre actualizaciones

    # def start_scanning(self):
    #     """Iniciar el escaneo de memoria"""
    #     if not self.running:
    #         self.running = True
    #         self.scan_thread = threading.Thread(target=self.scan_memory)
    #         self.scan_thread.daemon = True  # Permite que el hilo se cierre cuando se cierra la GUI
    #         self.scan_thread.start()
    #         self.scan_button.config(text="Stop Scanning", command=self.stop_scanning)
    
    # def stop_scanning(self):
    #     """Detener el escaneo de memoria"""
    #     self.running = False
    #     if self.scan_thread and self.scan_thread.is_alive():
    #         self.scan_thread.join()
    #     self.scan_button.config(text="Start Scanning", command=self.start_scanning)


    def play_game(self):
        while self.pyboy.tick() and self.game_running:
            pass

    def start_game(self):
        """Iniciar el juego"""
        if not self.game_running:
            self.game_running = True
            self.game_thread = threading.Thread(target=self.play_game)
            self.game_thread.daemon = True  # Permite que el hilo se cierre cuando se cierra la GUI
            self.game_thread.start()
            self.game_button.config(text="Pause Game", command=self.stop_game)
      
    def stop_game(self):
        """Detener el juego"""
        self.game_running = False
        if self.game_thread and self.game_thread.is_alive():
            self.game_thread.join()
        self.game_button.config(text="Resume Game", command=self.start_game)

    def track_selected(self):
        for item_id in self.search_result_tree.selection():
            self.tracking_table.insert("", "end", values=self.search_result_tree.item(item_id)["values"]+[""])

def main():
    # Crear una instancia de PyBoy con la ROM deseada
    pyboy = PyBoy("Castlevania - The Adventure (Europe).gb")

    # Crear la ventana principal de Tkinter
    root = tk.Tk()
    gui = MemoryScannerGUI(root, pyboy)

    # Ejecutar el loop de la GUI
    root.mainloop()

    # Detener PyBoy cuando se cierre la GUI
    pyboy.stop()

if __name__ == "__main__":
    main()
