# src/main.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import hashlib
from datetime import datetime
import sys
import os

# Agregar el directorio src al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import db

class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Papelería PRISMA - Login")
        self.window.geometry("450x350")
        self.window.resizable(False, False)
        self.setup_ui()
        self.center_window()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.window.winfo_screenheight() // 2) - (350 // 2)
        self.window.geometry(f"450x350+{x}+{y}")
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="PAPELERÍA PRISMA", 
                               font=("Arial", 20, "bold"))
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Sistema de Gestión", 
                                  font=("Arial", 12))
        subtitle_label.pack(pady=(0, 30))
        
        # Username
        ttk.Label(main_frame, text="Usuario:").pack(anchor=tk.W)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=30)
        username_entry.pack(pady=(5, 15))
        username_entry.focus()
        
        # Password
        ttk.Label(main_frame, text="Contraseña:").pack(anchor=tk.W)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, 
                                  show="*", width=30)
        password_entry.pack(pady=(5, 20))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        login_btn = ttk.Button(button_frame, text="Iniciar Sesión", 
                              command=self.login, width=15)
        login_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        exit_btn = ttk.Button(button_frame, text="Salir", 
                             command=self.window.quit, width=15)
        exit_btn.pack(side=tk.LEFT)
        
        # Bind Enter key
        self.window.bind('<Return>', lambda event: self.login())
    
    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Ingrese usuario y contraseña")
            return
        
        # Verificar credenciales
        query = "SELECT * FROM usuarios WHERE username = %s AND password = %s AND activo = TRUE"
        user = db.execute_query(query, (username, password))
        
        if user:
            self.window.destroy()
            MainApplication(user[0])
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")
            self.password_var.set("")

