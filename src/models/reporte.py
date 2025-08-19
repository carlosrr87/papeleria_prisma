# src/models/reporte.py
import sys
import os
from datetime import datetime, date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import db

class ReporteModel:
    
    @staticmethod
    def obtener_resumen_inventario():
        """Obtiene resumen completo del inventario"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_productos,
                    SUM(stock_actual) as total_stock,
                    SUM(stock_actual * precio_venta) as valor_total_inventario,
                    COUNT(CASE WHEN stock_actual <= stock_minimo THEN 1 END) as productos_stock_bajo,
                    COUNT(CASE WHEN stock_actual = 0 THEN 1 END) as productos_sin_stock,
                    AVG(precio_venta) as precio_promedio
                FROM productos 
                WHERE activo = TRUE
            """
            result = db.execute_query(query)
            return result[0] if result else None
        except Exception as e:
            print(f"Error obteniendo resumen inventario: {e}")
            return None
    
    @staticmethod
    def obtener_productos_inventario():
        """Obtiene lista completa de productos para inventario"""
        try:
            query = """
                SELECT 
                    p.codigo,
                    p.nombre,
                    c.nombre as categoria,
                    pr.nombre as proveedor,
                    p.stock_actual,
                    p.stock_minimo,
                    p.precio_compra,
                    p.precio_venta,
                    (p.stock_actual * p.precio_venta) as valor_stock,
                    CASE 
                        WHEN p.stock_actual = 0 THEN 'Sin Stock'
                        WHEN p.stock_actual <= p.stock_minimo THEN 'Stock Bajo'
                        ELSE 'Normal'
                    END as estado_stock
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
                WHERE p.activo = TRUE
                ORDER BY p.nombre
            """
            return db.execute_query(query) or []
        except Exception as e:
            print(f"Error obteniendo productos inventario: {e}")
            return []
    
    @staticmethod
    def obtener_ventas_por_periodo(fecha_inicio, fecha_fin):
        """Obtiene ventas detalladas por período"""
        try:
            query = """
                SELECT 
                    v.numero_venta,
                    v.fecha_venta,
                    COALESCE(c.nombre, 'Cliente General') as cliente_nombre,
                    u.nombre as usuario_nombre,
                    v.subtotal,
                    v.impuesto,
                    v.total,
                    v.estado,
                    COUNT(dv.id) as total_items
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                LEFT JOIN usuarios u ON v.usuario_id = u.id
                LEFT JOIN detalle_ventas dv ON v.id = dv.venta_id
                WHERE DATE(v.fecha_venta) BETWEEN %s AND %s
                GROUP BY v.id
                ORDER BY v.fecha_venta DESC
            """
            return db.execute_query(query, (fecha_inicio, fecha_fin)) or []
        except Exception as e:
            print(f"Error obteniendo ventas por período: {e}")
            return []
    
    @staticmethod
    def obtener_resumen_ventas(fecha_inicio, fecha_fin):
        """Obtiene resumen de ventas por período"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_ventas,
                    SUM(total) as total_ingresos,
                    AVG(total) as promedio_venta,
                    COUNT(CASE WHEN estado = 'completada' THEN 1 END) as ventas_completadas,
                    COUNT(CASE WHEN estado = 'cancelada' THEN 1 END) as ventas_canceladas,
                    SUM(CASE WHEN estado = 'completada' THEN total ELSE 0 END) as ingresos_reales
                FROM ventas 
                WHERE DATE(fecha_venta) BETWEEN %s AND %s
            """
            result = db.execute_query(query, (fecha_inicio, fecha_fin))
            return result[0] if result else None
        except Exception as e:
            print(f"Error obteniendo resumen ventas: {e}")
            return None
    
    @staticmethod
    def obtener_productos_mas_vendidos(fecha_inicio, fecha_fin, limite=20):
        """Obtiene productos más vendidos en un período"""
        try:
            query = """
                SELECT 
                    p.codigo,
                    p.nombre,
                    c.nombre as categoria,
                    SUM(dv.cantidad) as total_vendido,
                    SUM(dv.subtotal) as total_ingresos,
                    AVG(dv.precio_unitario) as precio_promedio,
                    COUNT(DISTINCT dv.venta_id) as num_ventas
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                LEFT JOIN categorias c ON p.categoria_id = c.id
                JOIN ventas v ON dv.venta_id = v.id
                WHERE DATE(v.fecha_venta) BETWEEN %s AND %s
                AND v.estado = 'completada'
                GROUP BY p.id
                ORDER BY total_vendido DESC
                LIMIT %s
            """
            return db.execute_query(query, (fecha_inicio, fecha_fin, limite)) or []
        except Exception as e:
            print(f"Error obteniendo productos más vendidos: {e}")
            return []
    
    @staticmethod
    def obtener_ventas_por_categoria(fecha_inicio, fecha_fin):
        """Obtiene ventas agrupadas por categoría"""
        try:
            query = """
                SELECT 
                    COALESCE(c.nombre, 'Sin categoría') as categoria,
                    COUNT(DISTINCT dv.venta_id) as num_ventas,
                    SUM(dv.cantidad) as total_cantidad,
                    SUM(dv.subtotal) as total_ingresos,
                    AVG(dv.precio_unitario) as precio_promedio
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                LEFT JOIN categorias c ON p.categoria_id = c.id
                JOIN ventas v ON dv.venta_id = v.id
                WHERE DATE(v.fecha_venta) BETWEEN %s AND %s
                AND v.estado = 'completada'
                GROUP BY c.id, c.nombre
                ORDER BY total_ingresos DESC
            """
            return db.execute_query(query, (fecha_inicio, fecha_fin)) or []
        except Exception as e:
            print(f"Error obteniendo ventas por categoría: {e}")
            return []
    
    @staticmethod
    def obtener_clientes_frecuentes(fecha_inicio, fecha_fin, limite=10):
        """Obtiene clientes más frecuentes"""
        try:
            query = """
                SELECT 
                    COALESCE(c.nombre, 'Cliente General') as cliente_nombre,
                    COALESCE(c.documento, 'N/A') as cliente_documento,
                    COUNT(v.id) as total_compras,
                    SUM(v.total) as total_gastado,
                    AVG(v.total) as promedio_compra,
                    MAX(v.fecha_venta) as ultima_compra
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                WHERE DATE(v.fecha_venta) BETWEEN %s AND %s
                AND v.estado = 'completada'
                GROUP BY v.cliente_id, c.nombre, c.documento
                ORDER BY total_compras DESC, total_gastado DESC
                LIMIT %s
            """
            return db.execute_query(query, (fecha_inicio, fecha_fin, limite)) or []
        except Exception as e:
            print(f"Error obteniendo clientes frecuentes: {e}")
            return []
    
    @staticmethod
    def obtener_compras_por_periodo(fecha_inicio, fecha_fin):
        """Obtiene compras por período"""
        try:
            query = """
                SELECT 
                    c.numero_compra,
                    c.fecha_compra,
                    p.nombre as proveedor_nombre,
                    u.nombre as usuario_nombre,
                    c.total,
                    c.estado,
                    COUNT(dc.id) as total_items
                FROM compras c
                LEFT JOIN proveedores p ON c.proveedor_id = p.id
                LEFT JOIN usuarios u ON c.usuario_id = u.id
                LEFT JOIN detalle_compras dc ON c.id = dc.compra_id
                WHERE DATE(c.fecha_compra) BETWEEN %s AND %s
                GROUP BY c.id
                ORDER BY c.fecha_compra DESC
            """
            return db.execute_query(query, (fecha_inicio, fecha_fin)) or []
        except Exception as e:
            print(f"Error obteniendo compras por período: {e}")
            return []
    
    @staticmethod
    def obtener_resumen_compras(fecha_inicio, fecha_fin):
        """Obtiene resumen de compras por período"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_compras,
                    SUM(total) as total_gastado,
                    AVG(total) as promedio_compra,
                    COUNT(CASE WHEN estado = 'pendiente' THEN 1 END) as compras_pendientes,
                    COUNT(CASE WHEN estado = 'recibida' THEN 1 END) as compras_recibidas,
                    COUNT(CASE WHEN estado = 'cancelada' THEN 1 END) as compras_canceladas
                FROM compras 
                WHERE DATE(fecha_compra) BETWEEN %s AND %s
            """
            result = db.execute_query(query, (fecha_inicio, fecha_fin))
            return result[0] if result else None
        except Exception as e:
            print(f"Error obteniendo resumen compras: {e}")
            return None
    
    @staticmethod
    def obtener_rentabilidad_productos(fecha_inicio, fecha_fin, limite=20):
        """Calcula rentabilidad por producto"""
        try:
            query = """
                SELECT 
                    p.codigo,
                    p.nombre,
                    c.nombre as categoria,
                    p.precio_compra,
                    AVG(dv.precio_unitario) as precio_venta_promedio,
                    SUM(dv.cantidad) as total_vendido,
                    SUM(dv.subtotal) as ingresos_totales,
                    SUM(dv.cantidad * COALESCE(p.precio_compra, 0)) as costo_total,
                    (SUM(dv.subtotal) - SUM(dv.cantidad * COALESCE(p.precio_compra, 0))) as ganancia_bruta,
                    CASE 
                        WHEN SUM(dv.subtotal) > 0 THEN 
                            ((SUM(dv.subtotal) - SUM(dv.cantidad * COALESCE(p.precio_compra, 0))) / SUM(dv.subtotal)) * 100
                        ELSE 0 
                    END as margen_porcentaje
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                LEFT JOIN categorias c ON p.categoria_id = c.id
                JOIN ventas v ON dv.venta_id = v.id
                WHERE DATE(v.fecha_venta) BETWEEN %s AND %s
                AND v.estado = 'completada'
                AND p.precio_compra IS NOT NULL
                AND p.precio_compra > 0
                GROUP BY p.id
                ORDER BY ganancia_bruta DESC
                LIMIT %s
            """
            return db.execute_query(query, (fecha_inicio, fecha_fin, limite)) or []
        except Exception as e:
            print(f"Error obteniendo rentabilidad productos: {e}")
            return []
    
    @staticmethod
    def obtener_movimientos_stock(fecha_inicio, fecha_fin):
        """Obtiene movimientos de stock (ventas y compras)"""
        try:
            # Movimientos por ventas
            ventas_query = """
                SELECT 
                    'VENTA' as tipo,
                    v.fecha_venta as fecha,
                    v.numero_venta as numero,
                    p.codigo,
                    p.nombre as producto,
                    dv.cantidad as cantidad,
                    'SALIDA' as movimiento,
                    dv.precio_unitario as precio
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                JOIN ventas v ON dv.venta_id = v.id
                WHERE DATE(v.fecha_venta) BETWEEN %s AND %s
                AND v.estado = 'completada'
            """
            
            # Movimientos por compras
            compras_query = """
                SELECT 
                    'COMPRA' as tipo,
                    c.fecha_compra as fecha,
                    c.numero_compra as numero,
                    p.codigo,
                    p.nombre as producto,
                    dc.cantidad as cantidad,
                    'ENTRADA' as movimiento,
                    dc.precio_unitario as precio
                FROM detalle_compras dc
                JOIN productos p ON dc.producto_id = p.id
                JOIN compras c ON dc.compra_id = c.id
                WHERE DATE(c.fecha_compra) BETWEEN %s AND %s
                AND c.estado = 'recibida'
            """
            
            # Unir ambas consultas
            query = f"""
                ({ventas_query})
                UNION ALL
                ({compras_query})
                ORDER BY fecha DESC, tipo
            """
            
            return db.execute_query(query, (fecha_inicio, fecha_fin, fecha_inicio, fecha_fin)) or []
        except Exception as e:
            print(f"Error obteniendo movimientos stock: {e}")
            return []
    
    @staticmethod
    def obtener_estadisticas_generales():
        """Obtiene estadísticas generales del sistema"""
        try:
            query = """
                SELECT 
                    (SELECT COUNT(*) FROM productos WHERE activo = TRUE) as total_productos,
                    (SELECT COUNT(*) FROM categorias WHERE activo = TRUE) as total_categorias,
                    (SELECT COUNT(*) FROM proveedores WHERE activo = TRUE) as total_proveedores,
                    (SELECT COUNT(*) FROM clientes WHERE activo = TRUE) as total_clientes,
                    (SELECT COUNT(*) FROM ventas WHERE estado = 'completada') as total_ventas,
                    (SELECT COUNT(*) FROM compras) as total_compras,
                    (SELECT SUM(total) FROM ventas WHERE estado = 'completada') as ingresos_totales,
                    (SELECT SUM(total) FROM compras WHERE estado = 'recibida') as gastos_totales
            """
            result = db.execute_query(query)
            return result[0] if result else None
        except Exception as e:
            print(f"Error obteniendo estadísticas generales: {e}")
            return None