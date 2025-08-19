# src/views/compras_simple.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sys
import os

# Agregar el directorio src al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from models.compra import CompraModel
    from models.producto import ProveedorModel, ProductoModel
except ImportError as e:
    print(f"Error importando modelos: {e}")

class ComprasView:
    def __init__(self, parent, usuario_data):
        self.parent = parent
        self.usuario_data = usuario_data
        self.frame = None
        
        # Variables del carrito
        self.carrito = []
        self.total = 0.0
        self.proveedor_seleccionado = None
        
        self.crear_interfaz()
    
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
        numero_compra = self.generar_numero_compra()
        ttk.Label(title_frame, text=f"Orden #: {numero_compra}", 
                 font=("Arial", 12)).pack(side=tk.RIGHT)
        self.numero_compra = numero_compra
        
        # Crear notebook para organizar mejor
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Nueva Orden
        self.crear_pestaña_nueva_orden()
        
        # Pestaña 2: Productos con Stock Bajo
        self.crear_pestaña_stock_bajo()
    
    def crear_pestaña_nueva_orden(self):
        # Frame para nueva orden
        orden_frame = ttk.Frame(self.notebook)
        self.notebook.add(orden_frame, text="Nueva Orden")
        
        # Dividir en dos columnas
        main_container = ttk.Frame(orden_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Columna izquierda
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Columna derecha
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Sección proveedor
        self.crear_seccion_proveedor(right_frame)
        
        # Sección carrito
        self.crear_seccion_carrito(left_frame)
        
        # Sección totales y botones
        self.crear_seccion_totales(right_frame)
    
    def crear_seccion_proveedor(self, parent):
        # Frame del proveedor
        proveedor_frame = ttk.LabelFrame(parent, text="Proveedor", padding="10")
        proveedor_frame.pack(fill=tk.X, pady=(0, 10))
        proveedor_frame.configure(width=300)
        
        # Selección de proveedor
        ttk.Label(proveedor_frame, text="Seleccionar Proveedor:").pack(anchor=tk.W)
        
        self.proveedor_var = tk.StringVar()
        self.proveedor_combo = ttk.Combobox(proveedor_frame, textvariable=self.proveedor_var, 
                                           state="readonly", width=35)
        self.proveedor_combo.pack(fill=tk.X, pady=(5, 10))
        self.proveedor_combo.bind('<<ComboboxSelected>>', self.on_proveedor_selected)
        
        # Información del proveedor
        self.proveedor_info = ttk.Label(proveedor_frame, text="", justify=tk.LEFT)
        self.proveedor_info.pack(anchor=tk.W, pady=5)
        
        # Botones
        buttons_frame = ttk.Frame(proveedor_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Cargar Proveedores", 
                  command=self.cargar_proveedores).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Nuevo Proveedor", 
                  command=self.nuevo_proveedor).pack(side=tk.LEFT)
        
        # Cargar proveedores automáticamente
        self.cargar_proveedores()
    
    def crear_seccion_carrito(self, parent):
        # Frame del carrito
        carrito_frame = ttk.LabelFrame(parent, text="Productos de la Orden", padding="10")
        carrito_frame.pack(fill=tk.BOTH, expand=True)
        
        # Botones superiores
        top_buttons = ttk.Frame(carrito_frame)
        top_buttons.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(top_buttons, text="Agregar Producto", 
                  command=self.agregar_producto_manual).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_buttons, text="Orden Sugerida", 
                  command=self.generar_orden_sugerida).pack(side=tk.LEFT)
        
        # Tabla del carrito
        columns = ('codigo', 'nombre', 'cantidad', 'precio', 'subtotal')
        self.carrito_tree = ttk.Treeview(carrito_frame, columns=columns, 
                                        show='headings', height=12)
        
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
        
        # Scrollbar
        carrito_scroll = ttk.Scrollbar(carrito_frame, orient=tk.VERTICAL, 
                                      command=self.carrito_tree.yview)
        self.carrito_tree.configure(yscrollcommand=carrito_scroll.set)
        
        self.carrito_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        carrito_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones del carrito
        carrito_buttons = ttk.Frame(carrito_frame)
        carrito_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(carrito_buttons, text="Editar", 
                  command=self.editar_item_carrito).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(carrito_buttons, text="Quitar", 
                  command=self.quitar_item_carrito).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(carrito_buttons, text="Limpiar Todo", 
                  command=self.limpiar_carrito).pack(side=tk.LEFT)
    
    def crear_seccion_totales(self, parent):
        # Frame de totales
        totales_frame = ttk.LabelFrame(parent, text="Total de la Orden", padding="10")
        totales_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Total
        self.total_label = ttk.Label(totales_frame, text="$0.00", 
                                    font=("Arial", 16, "bold"), 
                                    foreground="blue")
        self.total_label.pack(pady=10)
        
        # Información
        self.items_label = ttk.Label(totales_frame, text="0 productos")
        self.items_label.pack()
        
        # Botones principales
        buttons_frame = ttk.Frame(totales_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.btn_crear = ttk.Button(buttons_frame, text="CREAR ORDEN", 
                                   command=self.crear_orden, width=20)
        self.btn_crear.pack(fill=tk.X, pady=(0, 5))
        self.btn_crear.config(state='disabled')
        
        ttk.Button(buttons_frame, text="Nueva Orden", 
                  command=self.nueva_orden, width=20).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(buttons_frame, text="Cancelar", 
                  command=self.cancelar, width=20).pack(fill=tk.X)
    
    def crear_pestaña_stock_bajo(self):
        # Frame para productos con stock bajo
        stock_frame = ttk.Frame(self.notebook)
        self.notebook.add(stock_frame, text="Stock Bajo")
        
        # Título
        ttk.Label(stock_frame, text="Productos con Stock Bajo", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Botón actualizar
        ttk.Button(stock_frame, text="Actualizar Lista", 
                  command=self.cargar_productos_stock_bajo).pack(pady=5)
        
        # Lista de productos
        columns = ('codigo', 'nombre', 'stock', 'minimo', 'proveedor')
        self.stock_tree = ttk.Treeview(stock_frame, columns=columns, 
                                      show='headings', height=15)
        
        # Configurar encabezados
        self.stock_tree.heading('codigo', text='Código')
        self.stock_tree.heading('nombre', text='Producto')
        self.stock_tree.heading('stock', text='Stock')
        self.stock_tree.heading('minimo', text='Mínimo')
        self.stock_tree.heading('proveedor', text='Proveedor')
        
        # Configurar anchos
        self.stock_tree.column('codigo', width=100)
        self.stock_tree.column('nombre', width=250)
        self.stock_tree.column('stock', width=80)
        self.stock_tree.column('minimo', width=80)
        self.stock_tree.column('proveedor', width=150)
        
        self.stock_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cargar automáticamente
        self.cargar_productos_stock_bajo()
    
    def generar_numero_compra(self):
        """Genera número de compra simple"""
        try:
            return CompraModel.generar_numero_compra()
        except:
            # Fallback simple
            return f"OC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    def cargar_proveedores(self):
        """Carga los proveedores"""
        try:
            proveedores = ProveedorModel.obtener_todos()
            
            proveedores_list = [""]
            self.proveedores_data = {}
            
            for proveedor in proveedores:
                display_text = proveedor['nombre']
                proveedores_list.append(display_text)
                self.proveedores_data[display_text] = proveedor
            
            self.proveedor_combo['values'] = proveedores_list
            messagebox.showinfo("Éxito", f"Se cargaron {len(proveedores)} proveedores")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando proveedores: {str(e)}")
    
    def on_proveedor_selected(self, event=None):
        """Cuando se selecciona un proveedor"""
        proveedor_nombre = self.proveedor_var.get()
        
        if proveedor_nombre and proveedor_nombre in self.proveedores_data:
            self.proveedor_seleccionado = self.proveedores_data[proveedor_nombre]
            
            # Mostrar información
            info = f"Contacto: {self.proveedor_seleccionado.get('contacto', 'N/A')}\n"
            info += f"Teléfono: {self.proveedor_seleccionado.get('telefono', 'N/A')}"
            self.proveedor_info.config(text=info)
            
            self.actualizar_botones()
        else:
            self.proveedor_seleccionado = None
            self.proveedor_info.config(text="")
            self.actualizar_botones()
    
    def agregar_producto_manual(self):
        """Agrega un producto manualmente"""
        if not self.proveedor_seleccionado:
            messagebox.showwarning("Advertencia", "Primero seleccione un proveedor")
            return
        
        # Buscar productos del proveedor
        try:
            from models.compra import ProveedorModelExtendido
            productos = ProveedorModelExtendido.obtener_productos_proveedor(
                self.proveedor_seleccionado['id']
            )
            
            if not productos:
                messagebox.showinfo("Información", "Este proveedor no tiene productos asignados")
                return
            
            # Mostrar ventana de selección
            self.mostrar_selector_productos(productos)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error obteniendo productos: {str(e)}")
    
    def mostrar_selector_productos(self, productos):
        """Muestra ventana para seleccionar productos"""
        # Ventana simple de selección
        selector = tk.Toplevel(self.frame)
        selector.title("Seleccionar Producto")
        selector.geometry("600x400")
        selector.transient(self.frame)
        selector.grab_set()
        
        ttk.Label(selector, text="Seleccione un producto:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Lista de productos
        listbox = tk.Listbox(selector, height=15)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for producto in productos:
            listbox.insert(tk.END, f"{producto['codigo']} - {producto['nombre']} (Stock: {producto['stock_actual']})")
        
        def agregar_seleccionado():
            selection = listbox.curselection()
            if selection:
                producto = productos[selection[0]]
                self.agregar_al_carrito(producto)
                selector.destroy()
            else:
                messagebox.showwarning("Advertencia", "Seleccione un producto")
        
        ttk.Button(selector, text="Agregar", command=agregar_seleccionado).pack(pady=10)
        ttk.Button(selector, text="Cancelar", command=selector.destroy).pack()
    
    def agregar_al_carrito(self, producto):
        """Agrega producto al carrito"""
        # Pedir cantidad
        cantidad = simpledialog.askinteger(
            "Cantidad",
            f"Cantidad a ordenar de {producto['nombre']}:",
            initialvalue=max(producto['stock_minimo'] - producto['stock_actual'], 1),
            minvalue=1
        )
        
        if not cantidad:
            return
        
        # Pedir precio si no existe
        precio_compra = producto.get('precio_compra', 0)
        if precio_compra == 0:
            precio_str = simpledialog.askstring(
                "Precio",
                f"Precio de compra para {producto['nombre']}:",
                initialvalue="0.00"
            )
            try:
                precio_compra = float(precio_str)
            except:
                messagebox.showerror("Error", "Precio inválido")
                return
        
        # Agregar al carrito
        item = {
            'producto_id': producto['id'],
            'codigo': producto['codigo'],
            'nombre': producto['nombre'],
            'cantidad': cantidad,
            'precio_unitario': precio_compra,
            'subtotal': cantidad * precio_compra
        }
        
        self.carrito.append(item)
        self.actualizar_carrito_display()
        self.actualizar_totales()
    
    def actualizar_carrito_display(self):
        """Actualiza la vista del carrito"""
        # Limpiar
        for item in self.carrito_tree.get_children():
            self.carrito_tree.delete(item)
        
        # Llenar
        for item in self.carrito:
            self.carrito_tree.insert('', tk.END, values=(
                item['codigo'],
                item['nombre'],
                item['cantidad'],
                f"${item['precio_unitario']:,.2f}",
                f"${item['subtotal']:,.2f}"
            ))
    
    def actualizar_totales(self):
        """Actualiza los totales"""
        self.total = sum(item['subtotal'] for item in self.carrito)
        self.total_label.config(text=f"${self.total:,.2f}")
        self.items_label.config(text=f"{len(self.carrito)} productos")
        self.actualizar_botones()
    
    def actualizar_botones(self):
        """Actualiza estado de botones"""
        if len(self.carrito) > 0 and self.proveedor_seleccionado:
            self.btn_crear.config(state='normal')
        else:
            self.btn_crear.config(state='disabled')
    
    def editar_item_carrito(self):
        """Edita item del carrito"""
        selected = self.carrito_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        # Implementar edición básica
        messagebox.showinfo("Info", "Función de edición en desarrollo")
    
    def quitar_item_carrito(self):
        """Quita item del carrito"""
        selected = self.carrito_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        item_index = self.carrito_tree.index(selected[0])
        if messagebox.askyesno("Confirmar", "¿Quitar este producto?"):
            del self.carrito[item_index]
            self.actualizar_carrito_display()
            self.actualizar_totales()
    
    def limpiar_carrito(self):
        """Limpia el carrito"""
        if len(self.carrito) > 0:
            if messagebox.askyesno("Confirmar", "¿Limpiar toda la orden?"):
                self.carrito.clear()
                self.actualizar_carrito_display()
                self.actualizar_totales()
    
    def generar_orden_sugerida(self):
        """Genera orden sugerida"""
        if not self.proveedor_seleccionado:
            messagebox.showwarning("Advertencia", "Primero seleccione un proveedor")
            return
        
        try:
            sugerencias = CompraModel.generar_orden_sugerida(self.proveedor_seleccionado['id'])
            
            if not sugerencias:
                messagebox.showinfo("Información", "No hay productos con stock bajo para este proveedor")
                return
            
            # Agregar sugerencias al carrito
            for sugerencia in sugerencias:
                item = {
                    'producto_id': sugerencia['producto_id'],
                    'codigo': sugerencia['codigo'],
                    'nombre': sugerencia['nombre'],
                    'cantidad': sugerencia['cantidad_sugerida'],
                    'precio_unitario': sugerencia['precio_compra'],
                    'subtotal': sugerencia['cantidad_sugerida'] * sugerencia['precio_compra']
                }
                self.carrito.append(item)
            
            self.actualizar_carrito_display()
            self.actualizar_totales()
            
            messagebox.showinfo("Éxito", f"Se agregaron {len(sugerencias)} productos sugeridos")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando sugerencias: {str(e)}")
    
    def cargar_productos_stock_bajo(self):
        """Carga productos con stock bajo"""
        try:
            productos = CompraModel.obtener_productos_bajo_minimo()
            
            # Limpiar
            for item in self.stock_tree.get_children():
                self.stock_tree.delete(item)
            
            # Llenar
            for producto in productos:
                tags = ()
                if producto['stock_actual'] <= 0:
                    tags = ('critico',)
                elif producto['stock_actual'] <= producto['stock_minimo']:
                    tags = ('bajo',)
                
                self.stock_tree.insert('', tk.END, values=(
                    producto['codigo'],
                    producto['nombre'],
                    producto['stock_actual'],
                    producto['stock_minimo'],
                    producto['proveedor_nombre'] or 'Sin proveedor'
                ), tags=tags)
            
            # Colores
            self.stock_tree.tag_configure('critico', background='#ffcccc')
            self.stock_tree.tag_configure('bajo', background='#fff2cc')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando productos: {str(e)}")
    
    def crear_orden(self):
        """Crea la orden de compra"""
        if not self.proveedor_seleccionado or len(self.carrito) == 0:
            messagebox.showwarning("Advertencia", "Complete la orden")
            return
        
        # Confirmar
        if not messagebox.askyesno("Confirmar", 
                                  f"¿Crear orden por ${self.total:,.2f}?"):
            return
        
        try:
            # Preparar datos
            datos_compra = {
                'numero_compra': self.numero_compra,
                'proveedor_id': self.proveedor_seleccionado['id'],
                'usuario_id': self.usuario_data['id'],
                'fecha_compra': datetime.now(),
                'total': self.total
            }
            
            detalle_items = []
            for item in self.carrito:
                detalle_items.append({
                    'producto_id': item['producto_id'],
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio_unitario'],
                    'subtotal': item['subtotal']
                })
            
            # Crear orden
            compra_id = CompraModel.crear_compra(datos_compra, detalle_items)
            
            if compra_id:
                messagebox.showinfo("Éxito", 
                                  f"Orden creada exitosamente\n"
                                  f"Número: {self.numero_compra}\n"
                                  f"Total: ${self.total:,.2f}")
                self.nueva_orden()
            else:
                messagebox.showerror("Error", "No se pudo crear la orden")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error creando orden: {str(e)}")
    
    def nueva_orden(self):
        """Prepara nueva orden"""
        self.carrito.clear()
        self.proveedor_seleccionado = None
        self.numero_compra = self.generar_numero_compra()
        
        # Limpiar interfaz
        self.proveedor_var.set("")
        self.proveedor_info.config(text="")
        self.actualizar_carrito_display()
        self.actualizar_totales()
        
        # Actualizar título
        title_frame = self.frame.winfo_children()[0]
        numero_label = title_frame.winfo_children()[1]
        numero_label.config(text=f"Orden #: {self.numero_compra}")
    
    def nuevo_proveedor(self):
        """Crear nuevo proveedor - versión simple"""
        messagebox.showinfo("Info", "Función de nuevo proveedor en desarrollo")
    
    def cancelar(self):
        """Cancela la orden"""
        if len(self.carrito) > 0:
            if messagebox.askyesno("Cancelar", "¿Cancelar la orden actual?"):
                self.nueva_orden()
        else:
            messagebox.showinfo("Info", "No hay orden que cancelar")