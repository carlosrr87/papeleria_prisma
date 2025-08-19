# Clases auxiliares para el sistema de compras

class OrdenSugeridaView:
    def __init__(self, parent, sugerencias, callback):
        self.parent = parent
        self.sugerencias = sugerencias
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Orden Sugerida")
        self.window.geometry("800x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.productos_seleccionados = []
        self.crear_interfaz()
        self.cargar_sugerencias()
        self.center_window()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"800x500+{x}+{y}")
    
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Productos Sugeridos para Reorden", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Descripción
        ttk.Label(main_frame, 
                 text="Seleccione los productos que desea agregar a la orden de compra:").pack(pady=(0, 10))
        
        # Frame de tabla
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Crear Treeview
        columns = ('seleccionar', 'codigo', 'nombre', 'stock', 'minimo', 'sugerida', 'precio')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar encabezados
        self.tree.heading('seleccionar', text='Sel.')
        self.tree.heading('codigo', text='Código')
        self.tree.heading('nombre', text='Producto')
        self.tree.heading('stock', text='Stock')
        self.tree.heading('minimo', text='Mínimo')
        self.tree.heading('sugerida', text='Cant. Sugerida')
        self.tree.heading('precio', text='Precio')
        
        # Configurar anchos
        self.tree.column('seleccionar', width=50)
        self.tree.column('codigo', width=80)
        self.tree.column('nombre', width=200)
        self.tree.column('stock', width=60)
        self.tree.column('minimo', width=60)
        self.tree.column('sugerida', width=100)
        self.tree.column('precio', width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind click para seleccionar
        self.tree.bind('<Button-1>', self.on_tree_click)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Seleccionar Todos", 
                  command=self.seleccionar_todos).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Deseleccionar Todos", 
                  command=self.deseleccionar_todos).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(button_frame, text="Agregar Seleccionados", 
                  command=self.agregar_seleccionados).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
    
    def cargar_sugerencias(self):
        """Carga las sugerencias en la tabla"""
        for sugerencia in self.sugerencias:
            self.tree.insert('', tk.END, values=(
                "☐",  # Checkbox vacío
                sugerencia['codigo'],
                sugerencia['nombre'],
                sugerencia['stock_actual'],
                sugerencia['stock_minimo'],
                sugerencia['cantidad_sugerida'],
                f"${sugerencia['precio_compra']:,.2f}"
            ))
    
    def on_tree_click(self, event):
        """Maneja el click en la tabla para seleccionar/deseleccionar"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x, event.y)
            if column == '#1':  # Columna de selección
                item = self.tree.identify_row(event.y)
                if item:
                    self.toggle_selection(item)
    
    def toggle_selection(self, item):
        """Alterna la selección de un item"""
        values = list(self.tree.item(item, 'values'))
        if values[0] == "☐":
            values[0] = "☑"
        else:
            values[0] = "☐"
        self.tree.item(item, values=values)
    
    def seleccionar_todos(self):
        """Selecciona todos los productos"""
        for item in self.tree.get_children():
            values = list(self.tree.item(item, 'values'))
            values[0] = "☑"
            self.tree.item(item, values=values)
    
    def deseleccionar_todos(self):
        """Deselecciona todos los productos"""
        for item in self.tree.get_children():
            values = list(self.tree.item(item, 'values'))
            values[0] = "☐"
            self.tree.item(item, values=values)
    
    def agregar_seleccionados(self):
        """Agrega los productos seleccionados"""
        productos_seleccionados = []
        
        for i, item in enumerate(self.tree.get_children()):
            values = self.tree.item(item, 'values')
            if values[0] == "☑":
                sugerencia = self.sugerencias[i]
                productos_seleccionados.append({
                    'producto_id': sugerencia['producto_id'],
                    'codigo': sugerencia['codigo'],
                    'nombre': sugerencia['nombre'],
                    'cantidad': sugerencia['cantidad_sugerida'],
                    'precio_compra': sugerencia['precio_compra']
                })
        
        if productos_seleccionados:
            self.callback(productos_seleccionados)
            self.window.destroy()
        else:
            messagebox.showwarning("Advertencia", "Seleccione al menos un producto")

class ProveedorFormView:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Nuevo Proveedor")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables
        self.nombre_var = tk.StringVar()
        self.contacto_var = tk.StringVar()
        self.telefono_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.direccion_var = tk.StringVar()
        
        self.crear_interfaz()
        self.center_window()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"500x400+{x}+{y}")
    
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Nuevo Proveedor", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Nombre
        ttk.Label(form_frame, text="* Nombre:").grid(row=row, column=0, sticky="w", pady=5)
        nombre_entry = ttk.Entry(form_frame, textvariable=self.nombre_var, width=40)
        nombre_entry.grid(row=row, column=1, sticky="w", pady=5)
        nombre_entry.focus()
        row += 1
        
        # Contacto
        ttk.Label(form_frame, text="Persona de Contacto:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.contacto_var, width=40).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Teléfono
        ttk.Label(form_frame, text="Teléfono:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.telefono_var, width=40).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.email_var, width=40).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Dirección
        ttk.Label(form_frame, text="Dirección:").grid(row=row, column=0, sticky="w", pady=5)
        direccion_text = tk.Text(form_frame, width=40, height=4)
        direccion_text.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Vincular el Text widget a la variable
        self.direccion_text = direccion_text
        
        # Nota
        ttk.Label(form_frame, text="* Campo obligatorio", 
                 font=("Arial", 8)).grid(row=row, column=0, columnspan=2, pady=(20, 10))
        row += 1
        
        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Guardar", 
                  command=self.guardar).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.window.destroy).pack(side=tk.LEFT)
    
    def guardar(self):
        """Guarda el nuevo proveedor"""
        nombre = self.nombre_var.get().strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        direccion = self.direccion_text.get(1.0, tk.END).strip()
        
        datos = {
            'nombre': nombre,
            'contacto': self.contacto_var.get().strip(),
            'telefono': self.telefono_var.get().strip(),
            'email': self.email_var.get().strip(),
            'direccion': direccion
        }
        
        try:
            proveedor_id = ProveedorModel.crear(datos)
            if proveedor_id:
                # Obtener proveedor creado
                proveedor = ProveedorModel.obtener_todos()
                nuevo_proveedor = None
                for p in proveedor:
                    if p['id'] == proveedor_id:
                        nuevo_proveedor = p
                        break
                
                messagebox.showinfo("Éxito", "Proveedor creado correctamente")
                self.callback(nuevo_proveedor)
                self.window.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear el proveedor")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

class ProductosBajoStockView:
    def __init__(self, parent):
        self.parent = parent
        
        self.window = tk.Toplevel(parent)
        self.window.title("Productos con Stock Bajo")
        self.window.geometry("900x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.crear_interfaz()
        self.cargar_productos()
        self.center_window()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"900x600+{x}+{y}")
    
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Productos con Stock Bajo", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        # Descripción
        ttk.Label(main_frame, 
                 text="Productos que están en o por debajo del stock mínimo:").pack(pady=(0, 10))
        
        # Frame de tabla
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Crear Treeview
        columns = ('codigo', 'nombre', 'categoria', 'stock', 'minimo', 'diferencia', 'proveedor')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Configurar encabezados
        self.tree.heading('codigo', text='Código')
        self.tree.heading('nombre', text='Producto')
        self.tree.heading('categoria', text='Categoría')
        self.tree.heading('stock', text='Stock')
        self.tree.heading('minimo', text='Mínimo')
        self.tree.heading('diferencia', text='Diferencia')
        self.tree.heading('proveedor', text='Proveedor')
        
        # Configurar anchos
        self.tree.column('codigo', width=80)
        self.tree.column('nombre', width=200)
        self.tree.column('categoria', width=120)
        self.tree.column('stock', width=60)
        self.tree.column('minimo', width=60)
        self.tree.column('diferencia', width=80)
        self.tree.column('proveedor', width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Actualizar", 
                  command=self.cargar_productos).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Exportar Lista", 
                  command=self.exportar_lista).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cerrar", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
    
    def cargar_productos(self):
        """Carga los productos con stock bajo"""
        try:
            productos = CompraModel.obtener_productos_bajo_minimo()
            
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            if not productos:
                self.tree.insert('', tk.END, values=(
                    "", "No hay productos con stock bajo", "", "", "", "", ""
                ))
                return
            
            # Llenar tabla
            for producto in productos:
                diferencia = producto['stock_actual'] - producto['stock_minimo']
                
                # Determinar color según criticidad
                tags = ()
                if producto['stock_actual'] <= 0:
                    tags = ('critico',)
                elif diferencia < 0:
                    tags = ('bajo',)
                else:
                    tags = ('minimo',)
                
                self.tree.insert('', tk.END, values=(
                    producto['codigo'],
                    producto['nombre'],
                    producto['categoria_nombre'] or 'Sin categoría',
                    producto['stock_actual'],
                    producto['stock_minimo'],
                    diferencia,
                    producto['proveedor_nombre'] or 'Sin proveedor'
                ), tags=tags)
            
            # Configurar colores
            self.tree.tag_configure('critico', background='#ffcccc')
            self.tree.tag_configure('bajo', background='#fff2cc')
            self.tree.tag_configure('minimo', background='#e6f3ff')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando productos: {str(e)}")
    
    def exportar_lista(self):
        """Exporta la lista de productos con stock bajo"""
        try:
            import csv
            from tkinter import filedialog
            
            # Pedir ubicación de archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar lista de productos con stock bajo"
            )
            
            if not filename:
                return
            
            # Obtener datos
            productos = CompraModel.obtener_productos_bajo_minimo()
            
            # Escribir CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Encabezados
                writer.writerow(['Código', 'Producto', 'Categoría', 'Stock Actual', 
                               'Stock Mínimo', 'Diferencia', 'Proveedor'])
                
                # Datos
                for producto in productos:
                    diferencia = producto['stock_actual'] - producto['stock_minimo']
                    writer.writerow([
                        producto['codigo'],
                        producto['nombre'],
                        producto['categoria_nombre'] or 'Sin categoría',
                        producto['stock_actual'],
                        producto['stock_minimo'],
                        diferencia,
                        producto['proveedor_nombre'] or 'Sin proveedor'
                    ])
            
            messagebox.showinfo("Éxito", f"Lista exportada correctamente:\n{filename}")
            
        except ImportError:
            messagebox.showerror("Error", "Módulo csv no disponible")
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando: {str(e)}")# src/views/compras_view.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.compra import CompraModel, ProveedorModelExtendido
from models.producto import ProductoModel, ProveedorModel

class ComprasView:
    def __init__(self, parent, usuario_data):
        self.parent = parent
        self.usuario_data = usuario_data
        self.frame = None
        
        # Variables del carrito de compras
        self.carrito = []
        self.total = 0.0
        
        # Variables de la interfaz
        self.proveedor_seleccionado = None
        self.search_producto_var = tk.StringVar()
        self.proveedor_var = tk.StringVar()
        
        # Configurar eventos
        self.search_producto_var.trace('w', self.buscar_productos)
        self.proveedor_var.trace('w', self.on_proveedor_change)
        
        self.crear_interfaz()
        self.cargar_proveedores()
        self.actualizar_totales()
    
    def crear_interfaz(self):
        # Frame principal
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Nueva Orden de Compra", 
                 font=("Arial", 18, "bold")).pack(side=tk.LEFT)
        
        # Número de orden
        numero_compra = CompraModel.generar_numero_compra()
        ttk.Label(title_frame, text=f"Orden #: {numero_compra}", 
                 font=("Arial", 12)).pack(side=tk.RIGHT)
        self.numero_compra = numero_compra
        
        # Frame principal dividido en dos columnas
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Columna izquierda - Productos y carrito
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Columna derecha - Proveedor y totales
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Crear secciones
        self.crear_seccion_proveedor(right_frame)
        self.crear_seccion_productos(left_frame)
        self.crear_seccion_carrito(left_frame)
        self.crear_seccion_totales(right_frame)
        self.crear_botones_accion(right_frame)
    
    def crear_seccion_proveedor(self, parent):
        # Frame del proveedor
        proveedor_frame = ttk.LabelFrame(parent, text="Proveedor", padding="10")
        proveedor_frame.pack(fill=tk.X, pady=(0, 10))
        proveedor_frame.configure(width=300)
        
        # Selección de proveedor
        ttk.Label(proveedor_frame, text="* Seleccionar Proveedor:").pack(anchor=tk.W)
        
        self.proveedor_combo = ttk.Combobox(proveedor_frame, textvariable=self.proveedor_var, 
                                           state="readonly", width=35)
        self.proveedor_combo.pack(fill=tk.X, pady=(5, 10))
        
        # Información del proveedor
        self.proveedor_info_frame = ttk.Frame(proveedor_frame)
        self.proveedor_info_frame.pack(fill=tk.X)
        
        self.proveedor_info_text = tk.Text(self.proveedor_info_frame, height=4, width=35, 
                                          wrap=tk.WORD, state=tk.DISABLED)
        self.proveedor_info_text.pack(fill=tk.X)
        
        # Botones de proveedor
        prov_buttons = ttk.Frame(proveedor_frame)
        prov_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(prov_buttons, text="Nuevo Proveedor", 
                  command=self.nuevo_proveedor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(prov_buttons, text="Orden Sugerida", 
                  command=self.generar_orden_sugerida).pack(side=tk.LEFT)
    
    def crear_seccion_productos(self, parent):
        # Frame para búsqueda de productos
        productos_frame = ttk.LabelFrame(parent, text="Productos del Proveedor", padding="10")
        productos_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Búsqueda
        search_frame = ttk.Frame(productos_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_producto_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Lista de productos
        self.productos_frame = ttk.Frame(productos_frame)
        self.productos_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear Treeview para productos
        columns = ('codigo', 'nombre', 'stock', 'minimo', 'precio_compra')
        self.productos_tree = ttk.Treeview(self.productos_frame, columns=columns, 
                                          show='headings', height=8)
        
        # Configurar encabezados
        self.productos_tree.heading('codigo', text='Código')
        self.productos_tree.heading('nombre', text='Nombre')
        self.productos_tree.heading('stock', text='Stock')
        self.productos_tree.heading('minimo', text='Mínimo')
        self.productos_tree.heading('precio_compra', text='Precio Compra')
        
        # Configurar anchos
        self.productos_tree.column('codigo', width=100)
        self.productos_tree.column('nombre', width=250)
        self.productos_tree.column('stock', width=60)
        self.productos_tree.column('minimo', width=60)
        self.productos_tree.column('precio_compra', width=100)
        
        # Scrollbar para productos
        productos_scroll = ttk.Scrollbar(self.productos_frame, orient=tk.VERTICAL, 
                                        command=self.productos_tree.yview)
        self.productos_tree.configure(yscrollcommand=productos_scroll.set)
        
        self.productos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        productos_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind doble click para agregar producto
        self.productos_tree.bind('<Double-1>', self.agregar_producto_doble_click)
        
        # Botón agregar
        ttk.Button(productos_frame, text="Agregar a Orden", 
                  command=self.agregar_producto).pack(pady=(10, 0))
    
    def crear_seccion_carrito(self, parent):
        # Frame del carrito
        carrito_frame = ttk.LabelFrame(parent, text="Orden de Compra", padding="10")
        carrito_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Crear Treeview para carrito
        columns = ('codigo', 'nombre', 'cantidad', 'precio', 'subtotal')
        self.carrito_tree = ttk.Treeview(carrito_frame, columns=columns, 
                                        show='headings', height=10)
        
        # Configurar encabezados
        self.carrito_tree.heading('codigo', text='Código')
        self.carrito_tree.heading('nombre', text='Producto')
        self.carrito_tree.heading('cantidad', text='Cantidad')
        self.carrito_tree.heading('precio', text='Precio')
        self.carrito_tree.heading('subtotal', text='Subtotal')
        
        # Configurar anchos
        self.carrito_tree.column('codigo', width=100)
        self.carrito_tree.column('nombre', width=200)
        self.carrito_tree.column('cantidad', width=80)
        self.carrito_tree.column('precio', width=100)
        self.carrito_tree.column('subtotal', width=100)
        
        # Scrollbar para carrito
        carrito_scroll = ttk.Scrollbar(carrito_frame, orient=tk.VERTICAL, 
                                      command=self.carrito_tree.yview)
        self.carrito_tree.configure(yscrollcommand=carrito_scroll.set)
        
        self.carrito_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        carrito_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones del carrito
        carrito_buttons = ttk.Frame(carrito_frame)
        carrito_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(carrito_buttons, text="Editar Cantidad", 
                  command=self.editar_cantidad).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(carrito_buttons, text="Editar Precio", 
                  command=self.editar_precio).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(carrito_buttons, text="Quitar Producto", 
                  command=self.quitar_producto).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(carrito_buttons, text="Limpiar Orden", 
                  command=self.limpiar_carrito).pack(side=tk.LEFT)
    
    def crear_seccion_totales(self, parent):
        # Frame de totales
        totales_frame = ttk.LabelFrame(parent, text="Total de la Orden", padding="10")
        totales_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Total
        total_frame = ttk.Frame(totales_frame)
        total_frame.pack(fill=tk.X, pady=5)
        ttk.Label(total_frame, text="TOTAL ORDEN:", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.total_label = ttk.Label(total_frame, text="$0.00", 
                                    font=("Arial", 14, "bold"), 
                                    foreground="blue")
        self.total_label.pack(side=tk.RIGHT)
        
        # Información adicional
        info_frame = ttk.Frame(totales_frame)
        info_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.items_label = ttk.Label(info_frame, text="Productos: 0")
        self.items_label.pack(anchor=tk.W)
    
    def crear_botones_accion(self, parent):
        # Frame de botones
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botón crear orden (grande y destacado)
        self.btn_crear = ttk.Button(buttons_frame, text="CREAR ORDEN DE COMPRA", 
                                   command=self.crear_orden,
                                   style="Accent.TButton")
        self.btn_crear.pack(fill=tk.X, pady=(0, 10))
        
        # Otros botones
        ttk.Button(buttons_frame, text="Nueva Orden", 
                  command=self.nueva_orden).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(buttons_frame, text="Ver Productos Bajo Stock", 
                  command=self.ver_productos_bajo_stock).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(buttons_frame, text="Cancelar", 
                  command=self.cancelar_orden).pack(fill=tk.X)
    
    def cargar_proveedores(self):
        """Carga los proveedores en el combobox"""
        try:
            proveedores = ProveedorModelExtendido.obtener_todos_con_productos()
            
            # Preparar datos para el combobox
            proveedores_list = [""]
            self.proveedores_data = {}
            
            for proveedor in proveedores:
                display_text = f"{proveedor['nombre']} ({proveedor['total_productos']} productos)"
                proveedores_list.append(display_text)
                self.proveedores_data[display_text] = proveedor
            
            self.proveedor_combo['values'] = proveedores_list
            
        except Exception as e:
            print(f"Error cargando proveedores: {e}")
            messagebox.showerror("Error", f"Error cargando proveedores: {str(e)}")
    
    def on_proveedor_change(self, *args):
        """Se ejecuta cuando cambia la selección del proveedor"""
        proveedor_texto = self.proveedor_var.get()
        
        if proveedor_texto and proveedor_texto in self.proveedores_data:
            self.proveedor_seleccionado = self.proveedores_data[proveedor_texto]
            self.actualizar_info_proveedor()
            self.cargar_productos_proveedor()
        else:
            self.proveedor_seleccionado = None
            self.limpiar_info_proveedor()
            self.limpiar_productos()
    
    def actualizar_info_proveedor(self):
        """Actualiza la información del proveedor seleccionado"""
        if not self.proveedor_seleccionado:
            return
        
        info_text = f"""Proveedor: {self.proveedor_seleccionado['nombre']}
