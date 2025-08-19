# src/views/clientes_view.py - Versión final corregida
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os

# Agregar el directorio src al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import db

class ClientesView:
    def __init__(self, parent):
        self.parent = parent
        self.clientes_data = []
        self.cliente_seleccionado = None
        self.setup_ui()
        self.cargar_clientes()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="👥 GESTIÓN DE CLIENTES", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame superior - Búsqueda y botones
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(top_frame, text="🔍 Búsqueda", padding="5")
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Campo de búsqueda
        search_row = ttk.Frame(search_frame)
        search_row.pack(fill=tk.X)
        
        ttk.Label(search_row, text="Buscar:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_row, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(search_row, text="🔍", command=self.buscar_clientes, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_row, text="🔄", command=self.limpiar_busqueda, width=3).pack(side=tk.LEFT, padx=2)
        
        # Bind Enter para búsqueda
        self.search_entry.bind('<Return>', lambda e: self.buscar_clientes())
        self.search_var.trace('w', self.buscar_en_tiempo_real)
        
        # Frame de botones
        buttons_frame = ttk.LabelFrame(top_frame, text="⚡ Acciones", padding="5")
        buttons_frame.pack(side=tk.RIGHT)
        
        # Botones principales
        ttk.Button(buttons_frame, text="➕ Nuevo Cliente", 
                  command=self.nuevo_cliente, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="✏️ Editar", 
                  command=self.editar_cliente, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="🔄 Actualizar", 
                  command=self.actualizar_lista, width=12).pack(side=tk.LEFT, padx=2)
        
        # Frame central - Lista de clientes y detalles
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame izquierdo - Lista de clientes
        left_frame = ttk.LabelFrame(center_frame, text="📋 Lista de Clientes", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Treeview para clientes
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        columns = ("ID", "Documento", "Nombre", "Teléfono", "Email", "Ciudad", "Estado")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings",
                                yscrollcommand=v_scrollbar.set,
                                xscrollcommand=h_scrollbar.set)
        
        # Configurar scrollbars
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configurar columnas
        self.tree.heading("#0", text="", anchor="w")
        self.tree.column("#0", width=0, stretch=False)
        
        column_configs = {
            "ID": (50, False),
            "Documento": (100, True),
            "Nombre": (200, True),
            "Teléfono": (120, True),
            "Email": (180, True),
            "Ciudad": (120, True),
            "Estado": (80, True)
        }
        
        for col, (width, stretch) in column_configs.items():
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=width, stretch=stretch)
        
        # Bind eventos
        self.tree.bind("<<TreeviewSelect>>", self.on_cliente_select)
        self.tree.bind("<Double-1>", lambda e: self.editar_cliente())
        
        # Frame derecho - Detalles del cliente
        right_frame = ttk.LabelFrame(center_frame, text="👤 Detalles del Cliente", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 0))
        
        self.setup_cliente_details(right_frame)
        
        # Frame inferior - Estadísticas
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Estadísticas", padding="10")
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.setup_estadisticas(stats_frame)
    
    def setup_cliente_details(self, parent):
        """Configura el panel de detalles del cliente"""
        # Frame para información básica
        info_frame = ttk.LabelFrame(parent, text="📝 Información Personal", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Labels para mostrar información
        self.detail_labels = {}
        
        details = [
            ("ID:", "id"),
            ("Documento:", "documento"),
            ("Nombre:", "nombre"),
            ("Teléfono:", "telefono"),
            ("Email:", "email"),
            ("Dirección:", "direccion"),
            ("Ciudad:", "ciudad"),
            ("Estado:", "estado"),
            ("Fecha Registro:", "fecha_creacion")
        ]
        
        for i, (label_text, key) in enumerate(details):
            ttk.Label(info_frame, text=label_text, font=("Arial", 9, "bold")).grid(
                row=i, column=0, sticky="w", pady=2)
            
            value_label = ttk.Label(info_frame, text="-", font=("Arial", 9))
            value_label.grid(row=i, column=1, sticky="w", padx=(10, 0), pady=2)
            self.detail_labels[key] = value_label
        
        # Frame para estadísticas del cliente
        client_stats_frame = ttk.LabelFrame(parent, text="📈 Estadísticas de Compras", padding="10")
        client_stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_labels = {}
        stats = [
            ("Total Compras:", "total_compras"),
            ("Total Gastado:", "total_gastado"),
            ("Promedio por Compra:", "promedio_compra")
        ]
        
        for i, (label_text, key) in enumerate(stats):
            ttk.Label(client_stats_frame, text=label_text, font=("Arial", 9, "bold")).grid(
                row=i, column=0, sticky="w", pady=2)
            
            value_label = ttk.Label(client_stats_frame, text="-", font=("Arial", 9))
            value_label.grid(row=i, column=1, sticky="w", padx=(10, 0), pady=2)
            self.stats_labels[key] = value_label
        
        # Botones de acciones específicas
        actions_frame = ttk.LabelFrame(parent, text="⚡ Acciones Rápidas", padding="10")
        actions_frame.pack(fill=tk.X)
        
        ttk.Button(actions_frame, text="📊 Ver Historial", 
                  command=self.ver_historial_cliente, width=20).pack(pady=2, fill=tk.X)
        ttk.Button(actions_frame, text="🛒 Nueva Venta", 
                  command=self.nueva_venta_cliente, width=20).pack(pady=2, fill=tk.X)
    
    def setup_estadisticas(self, parent):
        """Configura el panel de estadísticas generales"""
        stats_row = ttk.Frame(parent)
        stats_row.pack(fill=tk.X)
        
        # Variables para estadísticas
        self.total_clientes_var = tk.StringVar(value="0")
        self.clientes_activos_var = tk.StringVar(value="0")
        self.nuevos_mes_var = tk.StringVar(value="0")
        self.sin_compras_var = tk.StringVar(value="0")
        
        # Estadísticas en columnas
        stats_data = [
            ("👥 Total Clientes:", self.total_clientes_var),
            ("✅ Activos:", self.clientes_activos_var),
            ("🆕 Nuevos (Mes):", self.nuevos_mes_var),
            ("😴 Sin Compras:", self.sin_compras_var)
        ]
        
        for i, (label_text, var) in enumerate(stats_data):
            frame = ttk.Frame(stats_row)
            frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
            
            ttk.Label(frame, text=label_text, font=("Arial", 10, "bold")).pack()
            ttk.Label(frame, textvariable=var, font=("Arial", 14, "bold"), 
                     foreground="blue").pack()
    
    def cargar_clientes(self):
        """Carga la lista de clientes desde la base de datos - CORREGIDO para tu estructura"""
        try:
            # Query corregida para tu estructura de tabla
            query = """
                SELECT 
                    c.id,
                    c.documento,
                    c.nombre,
                    c.telefono,
                    c.email,
                    c.direccion,
                    c.ciudad,
                    CASE WHEN c.activo = 1 THEN 'Activo' ELSE 'Inactivo' END as estado,
                    c.fecha_creacion,
                    COUNT(v.id) as total_compras,
                    COALESCE(SUM(v.total), 0) as total_gastado
                FROM clientes c
                LEFT JOIN ventas v ON c.id = v.cliente_id AND v.estado = 'completada'
                GROUP BY c.id
                ORDER BY c.nombre
            """
            
            print("🔍 Ejecutando consulta de clientes...")  # Debug
            self.clientes_data = db.execute_query(query) or []
            print(f"📊 Clientes cargados: {len(self.clientes_data)}")  # Debug
            
            # Mostrar algunos datos para debug
            if self.clientes_data:
                print(f"✅ Primer cliente: {self.clientes_data[0]['nombre']}")
            else:
                print("⚠️ No se encontraron clientes")
            
            self.mostrar_clientes(self.clientes_data)
            self.actualizar_estadisticas()
            
        except Exception as e:
            print(f"❌ Error cargando clientes: {str(e)}")
            messagebox.showerror("Error", f"Error cargando clientes: {str(e)}")
    
    def mostrar_clientes(self, clientes):
        """Muestra los clientes en el TreeView"""
        # Limpiar TreeView
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        print(f"🔍 Mostrando {len(clientes)} clientes")  # Debug
        
        if not clientes:
            print("⚠️ No hay clientes para mostrar")
            return
        
        # Agregar clientes
        for cliente in clientes:
            # Formatear datos
            documento = cliente.get('documento', '') or '-'
            telefono = cliente.get('telefono', '') or '-'
            email = cliente.get('email', '') or '-'
            ciudad = cliente.get('ciudad', '') or '-'
            
            values = (
                cliente['id'],
                documento,
                cliente['nombre'],
                telefono,
                email,
                ciudad,
                cliente['estado']
            )
            
            # Insertar en TreeView
            item = self.tree.insert("", "end", values=values)
            
            # Colorear según estado
            if cliente['estado'] == 'Inactivo':
                self.tree.set(item, 'Estado', '🔴 Inactivo')
            else:
                self.tree.set(item, 'Estado', '🟢 Activo')
        
        print(f"✅ TreeView actualizado con {len(clientes)} clientes")  # Debug
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas generales"""
        try:
            # Total clientes
            total_query = "SELECT COUNT(*) as total FROM clientes"
            total_result = db.execute_query(total_query)
            total_clientes = total_result[0]['total'] if total_result else 0
            
            # Clientes activos
            activos_query = "SELECT COUNT(*) as total FROM clientes WHERE activo = TRUE"
            activos_result = db.execute_query(activos_query)
            clientes_activos = activos_result[0]['total'] if activos_result else 0
            
            # Nuevos del mes - CORREGIDO para fecha_creacion
            nuevos_query = """
                SELECT COUNT(*) as total FROM clientes 
                WHERE MONTH(fecha_creacion) = MONTH(CURDATE()) 
                  AND YEAR(fecha_creacion) = YEAR(CURDATE())
            """
            nuevos_result = db.execute_query(nuevos_query)
            nuevos_mes = nuevos_result[0]['total'] if nuevos_result else 0
            
            # Sin compras
            sin_compras_query = """
                SELECT COUNT(*) as total FROM clientes c
                LEFT JOIN ventas v ON c.id = v.cliente_id
                WHERE v.id IS NULL AND c.activo = TRUE
            """
            sin_compras_result = db.execute_query(sin_compras_query)
            sin_compras = sin_compras_result[0]['total'] if sin_compras_result else 0
            
            # Actualizar variables
            self.total_clientes_var.set(f"{total_clientes:,}")
            self.clientes_activos_var.set(f"{clientes_activos:,}")
            self.nuevos_mes_var.set(f"{nuevos_mes:,}")
            self.sin_compras_var.set(f"{sin_compras:,}")
            
            print(f"📊 Estadísticas: Total={total_clientes}, Activos={clientes_activos}")  # Debug
            
        except Exception as e:
            print(f"❌ Error actualizando estadísticas: {str(e)}")
    
    def actualizar_lista(self):
        """Método público para actualizar la lista"""
        print("🔄 Actualizando lista de clientes...")
        self.cargar_clientes()
        self.cliente_seleccionado = None
        
        # Limpiar detalles
        for label in self.detail_labels.values():
            label.config(text="-")
        for label in self.stats_labels.values():
            label.config(text="-")
        
        print("✅ Lista actualizada")
    
    def on_cliente_select(self, event):
        """Maneja la selección de un cliente"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            
            if values:
                cliente_id = values[0]
                self.cliente_seleccionado = cliente_id
                self.mostrar_detalles_cliente(cliente_id)
    
    def mostrar_detalles_cliente(self, cliente_id):
        """Muestra los detalles del cliente seleccionado"""
        try:
            # Obtener datos del cliente - CORREGIDO para tu estructura
            cliente_query = """
                SELECT c.*, 
                       DATE_FORMAT(c.fecha_creacion, '%d/%m/%Y') as fecha_creacion_fmt,
                       COUNT(v.id) as total_compras,
                       COALESCE(SUM(v.total), 0) as total_gastado
                FROM clientes c
                LEFT JOIN ventas v ON c.id = v.cliente_id AND v.estado = 'completada'
                WHERE c.id = %s
                GROUP BY c.id
            """
            
            resultado = db.execute_query(cliente_query, (cliente_id,))
            if not resultado:
                return
            
            cliente = resultado[0]
            
            # Actualizar labels de información
            self.detail_labels['id'].config(text=str(cliente['id']))
            self.detail_labels['documento'].config(text=cliente.get('documento', '') or '-')
            self.detail_labels['nombre'].config(text=cliente['nombre'] or '-')
            self.detail_labels['telefono'].config(text=cliente.get('telefono', '') or '-')
            self.detail_labels['email'].config(text=cliente.get('email', '') or '-')
            self.detail_labels['direccion'].config(text=cliente.get('direccion', '') or '-')
            self.detail_labels['ciudad'].config(text=cliente.get('ciudad', '') or '-')
            self.detail_labels['estado'].config(
                text='🟢 Activo' if cliente['activo'] else '🔴 Inactivo'
            )
            self.detail_labels['fecha_creacion'].config(text=cliente['fecha_creacion_fmt'] or '-')
            
            # Actualizar estadísticas del cliente
            total_compras = cliente['total_compras'] or 0
            total_gastado = cliente['total_gastado'] or 0
            promedio_compra = total_gastado / total_compras if total_compras > 0 else 0
            
            self.stats_labels['total_compras'].config(text=f"{total_compras:,}")
            self.stats_labels['total_gastado'].config(text=f"${total_gastado:,.2f}")
            self.stats_labels['promedio_compra'].config(text=f"${promedio_compra:,.2f}")
            
        except Exception as e:
            print(f"❌ Error mostrando detalles: {str(e)}")
            messagebox.showerror("Error", f"Error mostrando detalles: {str(e)}")
    
    def buscar_clientes(self):
        """Busca clientes según el criterio"""
        termino = self.search_var.get().strip()
        
        if not termino:
            self.mostrar_clientes(self.clientes_data)
            return
        
        # Filtrar clientes
        clientes_filtrados = []
        termino_lower = termino.lower()
        
        for cliente in self.clientes_data:
            nombre = (cliente.get('nombre') or '').lower()
            documento = (cliente.get('documento') or '').lower()
            telefono = (cliente.get('telefono') or '').lower()
            email = (cliente.get('email') or '').lower()
            ciudad = (cliente.get('ciudad') or '').lower()
            
            if (termino_lower in nombre or 
                termino_lower in documento or
                termino_lower in telefono or 
                termino_lower in email or 
                termino_lower in ciudad):
                clientes_filtrados.append(cliente)
        
        self.mostrar_clientes(clientes_filtrados)
    
    def buscar_en_tiempo_real(self, *args):
        """Búsqueda en tiempo real mientras se escribe"""
        self.buscar_clientes()
    
    def limpiar_busqueda(self):
        """Limpia la búsqueda y muestra todos los clientes"""
        self.search_var.set("")
        self.mostrar_clientes(self.clientes_data)
    
    def nuevo_cliente(self):
        """Abre ventana para crear nuevo cliente"""
        self.abrir_ventana_cliente()
    
    def editar_cliente(self):
        """Abre ventana para editar cliente seleccionado"""
        if not self.cliente_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para editar")
            return
        
        self.abrir_ventana_cliente(self.cliente_seleccionado)
    
    def abrir_ventana_cliente(self, cliente_id=None):
        """Abre ventana de formulario de cliente"""
        try:
            ventana = ClienteFormWindow(self.parent, cliente_id, self.actualizar_lista)
        except Exception as e:
            print(f"❌ Error abriendo ventana de cliente: {str(e)}")
            messagebox.showerror("Error", f"Error abriendo formulario: {str(e)}")
    
    def eliminar_cliente(self):
        """Elimina el cliente seleccionado"""
        if not self.cliente_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
            return
        
        # Buscar nombre del cliente
        cliente_nombre = "Cliente"
        for cliente in self.clientes_data:
            if str(cliente['id']) == str(self.cliente_seleccionado):
                cliente_nombre = cliente['nombre']
                break
        
        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar al cliente '{cliente_nombre}'?\n\n"
            "Esta acción no se puede deshacer."
        )
        
        if respuesta:
            try:
                # Verificar si tiene ventas
                ventas_query = "SELECT COUNT(*) as total FROM ventas WHERE cliente_id = %s"
                ventas_result = db.execute_query(ventas_query, (self.cliente_seleccionado,))
                tiene_ventas = ventas_result[0]['total'] > 0 if ventas_result else False
                
                if tiene_ventas:
                    # No eliminar, solo desactivar
                    respuesta_desactivar = messagebox.askyesno(
                        "Cliente con Historial",
                        f"El cliente '{cliente_nombre}' tiene historial de ventas.\n\n"
                        "¿Desea desactivarlo en lugar de eliminarlo?\n"
                        "(Recomendado para mantener integridad de datos)"
                    )
                    
                    if respuesta_desactivar:
                        update_query = "UPDATE clientes SET activo = FALSE WHERE id = %s"
                        db.execute_query(update_query, (self.cliente_seleccionado,))
                        messagebox.showinfo("Éxito", f"Cliente '{cliente_nombre}' desactivado correctamente")
                    else:
                        return
                else:
                    # Eliminar completamente
                    delete_query = "DELETE FROM clientes WHERE id = %s"
                    db.execute_query(delete_query, (self.cliente_seleccionado,))
                    messagebox.showinfo("Éxito", f"Cliente '{cliente_nombre}' eliminado correctamente")
                
                # Refrescar lista
                self.actualizar_lista()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error eliminando cliente: {str(e)}")
    
    def ver_historial_cliente(self):
        """Muestra el historial de compras del cliente"""
        if not self.cliente_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para ver su historial")
            return
        
        messagebox.showinfo("Info", f"Historial del cliente ID: {self.cliente_seleccionado}\nFuncionalidad disponible en próxima versión")
    
    def nueva_venta_cliente(self):
        """Inicia una nueva venta para el cliente seleccionado"""
        if not self.cliente_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return
        
        messagebox.showinfo("Info", 
                           f"Funcionalidad para nueva venta al cliente ID: {self.cliente_seleccionado}\n"
                           "Se integrará con el módulo de ventas existente.")


