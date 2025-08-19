# src/views/historial_compras_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.compra import CompraModel
from models.producto import ProveedorModel

class HistorialComprasView:
    def __init__(self, parent, usuario_data):
        self.parent = parent
        self.usuario_data = usuario_data
        self.frame = None
        self.compras_data = []
        
        # Variables de filtro
        self.fecha_inicio_var = tk.StringVar()
        self.fecha_fin_var = tk.StringVar()
        self.proveedor_var = tk.StringVar()
        self.estado_var = tk.StringVar()
        
        # Establecer fechas por defecto (último mes)
        hoy = date.today()
        hace_un_mes = hoy - timedelta(days=30)
        self.fecha_inicio_var.set(hace_un_mes.strftime("%Y-%m-%d"))
        self.fecha_fin_var.set(hoy.strftime("%Y-%m-%d"))
        
        self.crear_interfaz()
        self.cargar_proveedores()
        self.cargar_compras()
    
    def crear_interfaz(self):
        # Frame principal
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Historial de Compras", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Frame de filtros
        filtros_frame = ttk.LabelFrame(self.frame, text="Filtros", padding="10")
        filtros_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Primera fila de filtros
        filtros_row1 = ttk.Frame(filtros_frame)
        filtros_row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(filtros_row1, text="Desde:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        ttk.Entry(filtros_row1, textvariable=self.fecha_inicio_var, width=12).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(filtros_row1, text="Hasta:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        ttk.Entry(filtros_row1, textvariable=self.fecha_fin_var, width=12).grid(row=0, column=3, padx=(0, 20))
        
        ttk.Label(filtros_row1, text="Proveedor:").grid(row=0, column=4, sticky="w", padx=(0, 5))
        self.proveedor_combo = ttk.Combobox(filtros_row1, textvariable=self.proveedor_var, 
                                           state="readonly", width=20)
        self.proveedor_combo.grid(row=0, column=5, padx=(0, 20))
        
        # Segunda fila de filtros
        filtros_row2 = ttk.Frame(filtros_frame)
        filtros_row2.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(filtros_row2, text="Estado:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.estado_combo = ttk.Combobox(filtros_row2, textvariable=self.estado_var, 
                                        state="readonly", width=15)
        self.estado_combo['values'] = ["Todos", "Pendiente", "Recibida", "Cancelada"]
        self.estado_combo.set("Todos")
        self.estado_combo.grid(row=0, column=1, padx=(0, 20))
        
        # Botones de filtro
        ttk.Button(filtros_row2, text="Filtrar", 
                  command=self.cargar_compras).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(filtros_row2, text="Hoy", 
                  command=self.filtrar_hoy).grid(row=0, column=3, padx=(0, 5))
        ttk.Button(filtros_row2, text="Esta Semana", 
                  command=self.filtrar_semana).grid(row=0, column=4, padx=(0, 5))
        ttk.Button(filtros_row2, text="Este Mes", 
                  command=self.filtrar_mes).grid(row=0, column=5)
        
        # Frame de acciones
        acciones_frame = ttk.Frame(self.frame)
        acciones_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(acciones_frame, text="Ver Detalle", 
                  command=self.ver_detalle).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(acciones_frame, text="Recibir Compra", 
                  command=self.recibir_compra).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(acciones_frame, text="Cancelar Compra", 
                  command=self.cancelar_compra).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(acciones_frame, text="Reimprimir Orden", 
                  command=self.reimprimir_orden).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(acciones_frame, text="Actualizar", 
                  command=self.cargar_compras).pack(side=tk.LEFT)
        
        # Resumen
        self.resumen_frame = ttk.LabelFrame(self.frame, text="Resumen", padding="10")
        self.resumen_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.resumen_label = ttk.Label(self.resumen_frame, text="")
        self.resumen_label.pack()
        
        # Tabla de compras
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        self.crear_tabla(table_frame)
    
    def crear_tabla(self, parent):
        columns = ('numero', 'fecha', 'proveedor', 'usuario', 'total', 'estado')
        
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        # Configurar encabezados
        self.tree.heading('numero', text='Número')
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('proveedor', text='Proveedor')
        self.tree.heading('usuario', text='Usuario')
        self.tree.heading('total', text='Total')
        self.tree.heading('estado', text='Estado')
        
        # Configurar anchos
        self.tree.column('numero', width=150)
        self.tree.column('fecha', width=150)
        self.tree.column('proveedor', width=200)
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
    
    def cargar_proveedores(self):
        """Carga los proveedores en el combobox"""
        try:
            proveedores = ProveedorModel.obtener_todos()
            
            # Preparar datos para el combobox
            proveedores_list = ["Todos los proveedores"]
            self.proveedores_data = {}
            
            for proveedor in proveedores:
                proveedores_list.append(proveedor['nombre'])
                self.proveedores_data[proveedor['nombre']] = proveedor
            
            self.proveedor_combo['values'] = proveedores_list
            self.proveedor_var.set("Todos los proveedores")
            
        except Exception as e:
            print(f"Error cargando proveedores: {e}")
    
    def cargar_compras(self):
        """Carga las compras según los filtros"""
        try:
            fecha_inicio = self.fecha_inicio_var.get()
            fecha_fin = self.fecha_fin_var.get()
            
            # Validar fechas
            datetime.strptime(fecha_inicio, "%Y-%m-%d")
            datetime.strptime(fecha_fin, "%Y-%m-%d")
            
            # Obtener filtros
            proveedor_seleccionado = self.proveedor_var.get()
            proveedor_id = None
            if (proveedor_seleccionado and 
                proveedor_seleccionado != "Todos los proveedores" and
                proveedor_seleccionado in self.proveedores_data):
                proveedor_id = self.proveedores_data[proveedor_seleccionado]['id']
            
            estado_seleccionado = self.estado_var.get()
            estado = None
            if estado_seleccionado and estado_seleccionado != "Todos":
                estado = estado_seleccionado.lower()
            
            # Obtener compras
            self.compras_data = CompraModel.obtener_compras(fecha_inicio, fecha_fin, 
                                                           proveedor_id, estado)
            
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Llenar tabla
            total_compras = 0
            total_monto = 0
            compras_pendientes = 0
            
            for compra in self.compras_data:
                # Determinar color según estado
                tags = ()
                if compra['estado'] == 'cancelada':
                    tags = ('cancelada',)
                elif compra['estado'] == 'pendiente':
                    tags = ('pendiente',)
                elif compra['estado'] == 'recibida':
                    tags = ('recibida',)
                
                # Formatear fecha
                fecha_formatted = compra['fecha_compra'].strftime("%d/%m/%Y %H:%M")
                
                self.tree.insert('', tk.