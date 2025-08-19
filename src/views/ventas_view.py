# src/views/ventas_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.venta import VentaModel, ClienteModel
from models.producto import ProductoModel

class VentasView:
    def __init__(self, parent, usuario_data):
        self.parent = parent
        self.usuario_data = usuario_data
        self.frame = None
        
        # Variables del carrito
        self.carrito = []
        self.subtotal = 0.0
        self.impuesto = 0.0
        self.total = 0.0
        
        # Variables de la interfaz
        self.cliente_seleccionado = None
        self.search_producto_var = tk.StringVar()
        self.search_cliente_var = tk.StringVar()
        
        # Configurar eventos de búsqueda
        self.search_producto_var.trace('w', self.buscar_productos)
        self.search_cliente_var.trace('w', self.buscar_clientes)
        
        self.crear_interfaz()
        self.actualizar_totales()
    
    def crear_interfaz(self):
        # Frame principal
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Nueva Venta", 
                 font=("Arial", 18, "bold")).pack(side=tk.LEFT)
        
        # Número de venta
        numero_venta = VentaModel.generar_numero_venta()
        ttk.Label(title_frame, text=f"Venta #: {numero_venta}", 
                 font=("Arial", 12)).pack(side=tk.RIGHT)
        self.numero_venta = numero_venta
        
        # Frame principal dividido en dos columnas
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Columna izquierda - Productos y carrito
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Columna derecha - Cliente y totales
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Crear secciones
        self.crear_seccion_productos(left_frame)
        self.crear_seccion_carrito(left_frame)
        self.crear_seccion_cliente(right_frame)
        self.crear_seccion_totales(right_frame)
        self.crear_botones_accion(right_frame)
    
    def crear_seccion_productos(self, parent):
        # Frame para búsqueda de productos
        productos_frame = ttk.LabelFrame(parent, text="Buscar Productos", padding="10")
        productos_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Búsqueda
        search_frame = ttk.Frame(productos_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_producto_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        search_entry.focus()
        
        # Lista de productos
        self.productos_frame = ttk.Frame(productos_frame)
        self.productos_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear Treeview para productos
        columns = ('codigo', 'nombre', 'precio', 'stock')
        self.productos_tree = ttk.Treeview(self.productos_frame, columns=columns, 
                                          show='headings', height=8)
        
        # Configurar encabezados
        self.productos_tree.heading('codigo', text='Código')
        self.productos_tree.heading('nombre', text='Nombre')
        self.productos_tree.heading('precio', text='Precio')
        self.productos_tree.heading('stock', text='Stock')
        
        # Configurar anchos
        self.productos_tree.column('codigo', width=100)
        self.productos_tree.column('nombre', width=250)
        self.productos_tree.column('precio', width=80)
        self.productos_tree.column('stock', width=80)
        
        # Scrollbar para productos
        productos_scroll = ttk.Scrollbar(self.productos_frame, orient=tk.VERTICAL, 
                                        command=self.productos_tree.yview)
        self.productos_tree.configure(yscrollcommand=productos_scroll.set)
        
        self.productos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        productos_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind doble click para agregar producto
        self.productos_tree.bind('<Double-1>', self.agregar_producto_doble_click)
        self.productos_tree.bind('<Return>', self.agregar_producto_doble_click)
        
        # Botón agregar
        ttk.Button(productos_frame, text="Agregar al Carrito", 
                  command=self.agregar_producto).pack(pady=(10, 0))
    
    def crear_seccion_carrito(self, parent):
        # Frame del carrito
        carrito_frame = ttk.LabelFrame(parent, text="Carrito de Compras", padding="10")
        carrito_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Crear Treeview para carrito
        columns = ('codigo', 'nombre', 'cantidad', 'precio', 'subtotal')
        self.carrito_tree = ttk.Treeview(carrito_frame, columns=columns, 
                                        show='headings', height=10)
        
        # Configurar encabezados
        self.carrito_tree.heading('codigo', text='Código')
        self.carrito_tree.heading('nombre', text='Producto')
        self.carrito_tree.heading('cantidad', text='Cant.')
        self.carrito_tree.heading('precio', text='Precio')
        self.carrito_tree.heading('subtotal', text='Subtotal')
        
        # Configurar anchos
        self.carrito_tree.column('codigo', width=100)
        self.carrito_tree.column('nombre', width=200)
        self.carrito_tree.column('cantidad', width=60)
        self.carrito_tree.column('precio', width=80)
        self.carrito_tree.column('subtotal', width=80)
        
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
        ttk.Button(carrito_buttons, text="Quitar Producto", 
                  command=self.quitar_producto).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(carrito_buttons, text="Limpiar Carrito", 
                  command=self.limpiar_carrito).pack(side=tk.LEFT)
    
    def crear_seccion_cliente(self, parent):
        # Frame del cliente
        cliente_frame = ttk.LabelFrame(parent, text="Cliente", padding="10")
        cliente_frame.pack(fill=tk.X, pady=(0, 10))
        cliente_frame.configure(width=300)
        
        # Búsqueda de cliente
        ttk.Label(cliente_frame, text="Buscar Cliente:").pack(anchor=tk.W)
        
        search_cliente_frame = ttk.Frame(cliente_frame)
        search_cliente_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.cliente_entry = ttk.Entry(search_cliente_frame, textvariable=self.search_cliente_var)
        self.cliente_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(search_cliente_frame, text="Nuevo", 
                  command=self.nuevo_cliente, width=8).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Lista de clientes encontrados
        self.clientes_listbox = tk.Listbox(cliente_frame, height=6)
        self.clientes_listbox.pack(fill=tk.X, pady=(0, 10))
        self.clientes_listbox.bind('<Double-1>', self.seleccionar_cliente)
        
        # Cliente seleccionado
        self.cliente_info_frame = ttk.Frame(cliente_frame)
        self.cliente_info_frame.pack(fill=tk.X)
        
        self.cliente_info_label = ttk.Label(self.cliente_info_frame, 
                                           text="Cliente: Venta General", 
                                           font=("Arial", 10, "bold"))
        self.cliente_info_label.pack(anchor=tk.W)
        
        ttk.Button(self.cliente_info_frame, text="Quitar Cliente", 
                  command=self.quitar_cliente).pack(anchor=tk.W, pady=(5, 0))
    
    def crear_seccion_totales(self, parent):
        # Frame de totales
        totales_frame = ttk.LabelFrame(parent, text="Totales", padding="10")
        totales_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Subtotal
        subtotal_frame = ttk.Frame(totales_frame)
        subtotal_frame.pack(fill=tk.X, pady=2)
        ttk.Label(subtotal_frame, text="Subtotal:").pack(side=tk.LEFT)
        self.subtotal_label = ttk.Label(subtotal_frame, text="$0.00", 
                                       font=("Arial", 10, "bold"))
        self.subtotal_label.pack(side=tk.RIGHT)
        
        # Impuesto (opcional)
        impuesto_frame = ttk.Frame(totales_frame)
        impuesto_frame.pack(fill=tk.X, pady=2)
        ttk.Label(impuesto_frame, text="Impuesto (0%):").pack(side=tk.LEFT)
        self.impuesto_label = ttk.Label(impuesto_frame, text="$0.00")
        self.impuesto_label.pack(side=tk.RIGHT)
        
        # Separador
        ttk.Separator(totales_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Total
        total_frame = ttk.Frame(totales_frame)
        total_frame.pack(fill=tk.X, pady=2)
        ttk.Label(total_frame, text="TOTAL:", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.total_label = ttk.Label(total_frame, text="$0.00", 
                                    font=("Arial", 14, "bold"), 
                                    foreground="green")
        self.total_label.pack(side=tk.RIGHT)
    
    def crear_botones_accion(self, parent):
        # Frame de botones
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botón procesar venta (grande y destacado)
        self.btn_procesar = ttk.Button(buttons_frame, text="PROCESAR VENTA", 
                                      command=self.procesar_venta,
                                      style="Accent.TButton")
        self.btn_procesar.pack(fill=tk.X, pady=(0, 10))
        
        # Otros botones
        ttk.Button(buttons_frame, text="Nueva Venta", 
                  command=self.nueva_venta).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(buttons_frame, text="Cancelar", 
                  command=self.cancelar_venta).pack(fill=tk.X)
    
    def buscar_productos(self, *args):
        """Busca productos según el texto ingresado"""
        texto = self.search_producto_var.get().strip()
        
        # Limpiar lista
        for item in self.productos_tree.get_children():
            self.productos_tree.delete(item)
        
        if len(texto) < 2:
            return
        
        # Buscar productos
        productos = ProductoModel.obtener_todos(filtro_texto=texto)
        
        for producto in productos:
            # Determinar color según stock
            tags = ()
            if producto['stock_actual'] <= 0:
                tags = ('sin_stock',)
            elif producto['stock_actual'] <= producto['stock_minimo']:
                tags = ('stock_bajo',)
            
            self.productos_tree.insert('', tk.END, values=(
                producto['codigo'],
                producto['nombre'],
                f"${producto['precio_venta']:,.2f}",
                producto['stock_actual']
            ), tags=tags)
        
        # Configurar colores
        self.productos_tree.tag_configure('sin_stock', background='#ffcccc')
        self.productos_tree.tag_configure('stock_bajo', background='#fff2cc')
    
    def buscar_clientes(self, *args):
        """Busca clientes según el texto ingresado"""
        texto = self.search_cliente_var.get().strip()
        
        # Limpiar listbox
        self.clientes_listbox.delete(0, tk.END)
        
        if len(texto) < 2:
            return
        
        # Buscar clientes
        clientes = ClienteModel.buscar_clientes(texto)
        
        for cliente in clientes:
            display_text = f"{cliente['nombre']}"
            if cliente['documento']:
                display_text += f" - {cliente['documento']}"
            
            self.clientes_listbox.insert(tk.END, display_text)
            # Guardar referencia del cliente
            self.clientes_listbox.insert(tk.END, cliente)
            self.clientes_listbox.delete(tk.END)  # Solo mantener el texto visible
    
    def agregar_producto_doble_click(self, event=None):
        """Agregar producto con doble click"""
        self.agregar_producto()
    
    def agregar_producto(self):
        """Agrega el producto seleccionado al carrito"""
        selected = self.productos_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        item = self.productos_tree.item(selected[0])
        codigo = item['values'][0]
        nombre = item['values'][1]
        precio_text = item['values'][2].replace('$', '').replace(',', '')
        stock = int(item['values'][3])
        
        if stock <= 0:
            messagebox.showerror("Error", "El producto no tiene stock disponible")
            return
        
        # Obtener producto completo
        producto = ProductoModel.obtener_por_codigo(codigo)
        if not producto:
            messagebox.showerror("Error", "No se pudo obtener la información del producto")
            return
        
        # Verificar si ya está en el carrito
        for i, item_carrito in enumerate(self.carrito):
            if item_carrito['producto_id'] == producto['id']:
                # Aumentar cantidad
                nueva_cantidad = item_carrito['cantidad'] + 1
                if nueva_cantidad > stock:
                    messagebox.showerror("Error", f"Stock insuficiente. Disponible: {stock}")
                    return
                
                self.carrito[i]['cantidad'] = nueva_cantidad
                self.carrito[i]['subtotal'] = nueva_cantidad * item_carrito['precio_unitario']
                self.actualizar_carrito_display()
                self.actualizar_totales()
                return
        
        # Agregar nuevo producto al carrito
        cantidad = 1
        precio = float(precio_text)
        
        item_carrito = {
            'producto_id': producto['id'],
            'codigo': codigo,
            'nombre': nombre,
            'cantidad': cantidad,
            'precio_unitario': precio,
            'subtotal': cantidad * precio,
            'stock_disponible': stock
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
        """Actualiza los totales de la venta"""
        self.subtotal = sum(item['subtotal'] for item in self.carrito)
        self.impuesto = 0.0  # Puedes agregar lógica de impuestos aquí
        self.total = self.subtotal + self.impuesto
        
        # Actualizar labels
        self.subtotal_label.config(text=f"${self.subtotal:,.2f}")
        self.impuesto_label.config(text=f"${self.impuesto:,.2f}")
        self.total_label.config(text=f"${self.total:,.2f}")
        
        # Habilitar/deshabilitar botón procesar
        if len(self.carrito) > 0:
            self.btn_procesar.config(state='normal')
        else:
            self.btn_procesar.config(state='disabled')
    
    def editar_cantidad(self):
        """Edita la cantidad de un producto en el carrito"""
        selected = self.carrito_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto del carrito")
            return
        
        # Obtener índice del item seleccionado
        item_index = self.carrito_tree.index(selected[0])
        item_carrito = self.carrito[item_index]
        
        # Pedir nueva cantidad
        nueva_cantidad = tk.simpledialog.askinteger(
            "Editar Cantidad",
            f"Cantidad para {item_carrito['nombre']}:\n"
            f"Stock disponible: {item_carrito['stock_disponible']}",
            initialvalue=item_carrito['cantidad'],
            minvalue=1,
            maxvalue=item_carrito['stock_disponible']
        )
        
        if nueva_cantidad:
            self.carrito[item_index]['cantidad'] = nueva_cantidad
            self.carrito[item_index]['subtotal'] = nueva_cantidad * item_carrito['precio_unitario']
            self.actualizar_carrito_display()
            self.actualizar_totales()
    
    def quitar_producto(self):
        """Quita un producto del carrito"""
        selected = self.carrito_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto del carrito")
            return
        
        item_index = self.carrito_tree.index(selected[0])
        producto_nombre = self.carrito[item_index]['nombre']
        
        if messagebox.askyesno("Confirmar", f"¿Quitar '{producto_nombre}' del carrito?"):
            del self.carrito[item_index]
            self.actualizar_carrito_display()
            self.actualizar_totales()
    
    def limpiar_carrito(self):
        """Limpia todo el carrito"""
        if len(self.carrito) == 0:
            return
        
        if messagebox.askyesno("Confirmar", "¿Limpiar todo el carrito?"):
            self.carrito.clear()
            self.actualizar_carrito_display()
            self.actualizar_totales()
    
    def seleccionar_cliente(self, event=None):
        """Selecciona un cliente de la lista"""
        selection = self.clientes_listbox.curselection()
        if not selection:
            return
        
        # Buscar cliente por el texto seleccionado
        texto_seleccionado = self.clientes_listbox.get(selection[0])
        nombre_cliente = texto_seleccionado.split(' - ')[0]
        
        # Buscar en la lista de clientes
        clientes = ClienteModel.buscar_clientes(nombre_cliente)
        for cliente in clientes:
            if cliente['nombre'] == nombre_cliente:
                self.cliente_seleccionado = cliente
                self.cliente_info_label.config(
                    text=f"Cliente: {cliente['nombre']}"
                )
                self.search_cliente_var.set("")
                self.clientes_listbox.delete(0, tk.END)
                break
    
    def nuevo_cliente(self):
        """Abre ventana para crear nuevo cliente"""
        ClienteFormView(self.frame, self.on_cliente_creado)
    
    def on_cliente_creado(self, cliente):
        """Callback cuando se crea un nuevo cliente"""
        self.cliente_seleccionado = cliente
        self.cliente_info_label.config(
            text=f"Cliente: {cliente['nombre']}"
        )
    
    def quitar_cliente(self):
        """Quita el cliente seleccionado"""
        self.cliente_seleccionado = None
        self.cliente_info_label.config(text="Cliente: Venta General")
    
    def procesar_venta(self):
        """Procesa la venta"""
        if len(self.carrito) == 0:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return
        
        # Verificar stock disponible antes de procesar
        for item in self.carrito:
            # Obtener stock actual del producto
            producto = ProductoModel.obtener_por_id(item['producto_id'])
            if not producto:
                messagebox.showerror("Error", f"No se encontró el producto {item['nombre']}")
                return
            
            if producto['stock_actual'] < item['cantidad']:
                messagebox.showerror("Error", 
                                   f"Stock insuficiente para {item['nombre']}\n"
                                   f"Disponible: {producto['stock_actual']}\n"
                                   f"Solicitado: {item['cantidad']}")
                return
        
        # Confirmar venta
        mensaje = f"¿Confirmar venta por ${self.total:,.2f}?"
        if self.cliente_seleccionado:
            mensaje += f"\nCliente: {self.cliente_seleccionado['nombre']}"
        
        if not messagebox.askyesno("Confirmar Venta", mensaje):
            return
        
        # Preparar datos de venta
        datos_venta = {
            'numero_venta': self.numero_venta,
            'cliente_id': self.cliente_seleccionado['id'] if self.cliente_seleccionado else None,
            'usuario_id': self.usuario_data['id'],
            'fecha_venta': datetime.now(),
            'subtotal': self.subtotal,
            'impuesto': self.impuesto,
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
        
        # Crear venta
        try:
            venta_id = VentaModel.crear_venta(datos_venta, detalle_items)
            
            if venta_id:
                messagebox.showinfo("Éxito", 
                                  f"Venta procesada exitosamente\n"
                                  f"Número: {self.numero_venta}\n"
                                  f"Total: ${self.total:,.2f}")
                
                # Preguntar si quiere imprimir factura
                if messagebox.askyesno("Factura", "¿Desea generar la factura?"):
                    self.generar_factura(venta_id)
                
                # Limpiar para nueva venta
                self.nueva_venta()
            else:
                messagebox.showerror("Error", "No se pudo procesar la venta")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error procesando venta: {str(e)}")
    
    def generar_factura(self, venta_id):
        """Genera la factura de la venta"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import inch
            import os
            
            # Obtener datos de la venta
            venta = VentaModel.obtener_venta_por_id(venta_id)
            if not venta:
                messagebox.showerror("Error", "No se pudo obtener los datos de la venta")
                return
            
            # Crear directorio de facturas
            facturas_dir = "facturas"
            os.makedirs(facturas_dir, exist_ok=True)
            
            # Nombre del archivo
            filename = f"{facturas_dir}/factura_{venta['numero_venta']}.pdf"
            
            # Crear PDF
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            
            # Encabezado
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "PAPELERÍA PRISMA")
            
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, "Dirección de la papelería")
            c.drawString(50, height - 85, "Teléfono: XXX-XXXX")
            
            # Información de la venta
            c.setFont("Helvetica-Bold", 12)
            c.drawString(400, height - 50, f"FACTURA")
            c.setFont("Helvetica", 10)
            c.drawString(400, height - 70, f"No: {venta['numero_venta']}")
            c.drawString(400, height - 85, f"Fecha: {venta['fecha_venta'].strftime('%d/%m/%Y %H:%M')}")
            
            # Cliente
            y = height - 120
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "CLIENTE:")
            c.setFont("Helvetica", 10)
            cliente_nombre = venta['cliente_nombre'] or "Cliente General"
            c.drawString(120, y, cliente_nombre)
            
            # Línea separadora
            y -= 30
            c.line(50, y, width - 50, y)
            
            # Encabezados de tabla
            y -= 20
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "CÓDIGO")
            c.drawString(120, y, "PRODUCTO")
            c.drawString(350, y, "CANT.")
            c.drawString(400, y, "PRECIO")
            c.drawString(480, y, "SUBTOTAL")
            
            # Línea de encabezados
            y -= 5
            c.line(50, y, width - 50, y)
            
            # Productos
            y -= 15
            c.setFont("Helvetica", 9)
            for detalle in venta['detalles']:
                c.drawString(50, y, detalle['producto_codigo'])
                c.drawString(120, y, detalle['producto_nombre'][:30])
                c.drawString(350, y, str(detalle['cantidad']))
                c.drawString(400, y, f"${detalle['precio_unitario']:,.2f}")
                c.drawString(480, y, f"${detalle['subtotal']:,.2f}")
                y -= 15
            
            # Línea de totales
            y -= 10
            c.line(350, y, width - 50, y)
            
            # Totales
            y -= 20
            c.setFont("Helvetica-Bold", 11)
            c.drawString(400, y, f"TOTAL: ${venta['total']:,.2f}")
            
            # Pie de página
            c.setFont("Helvetica", 8)
            c.drawString(50, 50, "Gracias por su compra")
            c.drawString(50, 35, f"Atendido por: {venta['usuario_nombre']}")
            
            c.save()
            
            messagebox.showinfo("Factura", f"Factura generada: {filename}")
            
            # Preguntar si quiere abrir el archivo
            if messagebox.askyesno("Abrir Factura", "¿Desea abrir la factura?"):
                os.startfile(filename)  # Windows
                
        except ImportError:
            messagebox.showerror("Error", 
                               "Para generar facturas necesita instalar reportlab:\n"
                               "pip install reportlab")
        except Exception as e:
            messagebox.showerror("Error", f"Error generando factura: {str(e)}")
    
    def nueva_venta(self):
        """Prepara una nueva venta"""
        self.carrito.clear()
        self.cliente_seleccionado = None
        self.numero_venta = VentaModel.generar_numero_venta()
        
        # Limpiar interfaz
        self.actualizar_carrito_display()
        self.actualizar_totales()
        self.cliente_info_label.config(text="Cliente: Venta General")
        self.search_producto_var.set("")
        self.search_cliente_var.set("")
        
        # Limpiar listas
        for item in self.productos_tree.get_children():
            self.productos_tree.delete(item)
        self.clientes_listbox.delete(0, tk.END)
        
        # Actualizar número de venta en título
        title_frame = self.frame.winfo_children()[0]
        numero_label = title_frame.winfo_children()[1]
        numero_label.config(text=f"Venta #: {self.numero_venta}")
    
    def cancelar_venta(self):
        """Cancela la venta actual"""
        if len(self.carrito) > 0:
            if messagebox.askyesno("Cancelar", "¿Cancelar la venta actual?"):
                self.nueva_venta()
        else:
            # Cerrar pestaña de ventas
            notebook = self.parent.master
            current_tab = None
            for i in range(notebook.index('end')):
                if notebook.tab(i, 'text') == 'Nueva Venta':
                    current_tab = i
                    break
            
            if current_tab is not None:
                notebook.forget(current_tab)

class ClienteFormView:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Nuevo Cliente")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables
        self.documento_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.telefono_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.direccion_var = tk.StringVar()
        
        self.crear_interfaz()
        self.center_window()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (300 // 2)
        self.window.geometry(f"400x300+{x}+{y}")
    
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Nuevo Cliente", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Documento
        ttk.Label(form_frame, text="Documento:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.documento_var, width=30).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Nombre
        ttk.Label(form_frame, text="* Nombre:").grid(row=row, column=0, sticky="w", pady=5)
        nombre_entry = ttk.Entry(form_frame, textvariable=self.nombre_var, width=30)
        nombre_entry.grid(row=row, column=1, sticky="w", pady=5)
        nombre_entry.focus()
        row += 1
        
        # Teléfono
        ttk.Label(form_frame, text="Teléfono:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.telefono_var, width=30).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.email_var, width=30).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Dirección
        ttk.Label(form_frame, text="Dirección:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.direccion_var, width=30).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Nota
        ttk.Label(form_frame, text="* Campo obligatorio", 
                 font=("Arial", 8)).grid(row=row, column=0, columnspan=2, pady=(20, 10))
        row += 1
        
        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Guardar", 
                  command=self.guardar).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.window.destroy).pack(side=tk.LEFT)
    
    def guardar(self):
        """Guarda el nuevo cliente"""
        nombre = self.nombre_var.get().strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        datos = {
            'documento': self.documento_var.get().strip(),
            'nombre': nombre,
            'telefono': self.telefono_var.get().strip(),
            'email': self.email_var.get().strip(),
            'direccion': self.direccion_var.get().strip()
        }
        
        try:
            cliente_id = ClienteModel.crear(datos)
            if cliente_id:
                # Obtener cliente creado
                cliente = ClienteModel.obtener_por_id(cliente_id)
                messagebox.showinfo("Éxito", "Cliente creado correctamente")
                self.callback(cliente)
                self.window.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear el cliente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")