class ClienteFormWindow:
    def __init__(self, parent, cliente_id=None, callback=None):
        self.parent = parent
        self.cliente_id = cliente_id
        self.callback = callback
        
        # Verificar que parent es válido
        if not parent:
            raise Exception("Parent window es requerido")
        
        self.setup_window()
        
        if cliente_id:
            self.cargar_datos_cliente()
    
    def setup_window(self):
        """Configura la ventana del formulario"""
        try:
            self.window = tk.Toplevel(self.parent)
            self.window.title("➕ Nuevo Cliente" if not self.cliente_id else "✏️ Editar Cliente")
            self.window.geometry("500x650")
            self.window.resizable(False, False)
            self.window.transient(self.parent)
            self.window.grab_set()
            
            # Centrar ventana
            self.center_window()
            
            # Frame principal
            main_frame = ttk.Frame(self.window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            title_text = "Editar Cliente" if self.cliente_id else "Nuevo Cliente"
            ttk.Label(main_frame, text=title_text, font=("Arial", 16, "bold")).pack(pady=(0, 20))
            
            # Frame del formulario
            form_frame = ttk.LabelFrame(main_frame, text="📝 Información del Cliente", padding="15")
            form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            # Campos del formulario
            self.setup_form_fields(form_frame)
            
            # Frame de botones
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X)
            
            # Botones
            ttk.Button(buttons_frame, text="💾 Guardar", 
                      command=self.guardar_cliente, width=15).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(buttons_frame, text="❌ Cancelar", 
                      command=self.window.destroy, width=15).pack(side=tk.LEFT)
            
            # Si es edición, agregar botón de activar/desactivar
            if self.cliente_id:
                ttk.Button(buttons_frame, text="🔄 Cambiar Estado", 
                          command=self.cambiar_estado, width=15).pack(side=tk.RIGHT)
                          
        except Exception as e:
            print(f"❌ Error creando ventana: {str(e)}")
            raise e
    
    def setup_form_fields(self, parent):
        """Configura los campos del formulario - CORREGIDO para tu estructura"""
        try:
            # Variables para los campos
            self.documento_var = tk.StringVar()
            self.nombre_var = tk.StringVar()
            self.telefono_var = tk.StringVar()
            self.email_var = tk.StringVar()
            self.direccion_var = tk.StringVar()
            self.ciudad_var = tk.StringVar()
            self.activo_var = tk.BooleanVar(value=True)
            
            # Campos del formulario
            campos = [
                ("Documento:", self.documento_var, ttk.Entry),
                ("Nombre Completo *:", self.nombre_var, ttk.Entry),
                ("Teléfono:", self.telefono_var, ttk.Entry),
                ("Email:", self.email_var, ttk.Entry),
                ("Dirección:", self.direccion_var, ttk.Entry),
                ("Ciudad:", self.ciudad_var, ttk.Entry),
            ]
            
            for i, (label_text, var, widget_class) in enumerate(campos):
                # Label
                ttk.Label(parent, text=label_text, font=("Arial", 10, "bold")).grid(
                    row=i, column=0, sticky="w", pady=5, padx=(0, 10))
                
                # Entry
                if widget_class == ttk.Entry:
                    entry = ttk.Entry(parent, textvariable=var, width=40, font=("Arial", 10))
                    entry.grid(row=i, column=1, sticky="w", pady=5)
                    
                    # Focus en primer campo
                    if i == 1:  # Nombre es obligatorio, focus ahí
                        entry.focus()
            
            # Campo activo (checkbox)
            ttk.Label(parent, text="Estado:", font=("Arial", 10, "bold")).grid(
                row=len(campos), column=0, sticky="w", pady=5, padx=(0, 10))
            
            ttk.Checkbutton(parent, text="Cliente Activo", variable=self.activo_var).grid(
                row=len(campos), column=1, sticky="w", pady=5)
            
            # Nota obligatorios
            ttk.Label(parent, text="* Campos obligatorios", 
                     font=("Arial", 8, "italic"), foreground="red").grid(
                row=len(campos)+1, column=0, columnspan=2, sticky="w", pady=(10, 0))
                
        except Exception as e:
            print(f"❌ Error configurando campos: {str(e)}")
            raise e
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        try:
            self.window.update_idletasks()
            x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
            y = (self.window.winfo_screenheight() // 2) - (650 // 2)
            self.window.geometry(f"500x650+{x}+{y}")
        except Exception as e:
            print(f"❌ Error centrando ventana: {str(e)}")
    
    def cargar_datos_cliente(self):
        """Carga los datos del cliente para edición"""
        try:
            query = "SELECT * FROM clientes WHERE id = %s"
            resultado = db.execute_query(query, (self.cliente_id,))
            
            if resultado:
                cliente = resultado[0]
                self.documento_var.set(cliente.get('documento', '') or '')
                self.nombre_var.set(cliente['nombre'] or '')
                self.telefono_var.set(cliente.get('telefono', '') or '')
                self.email_var.set(cliente.get('email', '') or '')
                self.direccion_var.set(cliente.get('direccion', '') or '')
                self.ciudad_var.set(cliente.get('ciudad', '') or '')
                self.activo_var.set(bool(cliente['activo']))
                
        except Exception as e:
            print(f"❌ Error cargando datos del cliente: {str(e)}")
            messagebox.showerror("Error", f"Error cargando datos del cliente: {str(e)}")
    
    def validar_campos(self):
        """Valida los campos del formulario"""
        if not self.nombre_var.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return False
        
        # Validar email si se proporciona
        email = self.email_var.get().strip()
        if email and '@' not in email:
            messagebox.showerror("Error", "El formato del email no es válido")
            return False
        
        return True
    
    def guardar_cliente(self):
        """Guarda el cliente en la base de datos - CORREGIDO para tu estructura"""
        if not self.validar_campos():
            return
        
        try:
            datos = {
                'documento': self.documento_var.get().strip() or None,
                'nombre': self.nombre_var.get().strip(),
                'telefono': self.telefono_var.get().strip() or None,
                'email': self.email_var.get().strip() or None,
                'direccion': self.direccion_var.get().strip() or None,
                'ciudad': self.ciudad_var.get().strip() or None,
                'activo': self.activo_var.get()
            }
            
            if self.cliente_id:
                # Actualizar cliente existente
                query = """
                    UPDATE clientes 
                    SET documento = %s, nombre = %s, telefono = %s, email = %s, 
                        direccion = %s, ciudad = %s, activo = %s
                    WHERE id = %s
                """
                params = (datos['documento'], datos['nombre'], datos['telefono'], datos['email'],
                         datos['direccion'], datos['ciudad'], datos['activo'], self.cliente_id)
                
                resultado = db.execute_query(query, params)
                print(f"📝 Update result: {resultado}")  # Debug
                messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
            else:
                # Crear nuevo cliente - usando fecha_creacion
                query = """
                    INSERT INTO clientes (documento, nombre, telefono, email, direccion, ciudad, activo, fecha_creacion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """
                params = (datos['documento'], datos['nombre'], datos['telefono'], datos['email'],
                         datos['direccion'], datos['ciudad'], datos['activo'])
                
                resultado = db.execute_query(query, params)
                print(f"📝 Insert result: {resultado}")  # Debug
                messagebox.showinfo("Éxito", "Cliente creado correctamente")
            
            # Ejecutar callback para actualizar la lista
            if self.callback:
                print("🔄 Ejecutando callback...")  # Debug
                self.callback()
            
            self.window.destroy()
            
        except Exception as e:
            error_msg = f"Error guardando cliente: {str(e)}"
            print(f"❌ {error_msg}")  # Debug
            messagebox.showerror("Error", error_msg)
    
    def cambiar_estado(self):
        """Cambia el estado activo/inactivo del cliente"""
        try:
            nuevo_estado = not self.activo_var.get()
            estado_texto = "activar" if nuevo_estado else "desactivar"
            
            respuesta = messagebox.askyesno(
                "Confirmar",
                f"¿Está seguro que desea {estado_texto} este cliente?"
            )
            
            if respuesta:
                query = "UPDATE clientes SET activo = %s WHERE id = %s"
                db.execute_query(query, (nuevo_estado, self.cliente_id))
                
                self.activo_var.set(nuevo_estado)
                messagebox.showinfo("Éxito", f"Cliente {'activado' if nuevo_estado else 'desactivado'} correctamente")
                
                if self.callback:
                    self.callback()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cambiando estado: {str(e)}")