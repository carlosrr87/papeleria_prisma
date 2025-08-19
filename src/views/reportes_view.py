# src/views/reportes_view.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import os
import subprocess
import sys

# Agregar el directorio src al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import db

class ReportesView:
    def __init__(self, parent, user_data):
        self.parent = parent
        self.user_data = user_data
        self.reportes_generados = []
        self.setup_ui()
        self.actualizar_lista_reportes()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="🏢 CENTRO DE REPORTES", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame para contenido en dos columnas
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Columna izquierda - Generación de reportes
        left_frame = ttk.LabelFrame(content_frame, text="📊 Generar Reportes", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Columna derecha - Reportes generados
        right_frame = ttk.LabelFrame(content_frame, text="📁 Reportes Generados", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_generacion_reportes(left_frame)
        self.setup_lista_reportes(right_frame)
    
    def setup_generacion_reportes(self, parent):
        # Frame para fechas
        fecha_frame = ttk.LabelFrame(parent, text="📅 Seleccionar Período", padding="10")
        fecha_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Fechas en una fila
        fecha_row = ttk.Frame(fecha_frame)
        fecha_row.pack(fill=tk.X)
        
        # Fecha inicio
        ttk.Label(fecha_row, text="Desde:").pack(side=tk.LEFT)
        self.fecha_inicio = tk.StringVar()
        fecha_inicio_entry = ttk.Entry(fecha_row, textvariable=self.fecha_inicio, width=12)
        fecha_inicio_entry.pack(side=tk.LEFT, padx=(5, 15))
        
        # Fecha fin
        ttk.Label(fecha_row, text="Hasta:").pack(side=tk.LEFT)
        self.fecha_fin = tk.StringVar()
        fecha_fin_entry = ttk.Entry(fecha_row, textvariable=self.fecha_fin, width=12)
        fecha_fin_entry.pack(side=tk.LEFT, padx=(5, 15))
        
        # Botones de fecha rápida
        ttk.Button(fecha_row, text="Hoy", command=self.fecha_hoy, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(fecha_row, text="Semana", command=self.fecha_semana, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(fecha_row, text="Mes", command=self.fecha_mes, width=8).pack(side=tk.LEFT, padx=2)
        
        # Establecer fechas por defecto (último mes)
        self.fecha_mes()
        
        # Frame para tipos de reportes
        tipos_frame = ttk.LabelFrame(parent, text="📋 Tipos de Reportes", padding="10")
        tipos_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear notebook para categorías
        self.reportes_notebook = ttk.Notebook(tipos_frame)
        self.reportes_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestañas de categorías
        self.setup_reportes_ventas()
        self.setup_reportes_inventario()
        self.setup_reportes_compras()
        self.setup_reportes_ejecutivos()
    
    def setup_reportes_ventas(self):
        # Pestaña Ventas
        ventas_frame = ttk.Frame(self.reportes_notebook)
        self.reportes_notebook.add(ventas_frame, text="💰 Ventas")
        
        reportes_ventas = [
            ("📊 Reporte de Ventas por Período", self.generar_reporte_ventas),
            ("🏆 Productos Más Vendidos", self.generar_mas_vendidos),
            ("💹 Análisis de Rentabilidad", self.generar_rentabilidad),
            ("👥 Clientes Frecuentes", self.generar_clientes_frecuentes),
            ("📈 Ventas por Categoría", self.generar_ventas_categoria)
        ]
        
        for i, (texto, comando) in enumerate(reportes_ventas):
            btn = ttk.Button(ventas_frame, text=texto, command=comando, width=40)
            btn.pack(pady=5, padx=10, fill=tk.X)
    
    def setup_reportes_inventario(self):
        # Pestaña Inventario
        inventario_frame = ttk.Frame(self.reportes_notebook)
        self.reportes_notebook.add(inventario_frame, text="📦 Inventario")
        
        reportes_inventario = [
            ("📋 Reporte Completo de Inventario", self.generar_inventario_completo),
            ("⚠️ Productos con Stock Bajo", self.generar_stock_bajo),
            ("💎 Valorización de Inventario", self.generar_valorizacion),
            ("📊 Movimientos de Stock", self.generar_movimientos_stock),
            ("🏪 Estado por Categorías", self.generar_inventario_categorias)
        ]
        
        for i, (texto, comando) in enumerate(reportes_inventario):
            btn = ttk.Button(inventario_frame, text=texto, command=comando, width=40)
            btn.pack(pady=5, padx=10, fill=tk.X)
    
    def setup_reportes_compras(self):
        # Pestaña Compras
        compras_frame = ttk.Frame(self.reportes_notebook)
        self.reportes_notebook.add(compras_frame, text="🛒 Compras")
        
        reportes_compras = [
            ("📋 Reporte de Compras por Período", self.generar_compras_periodo),
            ("🏪 Compras por Proveedor", self.generar_compras_proveedor),
            ("📊 Análisis de Gastos", self.generar_analisis_gastos),
            ("🔄 Historial de Precios", self.generar_historial_precios)
        ]
        
        for i, (texto, comando) in enumerate(reportes_compras):
            btn = ttk.Button(compras_frame, text=texto, command=comando, width=40)
            btn.pack(pady=5, padx=10, fill=tk.X)
    
    def setup_reportes_ejecutivos(self):
        # Pestaña Ejecutivos
        ejecutivos_frame = ttk.Frame(self.reportes_notebook)
        self.reportes_notebook.add(ejecutivos_frame, text="🎯 Ejecutivos")
        
        # Descripción
        desc_label = ttk.Label(ejecutivos_frame, 
                              text="Reportes ejecutivos con análisis completo del negocio",
                              font=("Arial", 10, "italic"))
        desc_label.pack(pady=(0, 15))
        
        reportes_ejecutivos = [
            ("🏢 Dashboard Ejecutivo Completo", self.generar_dashboard_ejecutivo),
            ("📊 Resumen Gerencial", self.generar_resumen_gerencial),
            ("💼 Análisis de Desempeño", self.generar_analisis_desempeno),
            ("🎯 KPIs del Negocio", self.generar_kpis_negocio)
        ]
        
        for i, (texto, comando) in enumerate(reportes_ejecutivos):
            btn = ttk.Button(ejecutivos_frame, text=texto, command=comando, width=40)
            btn.pack(pady=8, padx=10, fill=tk.X)
    
    def setup_lista_reportes(self, parent):
        # Frame para botones de control
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="🔄 Actualizar", 
                  command=self.actualizar_lista_reportes).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="📁 Abrir Carpeta", 
                  command=self.abrir_carpeta_reportes).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(control_frame, text="🗑️ Limpiar", 
                  command=self.limpiar_reportes).pack(side=tk.RIGHT)
        
        # Lista de reportes
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.lista_reportes = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.lista_reportes.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_reportes.yview)
        
        # Bind doble click para abrir
        self.lista_reportes.bind('<Double-1>', self.abrir_reporte_seleccionado)
        
        # Menú contextual
        self.menu_contextual = tk.Menu(self.lista_reportes, tearoff=0)
        self.menu_contextual.add_command(label="Abrir", command=self.abrir_reporte_seleccionado)
        self.menu_contextual.add_command(label="Copiar ruta", command=self.copiar_ruta_reporte)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="Eliminar", command=self.eliminar_reporte_seleccionado)
        
        self.lista_reportes.bind('<Button-3>', self.mostrar_menu_contextual)
    
    # ===== MÉTODOS DE FECHAS =====
    
    def fecha_hoy(self):
        hoy = datetime.now()
        self.fecha_inicio.set(hoy.strftime("%Y-%m-%d"))
        self.fecha_fin.set(hoy.strftime("%Y-%m-%d"))
    
    def fecha_semana(self):
        hoy = datetime.now()
        inicio_semana = hoy - timedelta(days=7)
        self.fecha_inicio.set(inicio_semana.strftime("%Y-%m-%d"))
        self.fecha_fin.set(hoy.strftime("%Y-%m-%d"))
    
    def fecha_mes(self):
        hoy = datetime.now()
        inicio_mes = hoy - timedelta(days=30)
        self.fecha_inicio.set(inicio_mes.strftime("%Y-%m-%d"))
        self.fecha_fin.set(hoy.strftime("%Y-%m-%d"))
    
    def validar_fechas(self):
        """Valida que las fechas sean correctas"""
        try:
            inicio = datetime.strptime(self.fecha_inicio.get(), "%Y-%m-%d")
            fin = datetime.strptime(self.fecha_fin.get(), "%Y-%m-%d")
            
            if inicio > fin:
                messagebox.showerror("Error", "La fecha de inicio no puede ser mayor a la fecha de fin")
                return False
            
            return True
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
            return False
    
    # ===== MÉTODOS DE GENERACIÓN DE REPORTES =====
    
    def generar_reporte_ventas(self):
        """Genera reporte de ventas por período"""
        if not self.validar_fechas():
            return
        
        try:
            from views.generador_pdf import GeneradorPDF
            
            fecha_inicio = self.fecha_inicio.get()
            fecha_fin = self.fecha_fin.get()
            
            # Obtener resumen de ventas
            resumen_query = """
                SELECT 
                    COUNT(*) as total_ventas,
                    SUM(CASE WHEN estado = 'completada' THEN 1 ELSE 0 END) as ventas_completadas,
                    SUM(CASE WHEN estado = 'cancelada' THEN 1 ELSE 0 END) as ventas_canceladas,
                    SUM(total) as total_ingresos,
                    SUM(CASE WHEN estado = 'completada' THEN total ELSE 0 END) as ingresos_reales,
                    AVG(CASE WHEN estado = 'completada' THEN total ELSE NULL END) as promedio_venta
                FROM ventas 
                WHERE DATE(fecha_venta) BETWEEN %s AND %s
            """
            resumen = db.execute_query(resumen_query, (fecha_inicio, fecha_fin))
            resumen = resumen[0] if resumen else {}
            
            # Obtener detalle de ventas
            ventas_query = """
                SELECT 
                    v.numero_venta, v.fecha_venta, v.total, v.estado,
                    COALESCE(c.nombre, 'Cliente General') as cliente_nombre,
                    u.nombre as usuario_nombre,
                    COUNT(dv.id) as total_items
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                LEFT JOIN usuarios u ON v.usuario_id = u.id
                LEFT JOIN detalle_ventas dv ON v.id = dv.venta_id
                WHERE DATE(v.fecha_venta) BETWEEN %s AND %s
                GROUP BY v.id
                ORDER BY v.fecha_venta DESC
                LIMIT 100
            """
            ventas = db.execute_query(ventas_query, (fecha_inicio, fecha_fin)) or []
            
            # Generar PDF
            generador = GeneradorPDF()
            archivo = generador.generar_reporte_ventas(resumen, ventas, fecha_inicio, fecha_fin)
            
            if archivo:
                self.mostrar_exito_reporte(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte de ventas: {str(e)}")
    
    def generar_mas_vendidos(self):
        """Genera reporte de productos más vendidos"""
        if not self.validar_fechas():
            return
        
        try:
            from views.generador_pdf import GeneradorPDF
            
            fecha_inicio = self.fecha_inicio.get()
            fecha_fin = self.fecha_fin.get()
            
            # Obtener productos más vendidos
            query = """
                SELECT 
                    p.codigo, p.nombre,
                    c.nombre as categoria,
                    SUM(dv.cantidad) as total_vendido,
                    SUM(dv.cantidad * dv.precio_unitario) as total_ingresos,
                    AVG(dv.precio_unitario) as precio_promedio
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                JOIN ventas v ON dv.venta_id = v.id
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE DATE(v.fecha_venta) BETWEEN %s AND %s
                  AND v.estado = 'completada'
                GROUP BY p.id
                ORDER BY total_vendido DESC
                LIMIT 50
            """
            productos = db.execute_query(query, (fecha_inicio, fecha_fin)) or []
            
            if not productos:
                messagebox.showinfo("Info", "No hay datos de ventas en el período seleccionado")
                return
            
            # Generar PDF
            generador = GeneradorPDF()
            archivo = generador.generar_reporte_mas_vendidos(productos, fecha_inicio, fecha_fin)
            
            if archivo:
                self.mostrar_exito_reporte(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    def generar_rentabilidad(self):
        """Genera reporte de rentabilidad"""
        if not self.validar_fechas():
            return
        
        try:
            from views.generador_pdf import GeneradorPDF
            
            fecha_inicio = self.fecha_inicio.get()
            fecha_fin = self.fecha_fin.get()
            
            # Obtener datos de rentabilidad
            query = """
                SELECT 
                    p.nombre,
                    SUM(dv.cantidad) as total_vendido,
                    SUM(dv.cantidad * dv.precio_unitario) as ingresos_totales,
                    SUM(dv.cantidad * p.precio_compra) as costo_total,
                    (SUM(dv.cantidad * dv.precio_unitario) - SUM(dv.cantidad * p.precio_compra)) as ganancia_bruta,
                    CASE 
                        WHEN SUM(dv.cantidad * dv.precio_unitario) > 0 THEN
                            ((SUM(dv.cantidad * dv.precio_unitario) - SUM(dv.cantidad * p.precio_compra)) / 
                             SUM(dv.cantidad * dv.precio_unitario)) * 100
                        ELSE 0
                    END as margen_porcentaje
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                JOIN ventas v ON dv.venta_id = v.id
                WHERE DATE(v.fecha_venta) BETWEEN %s AND %s
                  AND v.estado = 'completada'
                  AND p.precio_compra > 0
                GROUP BY p.id
                HAVING total_vendido > 0
                ORDER BY ganancia_bruta DESC
                LIMIT 50
            """
            productos = db.execute_query(query, (fecha_inicio, fecha_fin)) or []
            
            if not productos:
                messagebox.showinfo("Info", "No hay datos suficientes para el análisis de rentabilidad")
                return
            
            # Generar PDF
            generador = GeneradorPDF()
            archivo = generador.generar_reporte_rentabilidad(productos, fecha_inicio, fecha_fin)
            
            if archivo:
                self.mostrar_exito_reporte(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    def generar_clientes_frecuentes(self):
        """Genera reporte de clientes frecuentes"""
        if not self.validar_fechas():
            return
        
        try:
            from views.generador_pdf import GeneradorPDF
            
            fecha_inicio = self.fecha_inicio.get()
            fecha_fin = self.fecha_fin.get()
            
            # Obtener clientes frecuentes
            query = """
                SELECT 
                    COALESCE(c.nombre, 'Cliente General') as nombre,
                    COUNT(v.id) as total_compras,
                    SUM(v.total) as total_gastado,
                    AVG(v.total) as promedio_compra,
                    MAX(v.fecha_venta) as ultima_compra
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                WHERE DATE(v.fecha_venta) BETWEEN %s AND %s
                  AND v.estado = 'completada'
                GROUP BY COALESCE(v.cliente_id, 0)
                HAVING total_compras > 0
                ORDER BY total_gastado DESC
                LIMIT 50
            """
            clientes = db.execute_query(query, (fecha_inicio, fecha_fin)) or []
            
            if not clientes:
                messagebox.showinfo("Info", "No hay datos de clientes en el período seleccionado")
                return
            
            # Generar PDF
            generador = GeneradorPDF()
            archivo = generador.generar_reporte_clientes(clientes, fecha_inicio, fecha_fin)
            
            if archivo:
                self.mostrar_exito_reporte(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    def generar_ventas_categoria(self):
        """Genera reporte de ventas por categoría"""
        if not self.validar_fechas():
            return
        
        try:
            from views.generador_pdf import GeneradorPDF
            
            fecha_inicio = self.fecha_inicio.get()
            fecha_fin = self.fecha_fin.get()
            
            # Obtener ventas por categoría
            query = """
                SELECT 
                    COALESCE(c.nombre, 'Sin Categoría') as nombre,
                    COUNT(DISTINCT p.id) as productos_vendidos,
                    SUM(dv.cantidad) as unidades_vendidas,
                    SUM(dv.cantidad * dv.precio_unitario) as ingresos,
                    (SUM(dv.cantidad * dv.precio_unitario) / 
                     (SELECT SUM(dv2.cantidad * dv2.precio_unitario) 
                      FROM detalle_ventas dv2 
                      JOIN ventas v2 ON dv2.venta_id = v2.id 
                      WHERE DATE(v2.fecha_venta) BETWEEN %s AND %s 
                        AND v2.estado = 'completada') * 100) as porcentaje
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                JOIN ventas v ON dv.venta_id = v.id
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE DATE(v.fecha_venta) BETWEEN %s AND %s
                  AND v.estado = 'completada'
                GROUP BY COALESCE(p.categoria_id, 0)
                ORDER BY ingresos DESC
            """
            categorias = db.execute_query(query, (fecha_inicio, fecha_fin, fecha_inicio, fecha_fin)) or []
            
            if not categorias:
                messagebox.showinfo("Info", "No hay datos de ventas por categoría en el período seleccionado")
                return
            
            # Generar PDF
            generador = GeneradorPDF()
            archivo = generador.generar_reporte_categorias(categorias, fecha_inicio, fecha_fin)
            
            if archivo:
                self.mostrar_exito_reporte(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    # ===== REPORTES DE INVENTARIO =====
    
    def generar_inventario_completo(self):
        """Genera reporte completo de inventario"""
        try:
            from views.generador_pdf import GeneradorPDF
            
            # Obtener resumen
            resumen_query = """
                SELECT 
                    COUNT(*) as total_productos,
                    SUM(stock_actual) as total_stock,
                    SUM(stock_actual * precio_venta) as valor_total_inventario,
                    SUM(CASE WHEN stock_actual <= stock_minimo THEN 1 ELSE 0 END) as productos_stock_bajo,
                    SUM(CASE WHEN stock_actual = 0 THEN 1 ELSE 0 END) as productos_sin_stock,
                    AVG(precio_venta) as precio_promedio
                FROM productos 
                WHERE activo = TRUE
            """
            resumen = db.execute_query(resumen_query)
            resumen = resumen[0] if resumen else {}
            
            # Obtener productos
            productos_query = """
                SELECT 
                    codigo, nombre, precio_venta, stock_actual,
                    (stock_actual * precio_venta) as valor_stock,
                    CASE 
                        WHEN stock_actual = 0 THEN 'Sin Stock'
                        WHEN stock_actual <= stock_minimo THEN 'Stock Bajo'
                        ELSE 'Normal'
                    END as estado_stock,
                    c.nombre as categoria
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE p.activo = TRUE
                ORDER BY valor_stock DESC
            """
            productos = db.execute_query(productos_query) or []
            
            # Generar PDF
            generador = GeneradorPDF()
            archivo = generador.generar_reporte_inventario(resumen, productos)
            
            if archivo:
                self.mostrar_exito_reporte(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    def generar_stock_bajo(self):
        """Genera reporte de stock bajo"""
        try:
            from views.generador_pdf import GeneradorPDF
            
            # Obtener productos con stock bajo
            query = """
                SELECT 
                    p.codigo, p.nombre, p.stock_actual, p.stock_minimo,
                    c.nombre as categoria_nombre,
                    pr.nombre as proveedor_nombre
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
                WHERE p.stock_actual <= p.stock_minimo AND p.activo = TRUE
                ORDER BY (p.stock_actual - p.stock_minimo) ASC
            """
            productos = db.execute_query(query) or []
            
            if not productos:
                messagebox.showinfo("Info", "¡Excelente! No hay productos con stock bajo")
                return
            
            # Generar PDF
            generador = GeneradorPDF()
            archivo = generador.generar_reporte_stock_bajo(productos)
            
            if archivo:
                self.mostrar_exito_reporte(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    def generar_valorizacion(self):
        """Genera reporte de valorización"""
        try:
            from views.generador_pdf import GeneradorPDF
            
            # Obtener resumen de valorización
            resumen_query = """
                SELECT 
                    COUNT(*) as total_productos,
                    SUM(stock_actual) as total_stock,
                    SUM(stock_actual * precio_venta) as valor_total_inventario,
                    AVG(precio_venta) as precio_promedio
                FROM productos 
                WHERE activo = TRUE
            """
            resumen = db.execute_query(resumen_query)
            resumen = resumen[0] if resumen else {}
            
            # Obtener productos para detalle
            productos_query = """
                SELECT codigo, nombre, stock_actual, precio_venta,
                       (stock_actual * precio_venta) as valor_stock
                FROM productos 
                WHERE activo = TRUE AND stock_actual > 0
                ORDER BY valor_stock DESC
                LIMIT 100
            """
            productos = db.execute_query(productos_query) or []
            
            # Generar PDF
            generador = GeneradorPDF()
            archivo = generador.generar_reporte_valorizacion(resumen, productos)
            
            if archivo:
                self.mostrar_exito_reporte(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    # ===== MÉTODOS PLACEHOLDER PARA OTROS REPORTES =====
    
    def generar_movimientos_stock(self):
        messagebox.showinfo("Info", "Reporte de movimientos en desarrollo")
    
    def generar_inventario_categorias(self):
        messagebox.showinfo("Info", "Reporte de inventario por categorías en desarrollo")
    
    def generar_compras_periodo(self):
        messagebox.showinfo("Info", "Reporte de compras en desarrollo")
    
    def generar_compras_proveedor(self):
        messagebox.showinfo("Info", "Reporte de compras por proveedor en desarrollo")
    
    def generar_analisis_gastos(self):
        messagebox.showinfo("Info", "Análisis de gastos en desarrollo")
    
    def generar_historial_precios(self):
        messagebox.showinfo("Info", "Historial de precios en desarrollo")
    
    def generar_dashboard_ejecutivo(self):
        messagebox.showinfo("Info", "Dashboard ejecutivo en desarrollo")
    
    def generar_resumen_gerencial(self):
        messagebox.showinfo("Info", "Resumen gerencial en desarrollo")
    
    def generar_analisis_desempeno(self):
        messagebox.showinfo("Info", "Análisis de desempeño en desarrollo")