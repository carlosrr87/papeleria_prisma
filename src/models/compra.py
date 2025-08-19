# src/models/compra.py
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import db

class CompraModel:
    @staticmethod
    def generar_numero_compra():
        """Genera el siguiente número de compra"""
        try:
            # Obtener el último número de compra del día
            query = """
                SELECT numero_compra 
                FROM compras 
                WHERE DATE(fecha_compra) = CURDATE() 
                ORDER BY numero_compra DESC 
                LIMIT 1
            """
            result = db.execute_query(query)
            
            # Generar número basado en fecha y secuencia
            fecha_actual = datetime.now().strftime("%Y%m%d")
            
            if result and result[0]['numero_compra']:
                ultimo_numero = result[0]['numero_compra']
                # Extraer secuencia del último número (formato: OC-YYYYMMDD-XXX)
                if '-' in ultimo_numero:
                    partes = ultimo_numero.split('-')
                    if len(partes) >= 3:
                        secuencia = int(partes[2]) + 1
                    else:
                        secuencia = 1
                else:
                    secuencia = 1
            else:
                secuencia = 1
            
            return f"OC-{fecha_actual}-{secuencia:03d}"
            
        except Exception as e:
            print(f"Error generando número de compra: {e}")
            # Fallback: usar timestamp
            return f"OC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    @staticmethod
    def crear_compra(datos_compra, detalle_items):
        """Crea una nueva orden de compra con sus detalles"""
        try:
            if not db.connect():
                return None
            
            connection = db.connection
            cursor = connection.cursor()
            connection.autocommit = False
            
            try:
                # 1. Insertar compra
                compra_query = """
                    INSERT INTO compras (numero_compra, proveedor_id, usuario_id, 
                                       fecha_compra, total, estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(compra_query, (
                    datos_compra['numero_compra'],
                    datos_compra['proveedor_id'],
                    datos_compra['usuario_id'],
                    datos_compra['fecha_compra'],
                    datos_compra['total'],
                    'pendiente'
                ))
                
                compra_id = cursor.lastrowid
                
                # 2. Insertar detalles de compra
                detalle_query = """
                    INSERT INTO detalle_compras (compra_id, producto_id, cantidad, 
                                               precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """
                
                for item in detalle_items:
                    cursor.execute(detalle_query, (
                        compra_id,
                        item['producto_id'],
                        item['cantidad'],
                        item['precio_unitario'],
                        item['subtotal']
                    ))
                
                # Confirmar transacción
                connection.commit()
                cursor.close()
                
                print(f"Compra creada exitosamente. ID: {compra_id}")
                return compra_id
                
            except Exception as e:
                connection.rollback()
                cursor.close()
                print(f"Error en transacción de compra: {e}")
                raise e
                
        except Exception as e:
            print(f"Error creando compra: {e}")
            return None
        finally:
            if 'connection' in locals():
                connection.autocommit = True
    
    @staticmethod
    def obtener_compras(fecha_inicio=None, fecha_fin=None, proveedor_id=None, estado=None):
        """Obtiene compras con filtros opcionales"""
        query = """
            SELECT c.*, p.nombre as proveedor_nombre, u.nombre as usuario_nombre
            FROM compras c
            LEFT JOIN proveedores p ON c.proveedor_id = p.id
            LEFT JOIN usuarios u ON c.usuario_id = u.id
            WHERE 1=1
        """
        params = []
        
        if fecha_inicio:
            query += " AND DATE(c.fecha_compra) >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND DATE(c.fecha_compra) <= %s"
            params.append(fecha_fin)
        
        if proveedor_id:
            query += " AND c.proveedor_id = %s"
            params.append(proveedor_id)
        
        if estado:
            query += " AND c.estado = %s"
            params.append(estado)
        
        query += " ORDER BY c.fecha_compra DESC"
        
        try:
            result = db.execute_query(query, params)
            return result or []
        except Exception as e:
            print(f"Error obteniendo compras: {e}")
            return []
    
    @staticmethod
    def obtener_compra_por_id(compra_id):
        """Obtiene una compra específica con sus detalles"""
        try:
            # Obtener datos de la compra
            compra_query = """
                SELECT c.*, p.nombre as proveedor_nombre, p.contacto as proveedor_contacto,
                       p.telefono as proveedor_telefono, u.nombre as usuario_nombre
                FROM compras c
                LEFT JOIN proveedores p ON c.proveedor_id = p.id
                LEFT JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.id = %s
            """
            compra_result = db.execute_query(compra_query, (compra_id,))
            
            if not compra_result:
                return None
            
            compra = compra_result[0]
            
            # Obtener detalles de la compra
            detalle_query = """
                SELECT dc.*, p.codigo as producto_codigo, p.nombre as producto_nombre,
                       p.stock_actual as producto_stock_actual
                FROM detalle_compras dc
                JOIN productos p ON dc.producto_id = p.id
                WHERE dc.compra_id = %s
                ORDER BY p.nombre
            """
            detalle_result = db.execute_query(detalle_query, (compra_id,))
            
            compra['detalles'] = detalle_result or []
            return compra
            
        except Exception as e:
            print(f"Error obteniendo compra por ID: {e}")
            return None
    
    @staticmethod
    def recibir_compra(compra_id, usuario_id, cantidades_recibidas=None):
        """Marca una compra como recibida y actualiza el stock"""
        try:
            if not db.connect():
                return False
            
            connection = db.connection
            cursor = connection.cursor()
            connection.autocommit = False
            
            try:
                # Verificar que la compra esté pendiente
                compra_query = "SELECT estado FROM compras WHERE id = %s"
                cursor.execute(compra_query, (compra_id,))
                compra_result = cursor.fetchone()
                
                if not compra_result:
                    raise Exception("Compra no encontrada")
                
                if compra_result[0] != 'pendiente':
                    raise Exception("La compra no está en estado pendiente")
                
                # Obtener detalles de la compra
                detalle_query = """
                    SELECT producto_id, cantidad 
                    FROM detalle_compras 
                    WHERE compra_id = %s
                """
                cursor.execute(detalle_query, (compra_id,))
                detalles = cursor.fetchall()
                
                # Actualizar stock de cada producto
                for detalle in detalles:
                    producto_id, cantidad_ordenada = detalle
                    
                    # Si se especificaron cantidades recibidas, usar esas
                    # sino usar la cantidad ordenada
                    cantidad_recibida = cantidad_ordenada
                    if cantidades_recibidas and producto_id in cantidades_recibidas:
                        cantidad_recibida = cantidades_recibidas[producto_id]
                    
                    if cantidad_recibida > 0:
                        stock_query = """
                            UPDATE productos 
                            SET stock_actual = stock_actual + %s 
                            WHERE id = %s
                        """
                        cursor.execute(stock_query, (cantidad_recibida, producto_id))
                        
                        if cursor.rowcount == 0:
                            raise Exception(f"No se pudo actualizar el stock del producto ID: {producto_id}")
                
                # Marcar compra como recibida
                compra_update_query = """
                    UPDATE compras 
                    SET estado = 'recibida' 
                    WHERE id = %s
                """
                cursor.execute(compra_update_query, (compra_id,))
                
                if cursor.rowcount == 0:
                    raise Exception("No se pudo actualizar el estado de la compra")
                
                connection.commit()
                cursor.close()
                
                print(f"Compra {compra_id} recibida exitosamente")
                return True
                
            except Exception as e:
                connection.rollback()
                cursor.close()
                print(f"Error recibiendo compra: {e}")
                return False
                
        except Exception as e:
            print(f"Error en recibir_compra: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.autocommit = True
    
    @staticmethod
    def cancelar_compra(compra_id, usuario_id):
        """Cancela una orden de compra"""
        try:
            # Verificar que la compra esté pendiente
            compra = CompraModel.obtener_compra_por_id(compra_id)
            if not compra:
                return False
            
            if compra['estado'] != 'pendiente':
                raise Exception("Solo se pueden cancelar compras pendientes")
            
            # Actualizar estado
            query = "UPDATE compras SET estado = 'cancelada' WHERE id = %s"
            return db.execute_update(query, (compra_id,))
            
        except Exception as e:
            print(f"Error cancelando compra: {e}")
            return False
    
    @staticmethod
    def obtener_productos_bajo_minimo():
        """Obtiene productos que están por debajo del stock mínimo"""
        query = """
            SELECT p.*, c.nombre as categoria_nombre, pr.nombre as proveedor_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
            WHERE p.stock_actual <= p.stock_minimo 
            AND p.activo = TRUE
            ORDER BY (p.stock_actual - p.stock_minimo) ASC, p.nombre
        """
        
        try:
            result = db.execute_query(query)
            return result or []
        except Exception as e:
            print(f"Error obteniendo productos bajo mínimo: {e}")
            return []
    
    @staticmethod
    def generar_orden_sugerida(proveedor_id=None):
        """Genera una orden de compra sugerida basada en productos con stock bajo"""
        try:
            productos_bajo_minimo = CompraModel.obtener_productos_bajo_minimo()
            
            if proveedor_id:
                # Filtrar solo productos del proveedor especificado
                productos_filtrados = [p for p in productos_bajo_minimo if p['proveedor_id'] == proveedor_id]
            else:
                productos_filtrados = productos_bajo_minimo
            
            # Generar sugerencias de cantidad
            sugerencias = []
            for producto in productos_filtrados:
                cantidad_faltante = producto['stock_minimo'] - producto['stock_actual']
                cantidad_sugerida = max(cantidad_faltante, producto['stock_minimo']) * 2  # Comprar para 2 períodos
                
                sugerencias.append({
                    'producto_id': producto['id'],
                    'codigo': producto['codigo'],
                    'nombre': producto['nombre'],
                    'stock_actual': producto['stock_actual'],
                    'stock_minimo': producto['stock_minimo'],
                    'cantidad_sugerida': cantidad_sugerida,
                    'precio_compra': producto['precio_compra'] or 0,
                    'proveedor_id': producto['proveedor_id'],
                    'proveedor_nombre': producto['proveedor_nombre']
                })
            
            return sugerencias
            
        except Exception as e:
            print(f"Error generando orden sugerida: {e}")
            return []

class ProveedorModelExtendido:
    @staticmethod
    def obtener_todos_con_productos(activos_solo=True):
        """Obtiene todos los proveedores con la cantidad de productos que suministran"""
        query = """
            SELECT p.*, 
                   COUNT(pr.id) as total_productos,
                   COUNT(CASE WHEN pr.stock_actual <= pr.stock_minimo THEN 1 END) as productos_bajo_stock
            FROM proveedores p
            LEFT JOIN productos pr ON p.id = pr.proveedor_id AND pr.activo = TRUE
        """
        
        if activos_solo:
            query += " WHERE p.activo = TRUE"
        
        query += " GROUP BY p.id ORDER BY p.nombre"
        
        try:
            result = db.execute_query(query)
            return result or []
        except Exception as e:
            print(f"Error obteniendo proveedores con productos: {e}")
            return []
    
    @staticmethod
    def obtener_productos_proveedor(proveedor_id):
        """Obtiene todos los productos de un proveedor específico"""
        query = """
            SELECT p.*, c.nombre as categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.proveedor_id = %s AND p.activo = TRUE
            ORDER BY p.nombre
        """
        
        try:
            result = db.execute_query(query, (proveedor_id,))
            return result or []
        except Exception as e:
            print(f"Error obteniendo productos del proveedor: {e}")
            return []
    
    @staticmethod
    def actualizar_precios_proveedor(proveedor_id, actualizaciones_precios):
        """Actualiza los precios de compra de productos de un proveedor"""
        try:
            if not db.connect():
                return False
            
            connection = db.connection
            cursor = connection.cursor()
            connection.autocommit = False
            
            try:
                for producto_id, nuevo_precio in actualizaciones_precios.items():
                    query = """
                        UPDATE productos 
                        SET precio_compra = %s 
                        WHERE id = %s AND proveedor_id = %s
                    """
                    cursor.execute(query, (nuevo_precio, producto_id, proveedor_id))
                
                connection.commit()
                cursor.close()
                return True
                
            except Exception as e:
                connection.rollback()
                cursor.close()
                print(f"Error actualizando precios: {e}")
                return False
                
        except Exception as e:
            print(f"Error en actualizar_precios_proveedor: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.autocommit = True