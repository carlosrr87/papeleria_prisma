# src/views/productos_view.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.producto import ProductoModel, CategoriaModel, ProveedorModel

class ProductosView:
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.tree = None
        self.productos_data = []
        self.categorias_data = []
        self.proveedores_data = []
        
        # Variables de búsqueda
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.category_var.trace('w', self.on_search_change)
        
        self.crear_interfaz()
        self.cargar_datos_iniciales()
    
    def crear_interfaz(self):
        # Frame principal
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="Gestión de Productos", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Frame de controles superiores
        controls_frame = ttk.Frame(self.frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Búsqueda
        search_frame = ttk.LabelFrame(controls_frame, text="Búsqueda y Filtros", padding="5")
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Búsqueda por texto
        ttk.Label(search_frame, text="Buscar:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky="w", padx=(0, 10))
        
        # Filtro por categoría
        ttk.Label(search_frame, text="Categoría:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.category_combo = ttk.Combobox(search_frame, textvariable=self.category_var, 
                                          state="readonly", width=20)
        self.category_combo.grid(row=0, column=3, sticky="w")
        
        # Botones de acción
        buttons_frame = ttk.LabelFrame(controls_frame, text="Acciones", padding="5")
        buttons_frame.pack(side=tk.RIGHT)
        
        ttk.Button(buttons_frame, text="Nuevo Producto", 
                  command=self.nuevo_producto).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Editar", 
                  command=self.editar_producto).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Eliminar", 
                  command=self.eliminar_producto).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Actualizar", 
                  command=self.cargar_productos).pack(side=tk.LEFT)
        
        # Frame para la tabla
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear Treeview con scrollbars
        self.crear_tabla(table_frame)
        
        # Frame de información inferior
        info_frame = ttk.Frame(self.frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.info_label = ttk.Label(info_frame, text="Total de productos: 0")
        self.info_label.pack(side=tk.LEFT)
        
        # Botón de categorías
        ttk.Button(info_frame, text="Gestionar Categorías", 
                  command=self.gestionar_categorias).pack(side=tk.RIGHT)
    
    def crear_tabla(self, parent):
        # Configurar columnas
        columns = ('codigo', 'nombre', 'categoria', 'precio_venta', 'stock_actual', 
                  'stock_minimo', 'estado')
        
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        # Configurar encabezados
        self.tree.heading('codigo', text='Código')
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('categoria', text='Categoría')
        self.tree.heading('precio_venta', text='Precio Venta')
        self.tree.heading('stock_actual', text='Stock Actual')
        self.tree.heading('stock_minimo', text='Stock Mínimo')
        self.tree.heading('estado', text='Estado')
        
        # Configurar anchos de columna
        self.tree.column('codigo', width=100)
        self.tree.column('nombre', width=250)
        self.tree.column('categoria', width=150)
        self.tree.column('precio_venta', width=100)
        self.tree.column('stock_actual', width=100)
        self.tree.column('stock_minimo', width=100)
        self.tree.column('estado', width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Posicionar elementos
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configurar grid weights
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Bind doble click
        self.tree.bind('<Double-1>', lambda e: self.editar_producto())
    
    def cargar_datos_iniciales(self):
        self.cargar_categorias()
        self.cargar_productos()
    
    def cargar_categorias(self):
        """Carga las categorías en el combobox"""
        self.categorias_data = CategoriaModel.obtener_todas()
        
        # Preparar datos para el combobox
        categorias_list = ["Todas las categorías"]
        for categoria in self.categorias_data:
            categorias_list.append(categoria['nombre'])
        
        self.category_combo['values'] = categorias_list
        if not self.category_var.get():
            self.category_var.set("Todas las categorías")
    
    def cargar_productos(self):
        """Carga los productos en la tabla"""
        # Obtener filtros
        filtro_texto = self.search_var.get()
        categoria_seleccionada = self.category_var.get()
        categoria_id = None
        
        if categoria_seleccionada and categoria_seleccionada != "Todas las categorías":
            for cat in self.categorias_data:
                if cat['nombre'] == categoria_seleccionada:
                    categoria_id = cat['id']
                    break
        
        # Obtener productos
        self.productos_data = ProductoModel.obtener_todos(filtro_texto, categoria_id)
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Llenar tabla
        for producto in self.productos_data:
            # Determinar color según stock
            estado = "Normal"
            tags = ()
            
            if producto['stock_actual'] <= 0:
                estado = "Sin Stock"
                tags = ('sin_stock',)
            elif producto['stock_actual'] <= producto['stock_minimo']:
                estado = "Stock Bajo"
                tags = ('stock_bajo',)
            
            self.tree.insert('', tk.END, values=(
                producto['codigo'],
                producto['nombre'],
                producto['categoria_nombre'] or 'Sin categoría',
                f"${producto['precio_venta']:,.2f}",
                producto['stock_actual'],
                producto['stock_minimo'],
                estado
            ), tags=tags)
        
        # Configurar colores
        self.tree.tag_configure('sin_stock', background='#ffcccc')
        self.tree.tag_configure('stock_bajo', background='#fff2cc')
        
        # Actualizar información
        self.info_label.config(text=f"Total de productos: {len(self.productos_data)}")
    
    def on_search_change(self, *args):
        """Se ejecuta cuando cambian los filtros de búsqueda"""
        self.cargar_productos()
    
    def nuevo_producto(self):
        """Abre ventana para crear nuevo producto"""
        ProductoFormView(self.frame, self.cargar_productos)
    
    def editar_producto(self):
        """Abre ventana para editar producto seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return
        
        # Obtener índice del producto seleccionado
        item = self.tree.item(selected[0])
        codigo = item['values'][0]
        
        # Buscar producto en los datos
        producto = None
        for p in self.productos_data:
            if p['codigo'] == codigo:
                producto = p
                break
        
        if producto:
            ProductoFormView(self.frame, self.cargar_productos, producto)
    
    def eliminar_producto(self):
        """Elimina (desactiva) el producto seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
        
        item = self.tree.item(selected[0])
        codigo = item['values'][0]
        nombre = item['values'][1]
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Está seguro de eliminar el producto '{nombre}'?\n"
                              "El producto será desactivado pero mantendrá su historial."):
            
            # Buscar ID del producto
            for producto in self.productos_data:
                if producto['codigo'] == codigo:
                    if ProductoModel.eliminar(producto['id']):
                        messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                        self.cargar_productos()
                    else:
                        messagebox.showerror("Error", "No se pudo eliminar el producto")
                    break
    
    def gestionar_categorias(self):
        """Abre ventana para gestionar categorías"""
        CategoriasView(self.frame, self.cargar_categorias)

class ProductoFormView:
    def __init__(self, parent, callback, producto=None):
        self.parent = parent
        self.callback = callback
        self.producto = producto
        self.is_edit = producto is not None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Editar Producto" if self.is_edit else "Nuevo Producto")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables
        self.codigo_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.descripcion_var = tk.StringVar()
        self.categoria_var = tk.StringVar()
        self.proveedor_var = tk.StringVar()
        self.precio_compra_var = tk.StringVar()
        self.precio_venta_var = tk.StringVar()
        self.stock_actual_var = tk.StringVar()
        self.stock_minimo_var = tk.StringVar()
        
        self.crear_interfaz()
        self.cargar_datos()
        
        if self.is_edit:
            self.llenar_datos()
        
        # Centrar ventana
        self.center_window()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"500x600+{x}+{y}")
    
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = "Editar Producto" if self.is_edit else "Nuevo Producto"
        ttk.Label(main_frame, text=title, font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Código
        ttk.Label(form_frame, text="* Código:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.codigo_var, width=30).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Nombre
        ttk.Label(form_frame, text="* Nombre:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.nombre_var, width=30).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.descripcion_var, width=30).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Categoría
        ttk.Label(form_frame, text="Categoría:").grid(row=row, column=0, sticky="w", pady=5)
        self.categoria_combo = ttk.Combobox(form_frame, textvariable=self.categoria_var, 
                                           state="readonly", width=27)
        self.categoria_combo.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Proveedor
        ttk.Label(form_frame, text="Proveedor:").grid(row=row, column=0, sticky="w", pady=5)
        self.proveedor_combo = ttk.Combobox(form_frame, textvariable=self.proveedor_var, 
                                           state="readonly", width=27)
        self.proveedor_combo.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Precio de compra
        ttk.Label(form_frame, text="Precio Compra:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.precio_compra_var, width=30).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Precio de venta
        ttk.Label(form_frame, text="* Precio Venta:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.precio_venta_var, width=30).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Stock actual
        ttk.Label(form_frame, text="Stock Actual:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.stock_actual_var, width=30).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Stock mínimo
        ttk.Label(form_frame, text="Stock Mínimo:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.stock_minimo_var, width=30).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Nota
        ttk.Label(form_frame, text="* Campos obligatorios", 
                 font=("Arial", 8)).grid(row=row, column=0, columnspan=2, pady=(20, 10))
        row += 1
        
        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Guardar", 
                  command=self.guardar).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.window.destroy).pack(side=tk.LEFT)
    
    def cargar_datos(self):
        # Cargar categorías
        categorias = CategoriaModel.obtener_todas()
        categorias_list = [""]
        for cat in categorias:
            categorias_list.append(cat['nombre'])
        self.categoria_combo['values'] = categorias_list
        
        # Cargar proveedores
        proveedores = ProveedorModel.obtener_todos()
        proveedores_list = [""]
        for prov in proveedores:
            proveedores_list.append(prov['nombre'])
        self.proveedor_combo['values'] = proveedores_list
    
    def llenar_datos(self):
        """Llena el formulario con datos del producto a editar"""
        if self.producto:
            self.codigo_var.set(self.producto['codigo'])
            self.nombre_var.set(self.producto['nombre'])
            self.descripcion_var.set(self.producto['descripcion'] or '')
            self.categoria_var.set(self.producto['categoria_nombre'] or '')
            self.proveedor_var.set(self.producto['proveedor_nombre'] or '')
            self.precio_compra_var.set(str(self.producto['precio_compra'] or ''))
            self.precio_venta_var.set(str(self.producto['precio_venta']))
            self.stock_actual_var.set(str(self.producto['stock_actual']))
            self.stock_minimo_var.set(str(self.producto['stock_minimo']))
    
    def validar_datos(self):
        """Valida los datos del formulario"""
        # Campos obligatorios
        if not self.codigo_var.get().strip():
            messagebox.showerror("Error", "El código es obligatorio")
            return False
        
        if not self.nombre_var.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return False
        
        # Validar precio de venta
        try:
            precio_venta = float(self.precio_venta_var.get())
            if precio_venta <= 0:
                messagebox.showerror("Error", "El precio de venta debe ser mayor a 0")
                return False
        except ValueError:
            messagebox.showerror("Error", "El precio de venta debe ser un número válido")
            return False
        
        # Validar precios y stocks
        try:
            if self.precio_compra_var.get():
                float(self.precio_compra_var.get())
        except ValueError:
            messagebox.showerror("Error", "El precio de compra debe ser un número válido")
            return False
        
        try:
            if self.stock_actual_var.get():
                int(self.stock_actual_var.get())
        except ValueError:
            messagebox.showerror("Error", "El stock actual debe ser un número entero")
            return False
        
        try:
            if self.stock_minimo_var.get():
                int(self.stock_minimo_var.get())
        except ValueError:
            messagebox.showerror("Error", "El stock mínimo debe ser un número entero")
            return False
        
        # Verificar código único
        if not ProductoModel.verificar_codigo_unico(
            self.codigo_var.get().strip(), 
            self.producto['id'] if self.is_edit else None
        ):
            messagebox.showerror("Error", "Ya existe un producto con este código")
            return False
        
        return True
    
    def guardar(self):
        """Guarda el producto"""
        if not self.validar_datos():
            return
        
        # Buscar IDs de categoría y proveedor
        categoria_id = None
        if self.categoria_var.get():
            categorias = CategoriaModel.obtener_todas()
            for cat in categorias:
                if cat['nombre'] == self.categoria_var.get():
                    categoria_id = cat['id']
                    break
        
        proveedor_id = None
        if self.proveedor_var.get():
            proveedores = ProveedorModel.obtener_todos()
            for prov in proveedores:
                if prov['nombre'] == self.proveedor_var.get():
                    proveedor_id = prov['id']
                    break
        
        # Preparar datos
        datos = {
            'codigo': self.codigo_var.get().strip(),
            'nombre': self.nombre_var.get().strip(),
            'descripcion': self.descripcion_var.get().strip(),
            'categoria_id': categoria_id,
            'proveedor_id': proveedor_id,
            'precio_compra': float(self.precio_compra_var.get()) if self.precio_compra_var.get() else 0,
            'precio_venta': float(self.precio_venta_var.get()),
            'stock_actual': int(self.stock_actual_var.get()) if self.stock_actual_var.get() else 0,
            'stock_minimo': int(self.stock_minimo_var.get()) if self.stock_minimo_var.get() else 5
        }
        
        try:
            if self.is_edit:
                # Actualizar producto
                if ProductoModel.actualizar(self.producto['id'], datos):
                    messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                    self.callback()
                    self.window.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el producto")
            else:
                # Crear nuevo producto
                if ProductoModel.crear(datos):
                    messagebox.showinfo("Éxito", "Producto creado correctamente")
                    self.callback()
                    self.window.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo crear el producto")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

class CategoriasView:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Categorías")
        self.window.geometry("600x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.categorias_data = []
        self.crear_interfaz()
        self.cargar_categorias()
        self.center_window()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"600x400+{x}+{y}")
    
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Gestión de Categorías", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Botones superiores
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Nueva Categoría", 
                  command=self.nueva_categoria).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Editar", 
                  command=self.editar_categoria).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Eliminar", 
                  command=self.eliminar_categoria).pack(side=tk.LEFT)
        
        # Lista de categorías
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('nombre', 'descripcion', 'productos')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('descripcion', text='Descripción')
        self.tree.heading('productos', text='Productos')
        
        self.tree.column('nombre', width=200)
        self.tree.column('descripcion', width=300)
        self.tree.column('productos', width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=self.cerrar).pack(pady=(10, 0))
        
        # Bind doble click
        self.tree.bind('<Double-1>', lambda e: self.editar_categoria())
    
    def cargar_categorias(self):
        """Carga las categorías en la lista"""
        self.categorias_data = CategoriaModel.obtener_todas()
        
        # Limpiar lista
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Llenar lista
        for categoria in self.categorias_data:
            # Contar productos en esta categoría
            productos = ProductoModel.obtener_todos(categoria_id=categoria['id'])
            count_productos = len(productos)
            
            self.tree.insert('', tk.END, values=(
                categoria['nombre'],
                categoria['descripcion'] or '',
                count_productos
            ))
    
    def nueva_categoria(self):
        """Crear nueva categoría"""
        CategoriaFormView(self.window, self.cargar_categorias)
    
    def editar_categoria(self):
        """Editar categoría seleccionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una categoría para editar")
            return
        
        item = self.tree.item(selected[0])
        nombre = item['values'][0]
        
        # Buscar categoría en los datos
        categoria = None
        for cat in self.categorias_data:
            if cat['nombre'] == nombre:
                categoria = cat
                break
        
        if categoria:
            CategoriaFormView(self.window, self.cargar_categorias, categoria)
    
    def eliminar_categoria(self):
        """Eliminar categoría seleccionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una categoría para eliminar")
            return
        
        item = self.tree.item(selected[0])
        nombre = item['values'][0]
        productos_count = item['values'][2]
        
        if productos_count > 0:
            messagebox.showerror("Error", 
                               f"No se puede eliminar la categoría '{nombre}' "
                               f"porque tiene {productos_count} productos asociados")
            return
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Está seguro de eliminar la categoría '{nombre}'?"):
            
            # Buscar ID de la categoría
            for categoria in self.categorias_data:
                if categoria['nombre'] == nombre:
                    if CategoriaModel.eliminar(categoria['id']):
                        messagebox.showinfo("Éxito", "Categoría eliminada correctamente")
                        self.cargar_categorias()
                    else:
                        messagebox.showerror("Error", "No se pudo eliminar la categoría")
                    break
    
    def cerrar(self):
        """Cerrar ventana y actualizar callback"""
        self.callback()
        self.window.destroy()

class CategoriaFormView:
    def __init__(self, parent, callback, categoria=None):
        self.parent = parent
        self.callback = callback
        self.categoria = categoria
        self.is_edit = categoria is not None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Editar Categoría" if self.is_edit else "Nueva Categoría")
        self.window.geometry("400x250")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables
        self.nombre_var = tk.StringVar()
        self.descripcion_var = tk.StringVar()
        
        self.crear_interfaz()
        
        if self.is_edit:
            self.llenar_datos()
        
        self.center_window()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (250 // 2)
        self.window.geometry(f"400x250+{x}+{y}")
    
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = "Editar Categoría" if self.is_edit else "Nueva Categoría"
        ttk.Label(main_frame, text=title, font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X)
        
        # Nombre
        ttk.Label(form_frame, text="* Nombre:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.nombre_var, width=30).grid(row=0, column=1, sticky="w", pady=5)
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.descripcion_var, width=30).grid(row=1, column=1, sticky="w", pady=5)
        
        # Nota
        ttk.Label(form_frame, text="* Campo obligatorio", 
                 font=("Arial", 8)).grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Guardar", 
                  command=self.guardar).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.window.destroy).pack(side=tk.LEFT)
    
    def llenar_datos(self):
        """Llena el formulario con datos de la categoría a editar"""
        if self.categoria:
            self.nombre_var.set(self.categoria['nombre'])
            self.descripcion_var.set(self.categoria['descripcion'] or '')
    
    def guardar(self):
        """Guarda la categoría"""
        nombre = self.nombre_var.get().strip()
        descripcion = self.descripcion_var.get().strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        try:
            if self.is_edit:
                # Actualizar categoría
                if CategoriaModel.actualizar(self.categoria['id'], nombre, descripcion):
                    messagebox.showinfo("Éxito", "Categoría actualizada correctamente")
                    self.callback()
                    self.window.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar la categoría")
            else:
                # Crear nueva categoría
                if CategoriaModel.crear(nombre, descripcion):
                    messagebox.showinfo("Éxito", "Categoría creada correctamente")
                    self.callback()
                    self.window.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo crear la categoría")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")