Contacto: {self.proveedor_seleccionado['contacto'] or 'N/A'}
Teléfono: {self.proveedor_seleccionado['telefono'] or 'N/A'}
Productos: {self.proveedor_seleccionado['total_productos']}
Stock bajo: {self.proveedor_seleccionado['productos_bajo_stock']}"""
        
        self.proveedor_info_text.config(state=tk.NORMAL)
        self.proveedor_info_text.delete(1.0, tk.END)
        self.proveedor_info_text.insert(1.0, info_text)
        self.proveedor_info_text.config(state=tk.DISABLED)
    
    def limpiar_info_proveedor(self):
        """Limpia la información del proveedor"""
        self.proveedor_info_text.config(state=tk.NORMAL)
        self.proveedor_info_text.delete(1.0, tk.END)
        self.proveedor_info_text.config(state=tk.DISABLED)
    
    def cargar_productos_proveedor(self):
        """Carga los productos del proveedor seleccionado"""
        if not self.proveedor_seleccionado:
            return
        
        try:
            productos = ProveedorModelExtendido.obtener_productos_proveedor(
                self.proveedor_seleccionado['id']
            )
            
            # Limpiar lista
            for item in self.productos_tree.get_children():
                self.productos_tree.delete(item)
            
            # Llenar lista
            for producto in productos:
                # Determinar color según stock
                tags = ()
                if producto['stock_actual'] <= 0:
                    tags = ('sin_stock',)
                elif producto['stock_actual'] <= producto['stock_minimo']:
                    tags = ('stock_bajo',)
                
                precio_compra = producto['precio_compra'] or 0
                
                self.productos_tree.insert('', tk.END, values=(
                    producto['codigo'],
                    producto['nombre'],
                    producto['stock_actual'],
                    producto['stock_minimo'],
                    f"${precio_compra:,.2f}"
                ), tags=tags)
            
            # Configurar colores
            self.productos_tree.tag_configure('sin_stock', background='#ffcccc')
            self.productos_tree.tag_configure('stock_bajo', background='#fff2cc')
            
        except Exception as e:
            print(f"Error cargando productos del proveedor: {e}")
            messagebox.showerror("Error", f"Error cargando productos: {str(e)}")
    
    def limpiar_productos(self):
        """Limpia la lista de productos"""
        for item in self.productos_tree.get_children():
            self.productos_tree.delete(item)
    
    def buscar_productos(self, *args):
        """Busca productos del proveedor seleccionado"""
        if not self.proveedor_seleccionado:
            return
        
        texto = self.search_producto_var.get().strip()
        
        try:
            # Obtener todos los productos del proveedor
            productos = ProveedorModelExtendido.obtener_productos_proveedor(
                self.proveedor_seleccionado['id']
            )
            
            # Filtrar por texto de búsqueda
            if texto:
                productos_filtrados = []
                for producto in productos:
                    if (texto.lower() in producto['nombre'].lower() or 
                        texto.lower() in producto['codigo'].lower()):
                        productos_filtrados.append(producto)
                productos = productos_filtrados
            
            # Limpiar y llenar lista
            for item in self.productos_tree.get_children():
                self.productos_tree.delete(item)
            
            for producto in productos:
                tags = ()
                if producto['stock_actual'] <= 0:
                    tags = ('sin_stock',)
                elif producto['stock_actual'] <= producto['stock_minimo']:
                    tags = ('stock_bajo',)
                
                precio_compra = producto['precio_compra'] or 0
                
                self.productos_tree.insert('', tk.END, values=(
                    producto['codigo'],
                    producto['nombre'],
                    producto['stock_actual'],
                    producto['stock_minimo'],
                    f"${precio_compra:,.2f}"
                ), tags=tags)
            
            # Configurar colores
            self.productos_tree.tag_configure('sin_stock', background='#ffcccc')
            self.productos_tree.tag_configure('stock_bajo', background='#fff2cc')
            
        except Exception as e:
            print(f"Error buscando productos: {e}")
    
    def agregar_producto_doble_click(self, event=None):
        """Agregar producto con doble click"""
        self.agregar_producto()
    
    def agregar_producto(self):
        """Agrega el producto seleccionado al carrito"""
        if not self.proveedor_seleccionado:
            messagebox.showwarning("Advertencia", "Primero seleccione un proveedor")
            return
        
        selected = self.productos_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        item = self.productos_tree.item(selected[0])
        codigo = item['values'][0]
        nombre = item['values'][1]
        stock_actual = int(item['values'][2])
        stock_minimo = int(item['values'][3])
        precio_text = item['values'][4].replace(', '').replace(',', '')
        
        # Obtener producto completo
        productos = ProveedorModelExtendido.obtener_productos_proveedor(
            self.proveedor_seleccionado['id']
        )
        producto = None
        for p in productos:
            if p['codigo'] == codigo:
                producto = p
                break
        
        if not producto:
            messagebox.showerror("Error", "No se pudo obtener la información del producto")
            return
        
        # Verificar si ya está en el carrito
        for i, item_carrito in enumerate(self.carrito):
            if item_carrito['producto_id'] == producto['id']:
                # Pedir nueva cantidad
                nueva_cantidad = simpledialog.askinteger(
                    "Cantidad",
                    f"El producto ya está en la orden.\n"
                    f"Cantidad actual: {item_carrito['cantidad']}\n"
                    f"Nueva cantidad:",
                    initialvalue=item_carrito['cantidad'],
                    minvalue=1
                )
                
                if nueva_cantidad:
                    self.carrito[i]['cantidad'] = nueva_cantidad
                    self.carrito[i]['subtotal'] = nueva_cantidad * item_carrito['precio_unitario']
                    self.actualizar_carrito_display()
                    self.actualizar_totales()
                return
        
        # Pedir cantidad y precio
        cantidad_sugerida = max(stock_minimo - stock_actual, stock_minimo) if stock_actual <= stock_minimo else stock_minimo
        
        cantidad = simpledialog.askinteger(
            "Cantidad a Ordenar",
            f"Producto: {nombre}\n"
            f"Stock actual: {stock_actual}\n"
            f"Stock mínimo: {stock_minimo}\n"
            f"Cantidad sugerida: {cantidad_sugerida}\n\n"
            f"Cantidad a ordenar:",
            initialvalue=cantidad_sugerida,
            minvalue=1
        )
        
        if not cantidad:
            return
        
        precio_compra = float(precio_text) if precio_text != '$0.00' else 0
        
        # Si no hay precio, pedirlo
        if precio_compra == 0:
            precio_str = simpledialog.askstring(
                "Precio de Compra",
                f"Ingrese el precio de compra para:\n{nombre}\n\n"
                f"Precio por unidad:",
                initialvalue="0.00"
            )
            
            if precio_str:
                try:
                    precio_compra = float(precio_str)
                except ValueError:
                    messagebox.showerror("Error", "Precio inválido")
                    return
            else:
                return
        
        # Agregar al carrito
        item_carrito = {
            'producto_id': producto['id'],
            'codigo': codigo,
            'nombre': nombre,
            'cantidad': cantidad,
            'precio_unitario': precio_compra,
            'subtotal': cantidad * precio_compra
        }
        
        self.carrito.append(item_carrito)
        self.actualizar_carrito_display()
        self.actualizar_totales()
    
    def actualizar_carrito_display(self):
        """Actualiza la visualización del carrito"""
        # Limpiar carrito
        for item in self.carrito_tree.get_children():
            self.carrito_tree.delete(item)
        
        # Llenar carrito
        for item in self.carrito:
            self.carrito_tree.insert('', tk.END, values=(
                item['codigo'],
                item['nombre'],
                item['cantidad'],
                f"${item['precio_unitario']:,.2f}",
                f"${item['subtotal']:,.2f}"
            ))
    
    def actualizar_totales(self):
        """Actualiza los totales de la orden"""
        self.total = sum(item['subtotal'] for item in self.carrito)
        
        # Actualizar labels
        self.total_label.config(text=f"${self.total:,.2f}")
        self.items_label.config(text=f"Productos: {len(self.carrito)}")
        
        # Habilitar/deshabilitar botón crear
        if len(self.carrito) > 0 and self.proveedor_seleccionado:
            self.btn_crear.config(state='normal')
        else:
            self.btn_crear.config(state='disabled')
    
    def editar_cantidad(self):
        """Edita la cantidad de un producto en el carrito"""
        selected = self.carrito_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto de la orden")
            return
        
        item_index = self.carrito_tree.index(selected[0])
        item_carrito = self.carrito[item_index]
        
        nueva_cantidad = simpledialog.askinteger(
            "Editar Cantidad",
            f"Nueva cantidad para {item_carrito['nombre']}:",
            initialvalue=item_carrito['cantidad'],
            minvalue=1
        )
        
        if nueva_cantidad:
            self.carrito[item_index]['cantidad'] = nueva_cantidad
            self.carrito[item_index]['subtotal'] = nueva_cantidad * item_carrito['precio_unitario']
            self.actualizar_carrito_display()
            self.actualizar_totales()
    
    def editar_precio(self):
        """Edita el precio de un producto en el carrito"""
        selected = self.carrito_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto de la orden")
            return
        
        item_index = self.carrito_tree.index(selected[0])
        item_carrito = self.carrito[item_index]
        
        nuevo_precio = simpledialog.askfloat(
            "Editar Precio",
            f"Nuevo precio unitario para {item_carrito['nombre']}:",
            initialvalue=item_carrito['precio_unitario'],
            minvalue=0.01
        )
        
        if nuevo_precio:
            self.carrito[item_index]['precio_unitario'] = nuevo_precio
            self.carrito[item_index]['subtotal'] = item_carrito['cantidad'] * nuevo_precio
            self.actualizar_carrito_display()
            self.actualizar_totales()
    
    def quitar_producto(self):
        """Quita un producto del carrito"""
        selected = self.carrito_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto de la orden")
            return
        
        item_index = self.carrito_tree.index(selected[0])
        producto_nombre = self.carrito[item_index]['nombre']
        
        if messagebox.askyesno("Confirmar", f"¿Quitar '{producto_nombre}' de la orden?"):
            del self.carrito[item_index]
            self.actualizar_carrito_display()
            self.actualizar_totales()
    
    def limpiar_carrito(self):
        """Limpia todo el carrito"""
        if len(self.carrito) == 0:
            return
        
        if messagebox.askyesno("Confirmar", "¿Limpiar toda la orden?"):
            self.carrito.clear()
            self.actualizar_carrito_display()
            self.actualizar_totales()
    
    def generar_orden_sugerida(self):
        """Genera una orden sugerida basada en productos con stock bajo"""
        if not self.proveedor_seleccionado:
            messagebox.showwarning("Advertencia", "Primero seleccione un proveedor")
            return
        
        try:
            sugerencias = CompraModel.generar_orden_sugerida(self.proveedor_seleccionado['id'])
            
            if not sugerencias:
                messagebox.showinfo("Información", 
                                   "No hay productos con stock bajo para este proveedor")
                return
            
            # Mostrar ventana de sugerencias
            OrdenSugeridaView(self.frame, sugerencias, self.aplicar_sugerencias)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando orden sugerida: {str(e)}")
    
    def aplicar_sugerencias(self, productos_seleccionados):
        """Aplica las sugerencias seleccionadas al carrito"""
        for producto in productos_seleccionados:
            # Verificar si ya está en el carrito
            encontrado = False
            for i, item_carrito in enumerate(self.carrito):
                if item_carrito['producto_id'] == producto['producto_id']:
                    # Actualizar cantidad
                    self.carrito[i]['cantidad'] = producto['cantidad']
                    self.carrito[i]['subtotal'] = producto['cantidad'] * item_carrito['precio_unitario']
                    encontrado = True
                    break
            
            if not encontrado:
                # Agregar nuevo item
                item_carrito = {
                    'producto_id': producto['producto_id'],
                    'codigo': producto['codigo'],
                    'nombre': producto['nombre'],
                    'cantidad': producto['cantidad'],
                    'precio_unitario': producto['precio_compra'],
                    'subtotal': producto['cantidad'] * producto['precio_compra']
                }
                self.carrito.append(item_carrito)
        
        self.actualizar_carrito_display()
        self.actualizar_totales()
        messagebox.showinfo("Éxito", f"Se agregaron {len(productos_seleccionados)} productos a la orden")
    
    def crear_orden(self):
        """Crea la orden de compra"""
        if not self.proveedor_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un proveedor")
            return
        
        if len(self.carrito) == 0:
            messagebox.showwarning("Advertencia", "La orden está vacía")
            return
        
        # Confirmar orden
        mensaje = (f"¿Crear orden de compra por ${self.total:,.2f}?\n"
                  f"Proveedor: {self.proveedor_seleccionado['nombre']}\n"
                  f"Productos: {len(self.carrito)}")
        
        if not messagebox.askyesno("Confirmar Orden", mensaje):
            return
        
        # Preparar datos de compra
        datos_compra = {
            'numero_compra': self.numero_compra,
            'proveedor_id': self.proveedor_seleccionado['id'],
            'usuario_id': self.usuario_data['id'],
            'fecha_compra': datetime.now(),
            'total': self.total
        }
        
        # Preparar detalles
        detalle_items = []
        for item in self.carrito:
            detalle_items.append({
                'producto_id': item['producto_id'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio_unitario'],
                'subtotal': item['subtotal']
            })
        
        # Crear orden
        try:
            compra_id = CompraModel.crear_compra(datos_compra, detalle_items)
            
            if compra_id:
                messagebox.showinfo("Éxito", 
                                  f"Orden de compra creada exitosamente\n"
                                  f"Número: {self.numero_compra}\n"
                                  f"Total: ${self.total:,.2f}")
                
                # Preguntar si quiere generar PDF
                if messagebox.askyesno("Generar PDF", "¿Desea generar la orden en PDF?"):
                    self.generar_pdf_orden(compra_id)
                
                # Limpiar para nueva orden
                self.nueva_orden()
            else:
                messagebox.showerror("Error", "No se pudo crear la orden de compra")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error creando orden: {str(e)}")
    
    def generar_pdf_orden(self, compra_id):
        """Genera el PDF de la orden de compra"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            import os
            
            # Obtener datos de la compra
            compra = CompraModel.obtener_compra_por_id(compra_id)
            if not compra:
                messagebox.showerror("Error", "No se pudo obtener los datos de la orden")
                return
            
            # Crear directorio
            proyecto_root = os.getcwd()
            ordenes_dir = os.path.join(proyecto_root, "ordenes_compra")
            os.makedirs(ordenes_dir, exist_ok=True)
            
            filename = os.path.join(ordenes_dir, f"orden_{compra['numero_compra']}.pdf")
            
            # Crear PDF
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            
            # Encabezado
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "PAPELERÍA PRISMA")
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 75, "ORDEN DE COMPRA")
            
            # Información de la orden
            c.setFont("Helvetica", 10)
            c.drawString(400, height - 50, f"Orden #: {compra['numero_compra']}")
            c.drawString(400, height - 65, f"Fecha: {compra['fecha_compra'].strftime('%d/%m/%Y')}")
            c.drawString(400, height - 80, f"Estado: {compra['estado'].title()}")
            
            # Proveedor
            y = height - 110
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "PROVEEDOR:")
            c.setFont("Helvetica", 10)
            c.drawString(50, y - 15, compra['proveedor_nombre'])
            if compra['proveedor_contacto']:
                c.drawString(50, y - 30, f"Contacto: {compra['proveedor_contacto']}")
            if compra['proveedor_telefono']:
                c.drawString(50, y - 45, f"Teléfono: {compra['proveedor_telefono']}")
            
            # Línea separadora
            y -= 70
            c.line(50, y, width - 50, y)
            
            # Encabezados de tabla
            y -= 25
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "CÓDIGO")
            c.drawString(120, y, "DESCRIPCIÓN")
            c.drawString(350, y, "CANT.")
            c.drawString(400, y, "PRECIO")
            c.drawString(480, y, "SUBTOTAL")
            
            # Línea de encabezados
            y -= 5
            c.line(50, y, width - 50, y)
            
            # Productos
            y -= 20
            c.setFont("Helvetica", 9)
            for detalle in compra['detalles']:
                if y < 150:
                    c.showPage()
                    y = height - 50
                    c.setFont("Helvetica", 9)
                
                c.drawString(50, y, detalle['producto_codigo'])
                nombre_producto = detalle['producto_nombre']
                if len(nombre_producto) > 30:
                    nombre_producto = nombre_producto[:27] + "..."
                c.drawString(120, y, nombre_producto)
                c.drawString(350, y, str(detalle['cantidad']))
                c.drawString(400, y, f"${detalle['precio_unitario']:,.2f}")
                c.drawString(480, y, f"${detalle['subtotal']:,.2f}")
                y -= 18
            
            # Total
            y -= 20
            c.line(400, y, width - 50, y)
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(400, y, f"TOTAL: ${compra['total']:,.2f}")
            
            # Pie de página
            c.setFont("Helvetica", 8)
            c.drawString(50, 80, f"Orden generada por: {compra['usuario_nombre']}")
            c.drawString(50, 65, f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            
            c.save()
            
            messagebox.showinfo("PDF Generado", 
                              f"Orden generada en:\n{filename}")
            
            # Abrir archivo
            if messagebox.askyesno("Abrir PDF", "¿Desea abrir la orden?"):
                try:
                    os.startfile(filename)
                except:
                    messagebox.showinfo("Información", f"Abra manualmente: {filename}")
                    
        except ImportError:
            messagebox.showerror("Error", "Instale reportlab: pip install reportlab")
        except Exception as e:
            messagebox.showerror("Error", f"Error generando PDF: {str(e)}")
    
    def nueva_orden(self):
        """Prepara una nueva orden"""
        self.carrito.clear()
        self.numero_compra = CompraModel.generar_numero_compra()
        
        # Limpiar interfaz
        self.actualizar_carrito_display()
        self.actualizar_totales()
        self.search_producto_var.set("")
        
        # Actualizar número de orden en título
        title_frame = self.frame.winfo_children()[0]
        numero_label = title_frame.winfo_children()[1]
        numero_label.config(text=f"Orden #: {self.numero_compra}")
    
    def nuevo_proveedor(self):
        """Abre ventana para crear nuevo proveedor"""
        ProveedorFormView(self.frame, self.on_proveedor_creado)
    
    def on_proveedor_creado(self, proveedor):
        """Callback cuando se crea un nuevo proveedor"""
        self.cargar_proveedores()
        # Seleccionar el nuevo proveedor
        display_text = f"{proveedor['nombre']} (0 productos)"
        self.proveedor_var.set(display_text)
    
    def ver_productos_bajo_stock(self):
        """Muestra ventana con productos bajo stock mínimo"""
        ProductosBajoStockView(self.frame)
    
    def cancelar_orden(self):
        """Cancela la orden actual"""
        if len(self.carrito) > 0:
            if messagebox.askyesno("Cancelar", "¿Cancelar la orden actual?"):
                self.nueva_orden()
        else:
            # Si no hay productos en el carrito, simplemente preparar nueva orden
            self.nueva_orden()  