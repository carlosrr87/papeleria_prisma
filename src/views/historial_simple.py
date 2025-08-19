# src/views/historial_simple.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from models.compra import CompraModel
except ImportError as e:
    print(f"Error importando modelos: {e}")

class HistorialComprasView:
    def __init__(self, parent, usuario_data):
        self.parent = parent
        self.usuario_data = usuario_data
        self.frame = None
        self.compras_data = []
        
        self.crear_interfaz()
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
        
        # Botones de acción
        ttk.Button(title_frame, text="Actualizar", 
                  command=self.cargar_compras).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(title_frame, text="Ver Detalle", 
                  command=self.ver_detalle).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(title_frame, text="Recibir Compra", 
                  command=self.recibir_compra).pack(side=tk.RIGHT, padx=(5, 0))
        
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
        columns = ('numero', 'fecha', 'proveedor', 'total', 'estado')
        
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        # Configurar encabezados
        self.tree.heading('numero', text='Número')
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('proveedor', text='Proveedor')
        self.tree.heading('total', text='Total')
        self.tree.heading('estado', text='Estado')
        
        # Configurar anchos
        self.tree.column('numero', width=150)
        self.tree.column('fecha', width=150)
        self.tree.column('proveedor', width=200)
        self.tree.column('total', width=100)
        self.tree.column('estado', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind doble click
        self.tree.bind('<Double-1>', lambda e: self.ver_detalle())
    
    def cargar_compras(self):
        """Carga las compras"""
        try:
            # Obtener compras del último mes
            fecha_fin = date.today()
            fecha_inicio = fecha_fin - timedelta(days=30)
            
            self.compras_data = CompraModel.obtener_compras(
                fecha_inicio.strftime("%Y-%m-%d"),
                fecha_fin.strftime("%Y-%m-%d")
            )
            
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
                fecha_formatted = compra['fecha_compra'].strftime("%d/%m/%Y")
                
                self.tree.insert('', tk.END, values=(
                    compra['numero_compra'],
                    fecha_formatted,
                    compra['proveedor_nombre'],
                    f"${compra['total']:,.2f}",
                    compra['estado'].title()
                ), tags=tags)
                
                total_compras += 1
                total_monto += compra['total']
                if compra['estado'] == 'pendiente':
                    compras_pendientes += 1
            
            # Configurar colores
            self.tree.tag_configure('cancelada', background='#ffcccc')
            self.tree.tag_configure('pendiente', background='#fff2cc')
            self.tree.tag_configure('recibida', background='#ccffcc')
            
            # Actualizar resumen
            promedio = total_monto / total_compras if total_compras > 0 else 0
            self.resumen_label.config(
                text=f"Compras (últimos 30 días): {total_compras} | "
                     f"Total: ${total_monto:,.2f} | "
                     f"Promedio: ${promedio:,.2f} | "
                     f"Pendientes: {compras_pendientes}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando compras: {str(e)}")
    
    def ver_detalle(self):
        """Ver detalle de la compra seleccionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una compra")
            return
        
        # Obtener compra seleccionada
        item = self.tree.item(selected[0])
        numero_compra = item['values'][0]
        
        # Buscar compra en los datos
        compra_seleccionada = None
        for compra in self.compras_data:
            if compra['numero_compra'] == numero_compra:
                compra_seleccionada = compra
                break
        
        if compra_seleccionada:
            self.mostrar_detalle_compra(compra_seleccionada)
    
    def mostrar_detalle_compra(self, compra):
        """Muestra el detalle de una compra"""
        try:
            # Obtener detalle completo
            detalle_completo = CompraModel.obtener_compra_por_id(compra['id'])
            
            # Crear ventana de detalle
            detalle_window = tk.Toplevel(self.frame)
            detalle_window.title(f"Detalle - {compra['numero_compra']}")
            detalle_window.geometry("700x500")
            detalle_window.transient(self.frame)
            
            # Información general
            info_frame = ttk.LabelFrame(detalle_window, text="Información", padding="10")
            info_frame.pack(fill=tk.X, padx=10, pady=10)
            
            info_text = f"""Número: {detalle_completo['numero_compra']}
Fecha: {detalle_completo['fecha_compra'].strftime('%d/%m/%Y %H:%M')}
Proveedor: {detalle_completo['proveedor_nombre']}
Estado: {detalle_completo['estado'].title()}
Total: ${detalle_completo['total']:,.2f}"""
            
            ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)
            
            # Productos
            productos_frame = ttk.LabelFrame(detalle_window, text="Productos", padding="10")
            productos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Tabla de productos
            columns = ('codigo', 'nombre', 'cantidad', 'precio', 'subtotal')
            productos_tree = ttk.Treeview(productos_frame, columns=columns, 
                                         show='headings', height=10)
            
            # Configurar encabezados
            productos_tree.heading('codigo', text='Código')
            productos_tree.heading('nombre', text='Producto')
            productos_tree.heading('cantidad', text='Cantidad')
            productos_tree.heading('precio', text='Precio')
            productos_tree.heading('subtotal', text='Subtotal')
            
            productos_tree.pack(fill=tk.BOTH, expand=True)
            
            # Llenar productos
            for detalle in detalle_completo['detalles']:
                productos_tree.insert('', tk.END, values=(
                    detalle['producto_codigo'],
                    detalle['producto_nombre'],
                    detalle['cantidad'],
                    f"${detalle['precio_unitario']:,.2f}",
                    f"${detalle['subtotal']:,.2f}"
                ))
            
            # Botón cerrar
            ttk.Button(detalle_window, text="Cerrar", 
                      command=detalle_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando detalle: {str(e)}")
    
    def recibir_compra(self):
        """Recibe la compra seleccionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una compra")
            return
        
        item = self.tree.item(selected[0])
        numero_compra = item['values'][0]
        estado = item['values'][4].lower()
        
        if estado != 'pendiente':
            messagebox.showerror("Error", "Solo se pueden recibir compras pendientes")
            return
        
        # Buscar compra en los datos
        compra_seleccionada = None
        for compra in self.compras_data:
            if compra['numero_compra'] == numero_compra:
                compra_seleccionada = compra
                break
        
        if compra_seleccionada:
            # Confirmar recepción
            if messagebox.askyesno("Confirmar", 
                                  f"¿Confirmar recepción de la compra {numero_compra}?\n"
                                  "Esta acción actualizará el stock de todos los productos."):
                
                try:
                    if CompraModel.recibir_compra(compra_seleccionada['id'], self.usuario_data['id']):
                        messagebox.showinfo("Éxito", 
                                          "Compra recibida correctamente.\n"
                                          "El stock ha sido actualizado.")
                        self.cargar_compras()  # Recargar lista
                    else:
                        messagebox.showerror("Error", "No se pudo recibir la compra")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Error recibiendo compra: {str(e)}")