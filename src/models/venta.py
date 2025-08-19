# src/models/venta.py
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import db

class VentaModel:
    @staticmethod
    def generar_numero_venta():
        """Genera el siguiente número de venta"""
        try:
            # Obtener el último número de venta del día
            query = """
                SELECT numero_venta 
                FROM ventas 
                WHERE DATE(fecha_venta) = CURDATE() 
                ORDER BY numero_venta DESC 
                LIMIT 1
            """
            result = db.execute_query(query)
            
            # Generar número basado en fecha y secuencia
            fecha_actual = datetime.now().strftime("%Y%m%d")
            
            if result and result[0]['numero_venta']:
                ultimo_numero = result[0]['numero_venta']
                # Extraer secuencia del último número (formato: YYYYMMDD-XXX)
                if '-' in ultimo_numero:
                    secuencia = int(ultimo_numero.split('-')[1]) + 1
                else:
                    secuencia = 1
            else:
                secuencia = 1
            
            return f"{fecha_actual}-{secuencia:03d}"
            
        except Exception as e:
            print(f"Error generando número de venta: {e}")
            # Fallback: usar timestamp
            return f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    @staticmethod
    def crear_venta(datos_venta, detalle_items):
        """Crea una nueva venta con sus detalles"""
        try:
            # Iniciar transacción manualmente
            if not db.connect():
                return None
            
            connection = db.connection
            cursor = connection.cursor()
            
            # Deshabilitar autocommit para manejar transacción
            connection.autocommit = False
            
            try:
                # 1. Insertar venta
                venta_query = """
                    INSERT INTO ventas (numero_venta, cliente_id, usuario_id, 
                                      fecha_venta, subtotal, impuesto, total, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(venta_query, (
                    datos_venta['numero_venta'],
                    datos_venta.get('cliente_id'),
                    datos_venta['usuario_id'],
                    datos_venta['fecha_venta'],
                    datos_venta['subtotal'],
                    datos_venta['impuesto'],
                    datos_venta['total'],
                    'completada'
                ))
                
                venta_id = cursor.lastrowid
                
                # 2. Insertar detalles de venta
                detalle_query = """
                    INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, 
                                              precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """
                
                for item in detalle_items:
                    cursor.execute(detalle_query, (
                        venta_id,
                        item['producto_id'],
                        item['cantidad'],
                        item['precio_unitario'],
                        item['subtotal']
                    ))
                    
                    # 3. Actualizar stock del producto
                    stock_query = """
                        UPDATE productos 
                        SET stock_actual = stock_actual - %s 
                        WHERE id = %s
                    """
                    cursor.execute(stock_query, (item['cantidad'], item['producto_id']))
                
                # Confirmar transacción
                connection.commit()
                cursor.close()
                
                print(f"Venta creada exitosamente. ID: {venta_id}")
                return venta_id
                
            except Exception as e:
                # Revertir transacción en caso de error
                connection.rollback()
                cursor.close()
                print(f"Error en transacción de venta: {e}")
                return None
                
        except Exception as e:
            print(f"Error creando venta: {e}")
            return None
        finally:
            # Restaurar autocommit
            if 'connection' in locals():
                connection.autocommit = True
    
    @staticmethod
    def obtener_ventas(fecha_inicio=None, fecha_fin=None, cliente_id=None):
        """Obtiene ventas con filtros opcionales"""
        query = """
            SELECT v.*, c.nombre as cliente_nombre, u.nombre as usuario_nombre
            FROM ventas v
            LEFT JOIN clientes c ON v.cliente_id = c.id
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            WHERE 1=1
        """
        params = []
        
        if fecha_inicio:
            query += " AND DATE(v.fecha_venta) >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND DATE(v.fecha_venta) <= %s"
            params.append(fecha_fin)
        
        if cliente_id:
            query += " AND v.cliente_id = %s"
            params.append(cliente_id)
        
        query += " ORDER BY v.fecha_venta DESC"
        
        try:
            result = db.execute_query(query, params)
            return result or []
        except Exception as e:
            print(f"Error obteniendo ventas: {e}")
            return []
    
    @staticmethod
    def obtener_venta_por_id(venta_id):
        """Obtiene una venta específica con sus detalles"""
        try:
            # Obtener datos de la venta
            venta_query = """
                SELECT v.*, c.nombre as cliente_nombre, c.documento as cliente_documento,
                       u.nombre as usuario_nombre
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                LEFT JOIN usuarios u ON v.usuario_id = u.id
                WHERE v.id = %s
            """
            venta_result = db.execute_query(venta_query, (venta_id,))
            
            if not venta_result:
                return None
            
            venta = venta_result[0]
            
            # Obtener detalles de la venta
            detalle_query = """
                SELECT dv.*, p.codigo as producto_codigo, p.nombre as producto_nombre
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                WHERE dv.venta_id = %s
                ORDER BY p.nombre
            """
            detalle_result = db.execute_query(detalle_query, (venta_id,))
            
            venta['detalles'] = detalle_result or []
            return venta
            
        except Exception as e:
            print(f"Error obteniendo venta por ID: {e}")
            return None
    
    @staticmethod
    def cancelar_venta(venta_id, usuario_id):
        """Cancela una venta y restaura el stock"""
        try:
            if not db.connect():
                return False
            
            connection = db.connection
            cursor = connection.cursor()
            connection.autocommit = False
            
            try:
                # 1. Obtener detalles de la venta para restaurar stock
                detalle_query = """
                    SELECT producto_id, cantidad 
                    FROM detalle_ventas 
                    WHERE venta_id = %s
                """
                cursor.execute(detalle_query, (venta_id,))
                detalles = cursor.fetchall()
                
                # 2. Restaurar stock de cada producto
                for detalle in detalles:
                    stock_query = """
                        UPDATE productos 
                        SET stock_actual = stock_actual + %s 
                        WHERE id = %s
                    """
                    cursor.execute(stock_query, (detalle[1], detalle[0]))
                
                # 3. Marcar venta como cancelada
                venta_query = """
                    UPDATE ventas 
                    SET estado = 'cancelada' 
                    WHERE id = %s
                """
                cursor.execute(venta_query, (venta_id,))
                
                connection.commit()
                cursor.close()
                
                print(f"Venta {venta_id} cancelada exitosamente")
                return True
                
            except Exception as e:
                connection.rollback()
                cursor.close()
                print(f"Error cancelando venta: {e}")
                return False
                
        except Exception as e:
            print(f"Error en cancelar_venta: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.autocommit = True
    
    @staticmethod
    def obtener_ventas_por_periodo(fecha_inicio, fecha_fin):
        """Obtiene resumen de ventas por período"""
        query = """
            SELECT 
                COUNT(*) as total_ventas,
                SUM(total) as total_ingresos,
                AVG(total) as promedio_venta,
                DATE(fecha_venta) as fecha
            FROM ventas 
            WHERE DATE(fecha_venta) BETWEEN %s AND %s 
            AND estado = 'completada'
            GROUP BY DATE(fecha_venta)
            ORDER BY fecha DESC
        """
        
        try:
            result = db.execute_query(query, (fecha_inicio, fecha_fin))
            return result or []
        except Exception as e:
            print(f"Error obteniendo ventas por período: {e}")
            return []

class ClienteModel:
    @staticmethod
    def obtener_todos(activos_solo=True):
        """Obtiene todos los clientes"""
        query = "SELECT * FROM clientes"
        if activos_solo:
            query += " WHERE activo = TRUE"
        query += " ORDER BY nombre"
        
        try:
            result = db.execute_query(query)
            return result or []
        except Exception as e:
            print(f"Error obteniendo clientes: {e}")
            return []
    
    @staticmethod
    def buscar_clientes(texto_busqueda):
        """Busca clientes por nombre o documento"""
        query = """
            SELECT * FROM clientes 
            WHERE (nombre LIKE %s OR documento LIKE %s) 
            AND activo = TRUE
            ORDER BY nombre
            LIMIT 10
        """
        filtro = f"%{texto_busqueda}%"
        
        try:
            result = db.execute_query(query, (filtro, filtro))
            return result or []
        except Exception as e:
            print(f"Error buscando clientes: {e}")
            return []
    
    @staticmethod
    def crear(datos):
        """Crea un nuevo cliente"""
        query = """
            INSERT INTO clientes (documento, nombre, telefono, email, direccion)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            datos.get('documento', ''),
            datos['nombre'],
            datos.get('telefono', ''),
            datos.get('email', ''),
            datos.get('direccion', '')
        )
        
        try:
            return db.execute_insert(query, params)
        except Exception as e:
            print(f"Error creando cliente: {e}")
            return None
    
    @staticmethod
    def obtener_por_id(cliente_id):
        """Obtiene un cliente por su ID"""
        query = "SELECT * FROM clientes WHERE id = %s"
        
        try:
            result = db.execute_query(query, (cliente_id,))
            return result[0] if result else None
        except Exception as e:
            print(f"Error obteniendo cliente por ID: {e}")
            return None