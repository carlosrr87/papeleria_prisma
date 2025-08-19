# src/views/historial_ventas_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.venta import VentaModel

class HistorialVentasView:
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.ventas_data = []
        
        # Variables de filtro
        self.fecha_inicio_var = tk.StringVar()
        self.fecha_fin_var = tk.StringVar()
        
        # Establecer fechas por defecto (último mes)
        hoy = date.today()
        hace_un_mes = hoy - timedelta(days=30)
        self.fecha_inicio_var.set(hace_un_mes.strftime("%Y-%m-%d"))
        self.fecha_fin_var.set(hoy.strftime("%Y-%m-%d"))
        
        self.crear_interfaz()
        self.cargar_ventas()
    
    def crear_interfaz(self):
        # Frame principal
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Historial de Ventas", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Frame de filtros
        filtros_frame = ttk.LabelFrame(self.frame, text="Filtros", padding="10")
        filtros_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Filtros de fecha
        fecha_frame = ttk.Frame(filtros_frame)
        fecha_frame.pack(fill=tk.X)
        
        ttk.Label(fecha_frame, text="Desde:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        fecha_inicio_entry = ttk.Entry(fecha_frame, textvariable=self.fecha_inicio_var, width=12)
        fecha_inicio_entry.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(fecha_frame, text="Hasta:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        fecha_fin_entry = ttk.Entry(fecha_frame, textvariable=self.fecha_fin_var, width=12)
        fecha_fin_entry.grid(row=0, column=3, padx=(0, 20))
        
        # Botones de filtro
        ttk.Button(fecha_frame, text="Filtrar", 
                  command=self.cargar_ventas).grid(row=0, column=4, padx=(0, 10))
        ttk.Button(fecha_frame, text="Hoy", 
                  command=self.filtrar_hoy).grid(row=0, column=5, padx=(0, 5))
        ttk.Button(fecha_frame, text="Esta Semana", 
                  command=self.filtrar_semana).grid(row=0, column=6, padx=(0, 5))
        ttk.Button(fecha_frame, text="Este Mes", 
                  command=self.filtrar_mes).grid(row=0, column=7)
        
        # Frame de acciones
        acciones_frame = ttk.Frame(self.frame)
        acciones_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(acciones_frame, text="Ver Detalle", 
                  command=self.ver_detalle).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(acciones_frame, text="Reimprimir Factura", 
                  command=self.reimprimir_factura).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(acciones_frame, text="Cancelar Venta", 
                  command=self.cancelar_venta).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(acciones_frame, text="Actualizar", 
                  command=self.cargar_ventas).pack(side=tk.LEFT)
        
        # Resumen
        self.resumen_frame = ttk.LabelFrame(self.frame, text="Resumen", padding="10")
        self.resumen_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.resumen_label = ttk.Label(self.resumen_frame, text="")
        self.resumen_label.pack()
        
        # Tabla de ventas
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        self.crear_tabla(table_frame)
    
    def crear_tabla(self, parent):
        columns = ('numero', 'fecha', 'cliente', 'usuario', 'total', 'estado')
        
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        # Configurar encabezados
        self.tree.heading('numero', text='Número')
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('cliente', text='Cliente')
        self.tree.heading('usuario', text='Usuario')
        self.tree.heading('total', text='Total')
        self.tree.heading('estado', text='Estado')
        
        # Configurar anchos
        self.tree.column('numero', width=120)
        self.tree.column('fecha', width=150)
        self.tree.column('cliente', width=200)
        self.tree.column('usuario', width=150)
        self.tree.column('total', width=100)
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
        self.tree.bind('<Double-1>', lambda e: self.ver_detalle())
    
    def cargar_ventas(self):
        """Carga las ventas según los filtros"""
        try:
            fecha_inicio = self.fecha_inicio_var.get()
            fecha_fin = self.fecha_fin_var.get()
            
            # Validar fechas
            datetime.strptime(fecha_inicio, "%Y-%m-%d")
            datetime.strptime(fecha_fin, "%Y-%m-%d")
            
            # Obtener ventas
            self.ventas_data = VentaModel.obtener_ventas(fecha_inicio, fecha_fin)
            
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Llenar tabla
            total_ventas = 0
            total_ingresos = 0
            
            for venta in self.ventas_data:
                # Determinar color según estado
                tags = ()
                if venta['estado'] == 'cancelada':
                    tags = ('cancelada',)
                
                # Formatear fecha
                fecha_formatted = venta['fecha_venta'].strftime("%d/%m/%Y %H:%M")
                
                self.tree.insert('', tk.END, values=(
                    venta['numero_venta'],
                    fecha_formatted,
                    venta['cliente_nombre'] or 'Cliente General',
                    venta['usuario_nombre'],
                    f"${venta['total']:,.2f}",
                    venta['estado'].title()
                ), tags=tags)
                
                if venta['estado'] == 'completada':
                    total_ventas += 1
                    total_ingresos += venta['total']
            
            # Configurar colores
            self.tree.tag_configure('cancelada', background='#ffcccc')
            
            # Actualizar resumen
            promedio = total_ingresos / total_ventas if total_ventas > 0 else 0
            self.resumen_label.config(
                text=f"Ventas completadas: {total_ventas} | "
                     f"Total ingresos: ${total_ingresos:,.2f} | "
                     f"Promedio por venta: ${promedio:,.2f}"
            )
            
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando ventas: {str(e)}")
    
    def filtrar_hoy(self):
        """Filtrar ventas de hoy"""
        hoy = date.today().strftime("%Y-%m-%d")
        self.fecha_inicio_var.set(hoy)
        self.fecha_fin_var.set(hoy)
        self.cargar_ventas()
    
    def filtrar_semana(self):
        """Filtrar ventas de esta semana"""
        hoy = date.today()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        self.fecha_inicio_var.set(inicio_semana.strftime("%Y-%m-%d"))
        self.fecha_fin_var.set(hoy.strftime("%Y-%m-%d"))
        self.cargar_ventas()
    
    def filtrar_mes(self):
        """Filtrar ventas de este mes"""
        hoy = date.today()
        inicio_mes = hoy.replace(day=1)
        self.fecha_inicio_var.set(inicio_mes.strftime("%Y-%m-%d"))
        self.fecha_fin_var.set(hoy.strftime("%Y-%m-%d"))
        self.cargar_ventas()
    
    def ver_detalle(self):
        """Ver detalle de la venta seleccionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una venta")
            return
        
        # Obtener venta seleccionada
        item = self.tree.item(selected[0])
        numero_venta = item['values'][0]
        
        # Buscar venta en los datos
        venta_seleccionada = None
        for venta in self.ventas_data:
            if venta['numero_venta'] == numero_venta:
                venta_seleccionada = venta
                break
        
        if venta_seleccionada:
            DetalleVentaView(self.frame, venta_seleccionada['id'])
    
    def reimprimir_factura(self):
        """Reimprimir factura de la venta seleccionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una venta")
            return
        
        item = self.tree.item(selected[0])
        numero_venta = item['values'][0]
        estado = item['values'][5].lower()
        
        if estado == 'cancelada':
            messagebox.showerror("Error", "No se puede reimprimir una venta cancelada")
            return
        
        # Buscar venta en los datos
        venta_seleccionada = None
        for venta in self.ventas_data:
            if venta['numero_venta'] == numero_venta:
                venta_seleccionada = venta
                break
        
        if venta_seleccionada:
            # Usar el mismo método de generar factura del módulo de ventas
            try:
                from views.ventas_view import VentasView
                # Crear instancia temporal solo para usar el método de factura
                temp_ventas = VentasView(self.frame, {'id': 1})  # Usuario temporal
                temp_ventas.generar_factura(venta_seleccionada['id'])
            except Exception as e:
                messagebox.showerror("Error", f"Error generando factura: {str(e)}")
    
    def cancelar_venta(self):
        """Cancelar la venta seleccionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una venta")
            return
        
        item = self.tree.item(selected[0])
        numero_venta = item['values'][0]
        estado = item['values'][5].lower()
        
        if estado == 'cancelada':
            messagebox.showerror("Error", "La venta ya está cancelada")
            return
        
        # Confirmar cancelación
        if not messagebox.askyesno("Confirmar", 
                                  f"¿Está seguro de cancelar la venta {numero_venta}?\n"
                                  "Esta acción restaurará el stock de los productos."):
            return
        
        # Buscar venta en los datos
        venta_seleccionada = None
        for venta in self.ventas_data:
            if venta['numero_venta'] == numero_venta:
                venta_seleccionada = venta
                break
        
        if venta_seleccionada:
            if VentaModel.cancelar_venta(venta_seleccionada['id'], 1):  # Usuario ID temporal
                messagebox.showinfo("Éxito", "Venta cancelada correctamente")
                self.cargar_ventas()  # Recargar lista
            else:
                messagebox.showerror("Error", "No se pudo cancelar la venta")

class DetalleVentaView:
    def __init__(self, parent, venta_id):
        self.parent = parent
        self.venta_id = venta_id
        
        self.window = tk.Toplevel(parent)
        self.window.title("Detalle de Venta")
        self.window.geometry("700x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.crear_interfaz()
        self.cargar_datos()
        self.center_window()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"700x600+{x}+{y}")
    
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        self.titulo_label = ttk.Label(main_frame, text="Detalle de Venta", 
                                     font=("Arial", 16, "bold"))
        self.titulo_label.pack(pady=(0, 20))
        
        # Información de la venta
        info_frame = ttk.LabelFrame(main_frame, text="Información General", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.info_text = tk.Text(info_frame, height=6, width=80, wrap=tk.WORD)
        self.info_text.pack(fill=tk.X)
        self.info_text.config(state=tk.DISABLED)
        
        # Productos
        productos_frame = ttk.LabelFrame(main_frame, text="Productos", padding="10")
        productos_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Crear tabla de productos
        columns = ('codigo', 'nombre', 'cantidad', 'precio', 'subtotal')
        self.productos_tree = ttk.Treeview(productos_frame, columns=columns, 
                                          show='headings', height=12)
        
        # Configurar encabezados
        self.productos_tree.heading('codigo', text='Código')
        self.productos_tree.heading('nombre', text='Producto')
        self.productos_tree.heading('cantidad', text='Cantidad')
        self.productos_tree.heading('precio', text='Precio Unit.')
        self.productos_tree.heading('subtotal', text='Subtotal')
        
        # Configurar anchos
        self.productos_tree.column('codigo', width=100)
        self.productos_tree.column('nombre', width=250)
        self.productos_tree.column('cantidad', width=80)
        self.productos_tree.column('precio', width=100)
        self.productos_tree.column('subtotal', width=100)
        
        # Scrollbar
        productos_scroll = ttk.Scrollbar(productos_frame, orient=tk.VERTICAL, 
                                        command=self.productos_tree.yview)
        self.productos_tree.configure(yscrollcommand=productos_scroll.set)
        
        self.productos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        productos_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Totales
        totales_frame = ttk.Frame(main_frame)
        totales_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.totales_label = ttk.Label(totales_frame, text="", 
                                      font=("Arial", 12, "bold"))
        self.totales_label.pack(side=tk.RIGHT)
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Imprimir Factura", 
                  command=self.imprimir_factura).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cerrar", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
    
    def cargar_datos(self):
        """Carga los datos de la venta"""
        try:
            venta = VentaModel.obtener_venta_por_id(self.venta_id)
            if not venta:
                messagebox.showerror("Error", "No se pudo obtener la información de la venta")
                self.window.destroy()
                return
            
            # Actualizar título
            self.titulo_label.config(text=f"Detalle de Venta - {venta['numero_venta']}")
            
            # Información general
            info_text = f"""Número de Venta: {venta['numero_venta']}
Fecha: {venta['fecha_venta'].strftime('%d/%m/%Y %H:%M:%S')}
Cliente: {venta['cliente_nombre'] or 'Cliente General'}
Documento Cliente: {venta['cliente_documento'] or 'N/A'}
Usuario: {venta['usuario_nombre']}
Estado: {venta['estado'].title()}"""
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
            self.info_text.config(state=tk.DISABLED)
            
            # Productos
            for item in self.productos_tree.get_children():
                self.productos_tree.delete(item)
            
            for detalle in venta['detalles']:
                self.productos_tree.insert('', tk.END, values=(
                    detalle['producto_codigo'],
                    detalle['producto_nombre'],
                    detalle['cantidad'],
                    f"${detalle['precio_unitario']:,.2f}",
                    f"${detalle['subtotal']:,.2f}"
                ))
            
            # Totales
            self.totales_label.config(
                text=f"Subtotal: ${venta['subtotal']:,.2f} | "
                     f"Impuesto: ${venta['impuesto']:,.2f} | "
                     f"TOTAL: ${venta['total']:,.2f}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando datos: {str(e)}")
    
    def imprimir_factura(self):
        """Imprimir factura de la venta"""
        try:
            from views.ventas_view import VentasView
            # Crear instancia temporal solo para usar el método de factura
            temp_ventas = VentasView(self.window, {'id': 1})  # Usuario temporal
            temp_ventas.generar_factura(self.venta_id)
        except Exception as e:
            messagebox.showerror("Error", f"Error generando factura: {str(e)}")