class MainApplication:
    def __init__(self, user_data):
        self.user_data = user_data
        self.window = tk.Tk()
        self.window.title(f"Papelería PRISMA - {user_data['nombre']}")
        self.window.geometry("1400x900")
        self.window.state('zoomed')  # Maximizar en Windows
        self.setup_ui()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        # Barra de menú
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Cerrar Sesión", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.on_closing)
        
        # Menú Inventario
        inventory_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Inventario", menu=inventory_menu)
        inventory_menu.add_command(label="Productos", command=self.show_productos)
        inventory_menu.add_command(label="Categorías", command=self.show_categorias)
        inventory_menu.add_command(label="Proveedores", command=self.show_proveedores)
        
        # Menú Ventas - ACTUALIZADO
        sales_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ventas", menu=sales_menu)
        sales_menu.add_command(label="Nueva Venta", command=self.nueva_venta)
        sales_menu.add_command(label="Historial de Ventas", command=self.show_ventas)
        sales_menu.add_separator()
        sales_menu.add_command(label="👥 Gestión de Clientes", command=self.show_clientes)
        
        # Menú Compras
        purchase_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Compras", menu=purchase_menu)
        purchase_menu.add_command(label="Nueva Compra", command=self.nueva_compra)
        purchase_menu.add_command(label="Historial de Compras", command=self.show_compras)
        
        # Menú Reportes
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reportes", menu=reports_menu)
        
        # Submenu Inventario
        inventory_reports = tk.Menu(reports_menu, tearoff=0)
        reports_menu.add_cascade(label="Inventario", menu=inventory_reports)
        inventory_reports.add_command(label="Reporte Completo", command=self.reporte_inventario_completo)
        inventory_reports.add_command(label="Stock Bajo", command=self.reporte_stock_bajo)
        inventory_reports.add_command(label="Valorización", command=self.reporte_valorizacion)
        
        # Submenu Ventas
        sales_reports = tk.Menu(reports_menu, tearoff=0)
        reports_menu.add_cascade(label="Ventas", menu=sales_reports)
        sales_reports.add_command(label="Ventas por Período", command=self.reporte_ventas_periodo)
        sales_reports.add_command(label="Productos Más Vendidos", command=self.reporte_mas_vendidos)
        sales_reports.add_command(label="Análisis de Rentabilidad", command=self.reporte_rentabilidad)
        sales_reports.add_command(label="Clientes Frecuentes", command=self.reporte_clientes_frecuentes)
        
        # Submenu Compras
        purchase_reports = tk.Menu(reports_menu, tearoff=0)
        reports_menu.add_cascade(label="Compras", menu=purchase_reports)
        purchase_reports.add_command(label="Compras por Período", command=self.reporte_compras_periodo)
        purchase_reports.add_command(label="Movimientos de Stock", command=self.reporte_movimientos)
        
        # Separador y reportes especiales
        reports_menu.add_separator()
        reports_menu.add_command(label="Dashboard Ejecutivo", command=self.dashboard_ejecutivo)
        reports_menu.add_command(label="Centro de Reportes", command=self.centro_reportes)
        
        # Menú Configuración - NUEVO
        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configuración", menu=config_menu)
        config_menu.add_command(label="👥 Usuarios", command=self.show_usuarios)
        config_menu.add_command(label="🏪 Datos de la Empresa", command=self.show_empresa)
        config_menu.add_separator()
        config_menu.add_command(label="🔧 Configuración General", command=self.show_configuracion)
        config_menu.add_command(label="💾 Respaldo de Datos", command=self.respaldo_datos)
        
        # Frame principal con notebook para pestañas
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de inicio
        self.create_dashboard()
    
    def create_dashboard(self):
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Título de bienvenida
        welcome_label = ttk.Label(dashboard_frame, 
                                 text=f"Bienvenido, {self.user_data['nombre']}", 
                                 font=("Arial", 18, "bold"))
        welcome_label.pack(pady=20)
        
        # Frame para estadísticas
        stats_frame = ttk.LabelFrame(dashboard_frame, text="Estadísticas Rápidas", padding="10")
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Obtener estadísticas
        self.update_dashboard_stats(stats_frame)
        
        # Frame para accesos rápidos
        quick_frame = ttk.LabelFrame(dashboard_frame, text="Accesos Rápidos", padding="15")
        quick_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Botones de acceso rápido
        buttons_row1 = ttk.Frame(quick_frame)
        buttons_row1.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(buttons_row1, text="🛒 Nueva Venta", command=self.nueva_venta, 
                  width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_row1, text="👥 Clientes", command=self.show_clientes, 
                  width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_row1, text="📦 Productos", command=self.show_productos, 
                  width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        buttons_row2 = ttk.Frame(quick_frame)
        buttons_row2.pack(fill=tk.X)
        
        ttk.Button(buttons_row2, text="📊 Reportes", command=self.centro_reportes, 
                  width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_row2, text="🛍️ Nueva Compra", command=self.nueva_compra, 
                  width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_row2, text="⚠️ Stock Bajo", command=self.reporte_stock_bajo, 
                  width=20).pack(side=tk.LEFT, padx=(0, 10))
    
    def update_dashboard_stats(self, parent):
        # Limpiar frame anterior
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Crear grid para estadísticas
        stats_grid = ttk.Frame(parent)
        stats_grid.pack(fill=tk.X)
        
        # Total productos
        total_productos = db.execute_query("SELECT COUNT(*) as total FROM productos WHERE activo = TRUE")
        total_productos = total_productos[0]['total'] if total_productos else 0
        
        # Total clientes
        total_clientes = db.execute_query("SELECT COUNT(*) as total FROM clientes WHERE activo = TRUE")
        total_clientes = total_clientes[0]['total'] if total_clientes else 0
        
        # Productos con stock bajo
        stock_bajo = db.execute_query("SELECT COUNT(*) as total FROM productos WHERE stock_actual <= stock_minimo AND activo = TRUE")
        stock_bajo = stock_bajo[0]['total'] if stock_bajo else 0
        
        # Ventas del día
        ventas_hoy = db.execute_query("""
            SELECT COUNT(*) as total, IFNULL(SUM(total), 0) as monto 
            FROM ventas 
            WHERE DATE(fecha_venta) = CURDATE() AND estado = 'completada'
        """)
        ventas_count = ventas_hoy[0]['total'] if ventas_hoy else 0
        ventas_monto = ventas_hoy[0]['monto'] if ventas_hoy else 0
        
        # Estadísticas en grid 2x2
        stats_data = [
            ("📦 Total Productos:", str(total_productos), 0, 0),
            ("👥 Total Clientes:", str(total_clientes), 0, 2),
            ("⚠️ Stock Bajo:", str(stock_bajo), 1, 0),
            ("💰 Ventas Hoy:", f"{ventas_count} (${ventas_monto:,.2f})", 1, 2)
        ]
        
        for label_text, value, row, col in stats_data:
            ttk.Label(stats_grid, text=label_text, font=("Arial", 11, "bold")).grid(
                row=row, column=col, sticky="w", padx=(0, 10), pady=5)
            
            value_label = ttk.Label(stats_grid, text=value, font=("Arial", 11))
            value_label.grid(row=row, column=col+1, sticky="w", padx=(0, 30), pady=5)
            
            # Colorear según el tipo
            if "Stock Bajo" in label_text and int(value.split()[0]) > 0:
                value_label.config(foreground="red")
            elif "Ventas Hoy" in label_text:
                value_label.config(foreground="green")
    
    def show_productos(self):
        # Crear nueva pestaña para productos
        from views.productos_view import ProductosView
        
        # Verificar si ya existe la pestaña
        for i in range(self.notebook.index('end')):
            if self.notebook.tab(i, 'text') == 'Productos':
                self.notebook.select(i)
                return
        
        # Crear nueva pestaña
        productos_frame = ttk.Frame(self.notebook)
        self.notebook.add(productos_frame, text='Productos')
        self.notebook.select(productos_frame)
        
        # Crear la vista de productos
        ProductosView(productos_frame)
    
    def show_categorias(self):
        messagebox.showinfo("Info", "Módulo de categorías en desarrollo")
    
    def show_proveedores(self):
        messagebox.showinfo("Info", "Módulo de proveedores en desarrollo")
    
    def nueva_venta(self):
        # Crear nueva pestaña para ventas
        from views.ventas_view import VentasView
        
        # Verificar si ya existe una pestaña de venta activa
        for i in range(self.notebook.index('end')):
            if self.notebook.tab(i, 'text') == 'Nueva Venta':
                self.notebook.select(i)
                return
        
        # Crear nueva pestaña
        ventas_frame = ttk.Frame(self.notebook)
        self.notebook.add(ventas_frame, text='Nueva Venta')
        self.notebook.select(ventas_frame)
        
        # Crear la vista de ventas
        VentasView(ventas_frame, self.user_data)
    
    def show_ventas(self):
        # Crear nueva pestaña para historial de ventas
        from views.historial_ventas_view import HistorialVentasView
        
        # Verificar si ya existe la pestaña
        for i in range(self.notebook.index('end')):
            if self.notebook.tab(i, 'text') == 'Historial Ventas':
                self.notebook.select(i)
                return
        
        # Crear nueva pestaña
        historial_frame = ttk.Frame(self.notebook)
        self.notebook.add(historial_frame, text='Historial Ventas')
        self.notebook.select(historial_frame)
        
        # Crear la vista del historial
        HistorialVentasView(historial_frame)
    
    def show_clientes(self):
        """Muestra el módulo de gestión de clientes"""
        try:
            from views.clientes_view import ClientesView
            
            # Verificar si ya existe la pestaña
            for i in range(self.notebook.index('end')):
                if self.notebook.tab(i, 'text') == 'Clientes':
                    self.notebook.select(i)
                    return
            
            # Crear nueva pestaña
            clientes_frame = ttk.Frame(self.notebook)
            self.notebook.add(clientes_frame, text='Clientes')
            self.notebook.select(clientes_frame)
            
            # Crear la vista de clientes
            ClientesView(clientes_frame)
            
        except ImportError as e:
            messagebox.showerror("Error", f"Error importando módulo de clientes: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error creando vista de clientes: {str(e)}")
    
    def nueva_compra(self):
        # Crear nueva pestaña para compras
        try:
            from views.compras_simple import ComprasView
            
            # Verificar si ya existe una pestaña de compra activa
            for i in range(self.notebook.index('end')):
                if self.notebook.tab(i, 'text') == 'Nueva Compra':
                    self.notebook.select(i)
                    return
            
            # Crear nueva pestaña
            compras_frame = ttk.Frame(self.notebook)
            self.notebook.add(compras_frame, text='Nueva Compra')
            self.notebook.select(compras_frame)
            
            # Crear la vista de compras
            ComprasView(compras_frame, self.user_data)
            
        except ImportError as e:
            messagebox.showerror("Error", f"Error importando módulo de compras: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error creando vista de compras: {str(e)}")
    
    def show_compras(self):
        # Crear nueva pestaña para historial de compras
        try:
            from views.historial_simple import HistorialComprasView
            
            # Verificar si ya existe la pestaña
            for i in range(self.notebook.index('end')):
                if self.notebook.tab(i, 'text') == 'Historial Compras':
                    self.notebook.select(i)
                    return
            
            # Crear nueva pestaña
            historial_frame = ttk.Frame(self.notebook)
            self.notebook.add(historial_frame, text='Historial Compras')
            self.notebook.select(historial_frame)
            
            # Crear la vista del historial
            HistorialComprasView(historial_frame, self.user_data)
            
        except ImportError as e:
            messagebox.showerror("Error", f"Error importando historial: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error creando historial: {str(e)}")
    
    # ===== MÉTODOS DE REPORTES =====
    
    def reporte_inventario_completo(self):
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
                messagebox.showinfo("Éxito", f"Reporte generado: {archivo}")
                os.startfile(archivo)  # Abrir archivo en Windows
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    def reporte_stock_bajo(self):
        """Genera reporte de productos con stock bajo"""
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
                messagebox.showinfo("Éxito", f"Reporte generado: {archivo}")
                os.startfile(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    def reporte_valorizacion(self):
        """Genera reporte de valorización de inventario"""
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
                messagebox.showinfo("Éxito", f"Reporte generado: {archivo}")
                os.startfile(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    def reporte_ventas_periodo(self):
        """Genera reporte de ventas por período"""
        messagebox.showinfo("Info", "Función disponible en Centro de Reportes")
        self.centro_reportes()
    
    def reporte_mas_vendidos(self):
        """Genera reporte de productos más vendidos"""
        messagebox.showinfo("Info", "Función disponible en Centro de Reportes")
        self.centro_reportes()
    
    def reporte_rentabilidad(self):
        """Genera reporte de rentabilidad"""
        messagebox.showinfo("Info", "Función disponible en Centro de Reportes")
        self.centro_reportes()
    
    def reporte_clientes_frecuentes(self):
        """Genera reporte de clientes frecuentes"""
        messagebox.showinfo("Info", "Función disponible en Centro de Reportes")
        self.centro_reportes()
    
    def reporte_compras_periodo(self):
        """Genera reporte de compras por período"""
        messagebox.showinfo("Info", "Función disponible en Centro de Reportes")
        self.centro_reportes()
    
    def reporte_movimientos(self):
        """Genera reporte de movimientos de stock"""
        messagebox.showinfo("Info", "Función disponible en Centro de Reportes")
        self.centro_reportes()
    
    def dashboard_ejecutivo(self):
        """Genera dashboard ejecutivo completo"""
        messagebox.showinfo("Info", "Función disponible en Centro de Reportes")
        self.centro_reportes()
    
    def centro_reportes(self):
        """Abre el centro de reportes"""
        try:
            from views.reportes_view import ReportesView
            
            # Verificar si ya existe la pestaña
            for i in range(self.notebook.index('end')):
                if self.notebook.tab(i, 'text') == 'Centro de Reportes':
                    self.notebook.select(i)
                    return
            
            # Crear nueva pestaña
            reportes_frame = ttk.Frame(self.notebook)
            self.notebook.add(reportes_frame, text='Centro de Reportes')
            self.notebook.select(reportes_frame)
            
            # Crear la vista de reportes
            ReportesView(reportes_frame, self.user_data)
            
        except ImportError as e:
            messagebox.showerror("Error", f"Error importando vista de reportes: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error creando vista de reportes: {str(e)}")
    
    # ===== MÉTODOS DE CONFIGURACIÓN =====
    
    def show_usuarios(self):
        """Muestra gestión de usuarios"""
        messagebox.showinfo("Info", "Módulo de usuarios en desarrollo")
    
    def show_empresa(self):
        """Muestra configuración de empresa"""
        messagebox.showinfo("Info", "Configuración de empresa en desarrollo")
    
    def show_configuracion(self):
        """Muestra configuración general"""
        messagebox.showinfo("Info", "Configuración general en desarrollo")
    
    def respaldo_datos(self):
        """Realiza respaldo de datos"""
        messagebox.showinfo("Info", "Respaldo de datos en desarrollo")
    
    def logout(self):
        self.window.destroy()
        LoginWindow().window.mainloop()
    
    def on_closing(self):
        if messagebox.askokcancel("Salir", "¿Está seguro que desea salir?"):
            self.window.quit()

def main():
    try:
        # Verificar conexión a la base de datos
        if not db.connect():
            messagebox.showerror("Error", 
                               "No se pudo conectar a la base de datos.\n"
                               "Verifique que MySQL esté ejecutándose y "
                               "las credenciales sean correctas.")
            return
        
        # Iniciar aplicación
        login_window = LoginWindow()
        login_window.window.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    main()