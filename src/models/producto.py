# src/models/producto.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import db

class ProductoModel:
    @staticmethod
    def obtener_todos(filtro_texto="", categoria_id=None, activos_solo=True):
        """Obtiene todos los productos con filtros opcionales"""
        query = """
            SELECT p.*, c.nombre as categoria_nombre, pr.nombre as proveedor_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
            WHERE 1=1
        """
        params = []
        
        if activos_solo:
            query += " AND p.activo = TRUE"
        
        if filtro_texto:
            query += " AND (p.nombre LIKE %s OR p.codigo LIKE %s OR p.descripcion LIKE %s)"
            filtro = f"%{filtro_texto}%"
            params.extend([filtro, filtro, filtro])
        
        if categoria_id:
            query += " AND p.categoria_id = %s"
            params.append(categoria_id)
        
        query += " ORDER BY p.nombre"
        
        try:
            print(f"Ejecutando query: {query}")
            print(f"Con parámetros: {params}")
            result = db.execute_query(query, params)
            print(f"Productos obtenidos: {len(result) if result else 0}")
            return result or []
        except Exception as e:
            print(f"Error en obtener_todos: {e}")
            return []
    
    @staticmethod
    def obtener_por_id(producto_id):
        """Obtiene un producto por su ID"""
        query = """
            SELECT p.*, c.nombre as categoria_nombre, pr.nombre as proveedor_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
            WHERE p.id = %s
        """
        try:
            result = db.execute_query(query, (producto_id,))
            return result[0] if result else None
        except Exception as e:
            print(f"Error en obtener_por_id: {e}")
            return None
    
    @staticmethod
    def obtener_por_codigo(codigo):
        """Obtiene un producto por su código"""
        query = "SELECT * FROM productos WHERE codigo = %s AND activo = TRUE"
        try:
            result = db.execute_query(query, (codigo,))
            return result[0] if result else None
        except Exception as e:
            print(f"Error en obtener_por_codigo: {e}")
            return None
    
    @staticmethod
    def crear(datos):
        """Crea un nuevo producto"""
        query = """
            INSERT INTO productos (codigo, nombre, descripcion, categoria_id, 
                                 proveedor_id, precio_compra, precio_venta, 
                                 stock_actual, stock_minimo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            datos['codigo'],
            datos['nombre'],
            datos.get('descripcion', ''),
            datos.get('categoria_id'),
            datos.get('proveedor_id'),
            datos.get('precio_compra', 0),
            datos['precio_venta'],
            datos.get('stock_actual', 0),
            datos.get('stock_minimo', 5)
        )
        
        return db.execute_insert(query, params)
    
    @staticmethod
    def actualizar(producto_id, datos):
        """Actualiza un producto existente"""
        query = """
            UPDATE productos 
            SET codigo = %s, nombre = %s, descripcion = %s, categoria_id = %s,
                proveedor_id = %s, precio_compra = %s, precio_venta = %s,
                stock_actual = %s, stock_minimo = %s
            WHERE id = %s
        """
        params = (
            datos['codigo'],
            datos['nombre'],
            datos.get('descripcion', ''),
            datos.get('categoria_id'),
            datos.get('proveedor_id'),
            datos.get('precio_compra', 0),
            datos['precio_venta'],
            datos.get('stock_actual', 0),
            datos.get('stock_minimo', 5),
            producto_id
        )
        
        return db.execute_update(query, params)
    
    @staticmethod
    def eliminar(producto_id):
        """Desactiva un producto (eliminación lógica)"""
        query = "UPDATE productos SET activo = FALSE WHERE id = %s"
        return db.execute_update(query, (producto_id,))
    
    @staticmethod
    def activar(producto_id):
        """Reactiva un producto"""
        query = "UPDATE productos SET activo = TRUE WHERE id = %s"
        return db.execute_update(query, (producto_id,))
    
    @staticmethod
    def obtener_stock_bajo():
        """Obtiene productos con stock bajo"""
        query = """
            SELECT p.*, c.nombre as categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.stock_actual <= p.stock_minimo AND p.activo = TRUE
            ORDER BY p.stock_actual ASC
        """
        return db.execute_query(query)
    
    @staticmethod
    def actualizar_stock(producto_id, cantidad, operacion='suma'):
        """Actualiza el stock de un producto"""
        if operacion == 'suma':
            query = "UPDATE productos SET stock_actual = stock_actual + %s WHERE id = %s"
        else:
            query = "UPDATE productos SET stock_actual = stock_actual - %s WHERE id = %s"
        
        return db.execute_update(query, (cantidad, producto_id))
    
    @staticmethod
    def verificar_codigo_unico(codigo, producto_id=None):
        """Verifica si un código es único"""
        if producto_id:
            query = "SELECT id FROM productos WHERE codigo = %s AND id != %s"
            params = (codigo, producto_id)
        else:
            query = "SELECT id FROM productos WHERE codigo = %s"
            params = (codigo,)
        
        result = db.execute_query(query, params)
        return len(result) == 0

class CategoriaModel:
    @staticmethod
    def obtener_todas(activas_solo=True):
        """Obtiene todas las categorías"""
        query = "SELECT * FROM categorias"
        if activas_solo:
            query += " WHERE activo = TRUE"
        query += " ORDER BY nombre"
        
        try:
            print(f"Ejecutando query categorías: {query}")
            result = db.execute_query(query)
            print(f"Categorías obtenidas: {len(result) if result else 0}")
            return result or []
        except Exception as e:
            print(f"Error en obtener_todas categorías: {e}")
            return []
    
    @staticmethod
    def crear(nombre, descripcion=""):
        """Crea una nueva categoría"""
        query = "INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)"
        return db.execute_insert(query, (nombre, descripcion))
    
    @staticmethod
    def actualizar(categoria_id, nombre, descripcion=""):
        """Actualiza una categoría"""
        query = "UPDATE categorias SET nombre = %s, descripcion = %s WHERE id = %s"
        return db.execute_update(query, (nombre, descripcion, categoria_id))
    
    @staticmethod
    def eliminar(categoria_id):
        """Desactiva una categoría"""
        query = "UPDATE categorias SET activo = FALSE WHERE id = %s"
        return db.execute_update(query, (categoria_id,))

class ProveedorModel:
    @staticmethod
    def obtener_todos(activos_solo=True):
        """Obtiene todos los proveedores"""
        query = "SELECT * FROM proveedores"
        if activos_solo:
            query += " WHERE activo = TRUE"
        query += " ORDER BY nombre"
        
        return db.execute_query(query)
    
    @staticmethod
    def crear(datos):
        """Crea un nuevo proveedor"""
        query = """
            INSERT INTO proveedores (nombre, contacto, telefono, email, direccion)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            datos['nombre'],
            datos.get('contacto', ''),
            datos.get('telefono', ''),
            datos.get('email', ''),
            datos.get('direccion', '')
        )
        return db.execute_insert(query, params)