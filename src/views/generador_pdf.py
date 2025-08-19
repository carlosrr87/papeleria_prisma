# src/views/generador_pdf.py
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class GeneradorPDF:
    def __init__(self):
        self.reportes_dir = "reportes"
        os.makedirs(self.reportes_dir, exist_ok=True)
        
        # Estilos
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        self.styles.add(ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_LEFT
        ))
    
    def _crear_encabezado(self, canvas, doc):
        """Crea el encabezado estándar"""
        canvas.saveState()
        
        # Logo/Título de la empresa
        canvas.setFont('Helvetica-Bold', 16)
        canvas.drawString(72, A4[1] - 50, "PAPELERÍA PRISMA")
        
        canvas.setFont('Helvetica', 10)
        canvas.drawString(72, A4[1] - 65, "Sistema de Gestión Integral")
        
        # Fecha de generación
        canvas.setFont('Helvetica', 8)
        fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")
        canvas.drawRightString(A4[0] - 72, A4[1] - 50, f"Generado: {fecha_generacion}")
        
        # Línea separadora
        canvas.line(72, A4[1] - 75, A4[0] - 72, A4[1] - 75)
        
        canvas.restoreState()
    
    def _crear_pie_pagina(self, canvas, doc):
        """Crea el pie de página estándar"""
        canvas.saveState()
        
        # Número de página
        page_num = canvas.getPageNumber()
        canvas.setFont('Helvetica', 8)
        canvas.drawCentredText(A4[0] / 2, 30, f"Página {page_num}")
        
        # Línea separadora
        canvas.line(72, 50, A4[0] - 72, 50)
        
        canvas.restoreState()
    
    def generar_reporte_inventario(self, resumen, productos):
        """Genera reporte completo de inventario"""
        try:
            filename = os.path.join(self.reportes_dir, f"inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph("REPORTE DE INVENTARIO", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Resumen
            if resumen:
                story.append(Paragraph("RESUMEN EJECUTIVO", self.styles['CustomHeading']))
                
                resumen_data = [
                    ['Métrica', 'Valor'],
                    ['Total de Productos', f"{resumen['total_productos']:,}"],
                    ['Stock Total', f"{resumen['total_stock']:,} unidades"],
                    ['Valor Total Inventario', f"${resumen['valor_total_inventario']:,.2f}"],
                    ['Productos con Stock Bajo', f"{resumen['productos_stock_bajo']:,}"],
                    ['Productos Sin Stock', f"{resumen['productos_sin_stock']:,}"],
                    ['Precio Promedio', f"${resumen['precio_promedio']:,.2f}"]
                ]
                
                resumen_table = Table(resumen_data, colWidths=[3*inch, 2*inch])
                resumen_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(resumen_table)
                story.append(Spacer(1, 30))
            
            # Detalle de productos
            story.append(Paragraph("DETALLE DE PRODUCTOS", self.styles['CustomHeading']))
            
            # Preparar datos para la tabla
            productos_data = [['Código', 'Producto', 'Categoría', 'Stock', 'Precio', 'Valor Stock', 'Estado']]
            
            for producto in productos:
                productos_data.append([
                    producto['codigo'],
                    producto['nombre'][:25] + ('...' if len(producto['nombre']) > 25 else ''),
                    producto['categoria'] or 'N/A',
                    f"{producto['stock_actual']:,}",
                    f"${producto['precio_venta']:,.2f}",
                    f"${producto['valor_stock']:,.2f}",
                    producto['estado_stock']
                ])
            
            productos_table = Table(productos_data, colWidths=[0.8*inch, 2.2*inch, 1*inch, 0.6*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            
            # Estilo de la tabla
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]
            
            # Aplicar colores según estado de stock
            for i, producto in enumerate(productos, 1):
                if producto['estado_stock'] == 'Sin Stock':
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.mistyrose))
                elif producto['estado_stock'] == 'Stock Bajo':
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightyellow))
            
            productos_table.setStyle(TableStyle(table_style))
            story.append(productos_table)
            
            # Construir PDF
            doc.build(story, onFirstPage=self._crear_encabezado, onLaterPages=self._crear_encabezado)
            
            return filename
            
        except Exception as e:
            print(f"Error generando reporte de inventario: {e}")
            return None
    
    def generar_reporte_stock_bajo(self, productos):
        """Genera reporte de productos con stock bajo"""
        try:
            filename = os.path.join(self.reportes_dir, f"stock_bajo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph("REPORTE DE PRODUCTOS CON STOCK BAJO", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Alerta
            story.append(Paragraph("⚠️ ATENCIÓN: Los siguientes productos necesitan reabastecimiento", 
                                 self.styles['CustomHeading']))
            story.append(Spacer(1, 20))
            
            # Tabla de productos
            productos_data = [['Código', 'Producto', 'Categoría', 'Stock Actual', 'Stock Mínimo', 'Diferencia', 'Proveedor']]
            
            for producto in productos:
                diferencia = producto['stock_actual'] - producto['stock_minimo']
                productos_data.append([
                    producto['codigo'],
                    producto['nombre'][:20] + ('...' if len(producto['nombre']) > 20 else ''),
                    producto.get('categoria_nombre', 'N/A') or 'N/A',
                    f"{producto['stock_actual']:,}",
                    f"{producto['stock_minimo']:,}",
                    f"{diferencia:,}",
                    producto.get('proveedor_nombre', 'Sin proveedor') or 'Sin proveedor'
                ])
            
            productos_table = Table(productos_data, colWidths=[0.8*inch, 2*inch, 1*inch, 0.7*inch, 0.7*inch, 0.7*inch, 1.1*inch])
            productos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            story.append(productos_table)
            
            # Recomendaciones
            story.append(Spacer(1, 30))
            story.append(Paragraph("RECOMENDACIONES", self.styles['CustomHeading']))
            recomendaciones = """
            • Generar órdenes de compra para los productos listados
            • Contactar a los proveedores para verificar disponibilidad
            • Revisar políticas de stock mínimo
            • Considerar productos alternativos si hay demoras
            """
            story.append(Paragraph(recomendaciones, self.styles['Normal']))
            
            doc.build(story, onFirstPage=self._crear_encabezado, onLaterPages=self._crear_encabezado)
            return filename
            
        except Exception as e:
            print(f"Error generando reporte de stock bajo: {e}")
            return None
    
    def generar_reporte_ventas(self, resumen, ventas, fecha_inicio, fecha_fin):
        """Genera reporte de ventas por período"""
        try:
            filename = os.path.join(self.reportes_dir, f"ventas_{fecha_inicio}_{fecha_fin}.pdf")
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph(f"REPORTE DE VENTAS<br/>{fecha_inicio} al {fecha_fin}", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Resumen
            if resumen:
                story.append(Paragraph("RESUMEN DEL PERÍODO", self.styles['CustomHeading']))
                
                resumen_data = [
                    ['Métrica', 'Valor'],
                    ['Total de Ventas', f"{resumen['total_ventas']:,}"],
                    ['Ventas Completadas', f"{resumen['ventas_completadas']:,}"],
                    ['Ventas Canceladas', f"{resumen['ventas_canceladas']:,}"],
                    ['Ingresos Totales', f"${resumen['total_ingresos']:,.2f}"],
                    ['Ingresos Reales', f"${resumen['ingresos_reales']:,.2f}"],
                    ['Promedio por Venta', f"${resumen['promedio_venta']:,.2f}"]
                ]
                
                resumen_table = Table(resumen_data, colWidths=[3*inch, 2*inch])
                resumen_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(resumen_table)
                story.append(Spacer(1, 30))
            
            # Detalle de ventas
            story.append(Paragraph("DETALLE DE VENTAS", self.styles['CustomHeading']))
            
            ventas_data = [['Número', 'Fecha', 'Cliente', 'Usuario', 'Items', 'Total', 'Estado']]
            
            for venta in ventas:
                fecha_formateada = venta['fecha_venta'].strftime('%d/%m/%Y') if hasattr(venta['fecha_venta'], 'strftime') else str(venta['fecha_venta'])[:10]
                ventas_data.append([
                    venta['numero_venta'],
                    fecha_formateada,
                    venta['cliente_nombre'][:15] + ('...' if len(venta['cliente_nombre']) > 15 else ''),
                    venta['usuario_nombre'],
                    f"{venta['total_items']:,}",
                    f"${venta['total']:,.2f}",
                    venta['estado'].title()
                ])
            
            ventas_table = Table(ventas_data, colWidths=[1*inch, 0.8*inch, 1.5*inch, 1*inch, 0.5*inch, 0.8*inch, 0.7*inch])
            ventas_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            
            story.append(ventas_table)
            
            doc.build(story, onFirstPage=self._crear_encabezado, onLaterPages=self._crear_encabezado)
            return filename
            
        except Exception as e:
            print(f"Error generando reporte de ventas: {e}")
            return None
    
    def generar_reporte_mas_vendidos(self, productos, fecha_inicio, fecha_fin):
        """Genera reporte de productos más vendidos"""
        try:
            filename = os.path.join(self.reportes_dir, f"mas_vendidos_{fecha_inicio}_{fecha_fin}.pdf")
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph(f"TOP PRODUCTOS MÁS VENDIDOS<br/>{fecha_inicio} al {fecha_fin}", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Tabla de productos
            productos_data = [['Pos.', 'Código', 'Producto', 'Categoría', 'Vendido', 'Ingresos', 'Precio Prom.']]
            
            for i, producto in enumerate(productos, 1):
                productos_data.append([
                    f"{i}°",
                    producto['codigo'],
                    producto['nombre'][:20] + ('...' if len(producto['nombre']) > 20 else ''),
                    producto.get('categoria', 'N/A') or 'N/A',
                    f"{producto['total_vendido']:,}",
                    f"${producto['total_ingresos']:,.2f}",
                    f"${producto['precio_promedio']:,.2f}"
                ])
            
            productos_table = Table(productos_data, colWidths=[0.4*inch, 0.8*inch, 2*inch, 1*inch, 0.7*inch, 1*inch, 0.8*inch])
            
            # Colores degradados para el ranking
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.gold),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]
            
            # Colores especiales para top 3
            if len(productos) >= 1:
                table_style.append(('BACKGROUND', (0, 1), (-1, 1), colors.gold))  # 1er lugar
            if len(productos) >= 2:
                table_style.append(('BACKGROUND', (0, 2), (-1, 2), colors.silver))  # 2do lugar
            if len(productos) >= 3:
                table_style.append(('BACKGROUND', (0, 3), (-1, 3), colors.orange))  # 3er lugar
            
            # Resto en color claro
            for i in range(4, len(productos) + 1):
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey))
            
            productos_table.setStyle(TableStyle(table_style))
            story.append(productos_table)
            
            doc.build(story, onFirstPage=self._crear_encabezado, onLaterPages=self._crear_encabezado)
            return filename
            
        except Exception as e:
            print(f"Error generando reporte de productos más vendidos: {e}")
            return None
    
    def generar_reporte_rentabilidad(self, productos, fecha_inicio, fecha_fin):
        """Genera reporte de rentabilidad por producto"""
        try:
            filename = os.path.join(self.reportes_dir, f"rentabilidad_{fecha_inicio}_{fecha_fin}.pdf")
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph(f"ANÁLISIS DE RENTABILIDAD<br/>{fecha_inicio} al {fecha_fin}", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Tabla de rentabilidad
            productos_data = [['Producto', 'Vendido', 'Ingresos', 'Costos', 'Ganancia', 'Margen %']]
            
            for producto in productos:
                productos_data.append([
                    producto['nombre'][:25] + ('...' if len(producto['nombre']) > 25 else ''),
                    f"{producto['total_vendido']:,}",
                    f"${producto['ingresos_totales']:,.2f}",
                    f"${producto['costo_total']:,.2f}",
                    f"${producto['ganancia_bruta']:,.2f}",
                    f"{producto['margen_porcentaje']:.1f}%"
                ])
            
            productos_table = Table(productos_data, colWidths=[2.5*inch, 0.7*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
            productos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            
            story.append(productos_table)
            
            # Interpretación
            story.append(Spacer(1, 20))
            story.append(Paragraph("INTERPRETACIÓN DE MÁRGENES", self.styles['CustomHeading']))
            interpretacion = """
            • Margen > 30%: Excelente rentabilidad (Verde)
            • Margen 15-30%: Rentabilidad aceptable (Naranja)  
            • Margen < 15%: Revisar precios o costos (Rojo)
            """
            story.append(Paragraph(interpretacion, self.styles['Normal']))
            
            doc.build(story, onFirstPage=self._crear_encabezado, onLaterPages=self._crear_encabezado)
            return filename
            
        except Exception as e:
            print(f"Error generando reporte de rentabilidad: {e}")
            return None
    
    def generar_dashboard_ejecutivo(self, stats_generales, resumen_inv, resumen_ventas, 
                                   resumen_compras, top_productos, top_clientes, fecha_inicio, fecha_fin):
        """Genera dashboard ejecutivo completo"""
        try:
            filename = os.path.join(self.reportes_dir, f"dashboard_ejecutivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            # Título principal
            story.append(Paragraph("DASHBOARD EJECUTIVO", self.styles['CustomTitle']))
            story.append(Paragraph(f"Período de análisis: {fecha_inicio} al {fecha_fin}", self.styles['Normal']))
            story.append(Spacer(1, 30))
            
            # Estadísticas generales
            story.append(Paragraph("📊 RESUMEN GENERAL DEL NEGOCIO", self.styles['CustomHeading']))
            
            if stats_generales:
                ganancia_bruta = (stats_generales.get('ingresos_totales', 0) or 0) - (stats_generales.get('gastos_totales', 0) or 0)
                
                general_data = [
                    ['Métrica', 'Valor'],
                    ['Total Productos', f"{stats_generales.get('total_productos', 0):,}"],
                    ['Total Clientes', f"{stats_generales.get('total_clientes', 0):,}"],
                    ['Total Ventas Históricas', f"{stats_generales.get('total_ventas', 0):,}"],
                    ['Ingresos Totales', f"${stats_generales.get('ingresos_totales', 0):,.2f}"],
                    ['Gastos Totales', f"${stats_generales.get('gastos_totales', 0):,.2f}"],
                    ['Ganancia Bruta', f"${ganancia_bruta:,.2f}"]
                ]
                
                general_table = Table(general_data, colWidths=[3*inch, 2*inch])
                general_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightsteelblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(general_table)
                story.append(Spacer(1, 30))
            
            # Resumen de ventas del período
            story.append(Paragraph(f"💰 VENTAS DEL PERÍODO ({fecha_inicio} - {fecha_fin})", self.styles['CustomHeading']))
            
            if resumen_ventas:
                total_ventas = resumen_ventas.get('total_ventas', 0)
                ventas_completadas = resumen_ventas.get('ventas_completadas', 0)
                tasa_exito = (ventas_completadas / total_ventas * 100) if total_ventas > 0 else 0
                
                ventas_data = [
                    ['Métrica', 'Valor'],
                    ['Ventas del Período', f"{total_ventas:,}"],
                    ['Ingresos del Período', f"${resumen_ventas.get('ingresos_reales', 0):,.2f}"],
                    ['Promedio por Venta', f"${resumen_ventas.get('promedio_venta', 0):,.2f}"],
                    ['Tasa de Éxito', f"{tasa_exito:.1f}%"]
                ]
                
                ventas_table = Table(ventas_data, colWidths=[3*inch, 2*inch])
                ventas_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(ventas_table)
                story.append(Spacer(1, 20))
            
            # Top 5 productos más vendidos
            if top_productos:
                story.append(Paragraph("🏆 TOP 5 PRODUCTOS MÁS VENDIDOS", self.styles['CustomHeading']))
                
                top_data = [['Pos.', 'Producto', 'Vendido', 'Ingresos']]
                for i, producto in enumerate(top_productos[:5], 1):
                    top_data.append([
                        f"{i}°",
                        producto['nombre'][:30] + ('...' if len(producto['nombre']) > 30 else ''),
                        f"{producto['total_vendido']:,}",
                        f"${producto['total_ingresos']:,.2f}"
                    ])
                
                top_table = Table(top_data, colWidths=[0.5*inch, 3*inch, 0.8*inch, 1.2*inch])
                top_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.gold),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9)
                ]))
                
                story.append(top_table)
                story.append(Spacer(1, 20))
            
            # Nueva página para inventario
            story.append(PageBreak())
            
            # Resumen de inventario
            story.append(Paragraph("📦 ESTADO DEL INVENTARIO", self.styles['CustomHeading']))
            
            if resumen_inv:
                inv_data = [
                    ['Métrica', 'Valor'],
                    ['Valor Total Inventario', f"${resumen_inv.get('valor_total_inventario', 0):,.2f}"],
                    ['Stock Total', f"{resumen_inv.get('total_stock', 0):,} unidades"],
                    ['Productos con Stock Bajo', f"{resumen_inv.get('productos_stock_bajo', 0):,}"],
                    ['Productos Sin Stock', f"{resumen_inv.get('productos_sin_stock', 0):,}"]
                ]
                
                inv_table = Table(inv_data, colWidths=[3*inch, 2*inch])
                inv_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.peachpuff),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(inv_table)
                story.append(Spacer(1, 30))
            
            # Recomendaciones estratégicas
            story.append(Paragraph("💡 RECOMENDACIONES ESTRATÉGICAS", self.styles['CustomHeading']))
            
            recomendaciones = """
            <b>ACCIONES INMEDIATAS:</b><br/>
            • Reabastecer productos con stock bajo<br/>
            • Analizar productos sin movimiento<br/>
            • Optimizar precios de productos con baja rotación<br/><br/>
            
            <b>ESTRATEGIAS A MEDIANO PLAZO:</b><br/>
            • Enfocar marketing en productos más rentables<br/>
            • Negociar mejores precios con proveedores<br/>
            • Implementar programa de fidelización de clientes<br/><br/>
            
            <b>MÉTRICAS A MONITOREAR:</b><br/>
            • Rotación de inventario<br/>
            • Margen de ganancia por categoría<br/>
            • Satisfacción del cliente
            """
            
            story.append(Paragraph(recomendaciones, self.styles['Normal']))
            
            doc.build(story, onFirstPage=self._crear_encabezado, onLaterPages=self._crear_encabezado)
            return filename
            
        except Exception as e:
            print(f"Error generando dashboard ejecutivo: {e}")
            return None
    
    def generar_reporte_valorizacion(self, resumen, productos):
        """Genera reporte simplificado de valorización"""
        try:
            filename = os.path.join(self.reportes_dir, f"valorizacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph("REPORTE DE VALORIZACIÓN DE INVENTARIO", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Resumen
            if resumen:
                story.append(Paragraph("RESUMEN DE VALORIZACIÓN", self.styles['CustomHeading']))
                
                resumen_data = [
                    ['Métrica', 'Valor'],
                    ['Valor Total del Inventario', f"${resumen.get('valor_total_inventario', 0):,.2f}"],
                    ['Total de Productos', f"{resumen.get('total_productos', 0):,}"],
                    ['Stock Total', f"{resumen.get('total_stock', 0):,} unidades"],
                    ['Precio Promedio', f"${resumen.get('precio_promedio', 0):,.2f}"]
                ]
                
                resumen_table = Table(resumen_data, colWidths=[3*inch, 2*inch])
                resumen_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(resumen_table)
                story.append(Spacer(1, 30))
            
            # Detalle de productos si se proporciona
            if productos:
                story.append(Paragraph("DETALLE POR PRODUCTO", self.styles['CustomHeading']))
                
                productos_data = [['Código', 'Producto', 'Stock', 'Precio Unit.', 'Valor Total']]
                
                for producto in productos[:50]:  # Limitar a 50 productos para el PDF
                    productos_data.append([
                        producto.get('codigo', ''),
                        producto.get('nombre', '')[:30] + ('...' if len(producto.get('nombre', '')) > 30 else ''),
                        f"{producto.get('stock_actual', 0):,}",
                        f"${producto.get('precio_venta', 0):,.2f}",
                        f"${producto.get('valor_stock', 0):,.2f}"
                    ])
                
                productos_table = Table(productos_data, colWidths=[1*inch, 2.5*inch, 0.8*inch, 1*inch, 1.2*inch])
                productos_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8)
                ]))
                
                story.append(productos_table)
            
            doc.build(story, onFirstPage=self._crear_encabezado, onLaterPages=self._crear_encabezado)
            return filename
            
        except Exception as e:
            print(f"Error generando reporte de valorización: {e}")
            return None
    
    def generar_reporte_compras(self, resumen, compras, fecha_inicio, fecha_fin):
        """Genera reporte completo de compras"""
        try:
            filename = os.path.join(self.reportes_dir, f"compras_{fecha_inicio}_{fecha_fin}.pdf")
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph(f"REPORTE DE COMPRAS<br/>{fecha_inicio} al {fecha_fin}", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Resumen
            if resumen:
                story.append(Paragraph("RESUMEN DEL PERÍODO", self.styles['CustomHeading']))
                
                resumen_data = [
                    ['Métrica', 'Valor'],
                    ['Total de Compras', f"{resumen.get('total_compras', 0):,}"],
                    ['Total Gastado', f"${resumen.get('total_gastado', 0):,.2f}"],
                    ['Promedio por Compra', f"${resumen.get('promedio_compra', 0):,.2f}"],
                    ['Productos Comprados', f"{resumen.get('productos_comprados', 0):,}"],
                    ['Proveedores Utilizados', f"{resumen.get('proveedores_utilizados', 0):,}"]
                ]
                
                resumen_table = Table(resumen_data, colWidths=[3*inch, 2*inch])
                resumen_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(resumen_table)
                story.append(Spacer(1, 30))
            
            # Detalle de compras
            if compras:
                story.append(Paragraph("DETALLE DE COMPRAS", self.styles['CustomHeading']))
                
                compras_data = [['Fecha', 'Proveedor', 'Productos', 'Total', 'Usuario']]
                
                for compra in compras:
                    fecha_formateada = compra['fecha'].strftime('%d/%m/%Y') if hasattr(compra['fecha'], 'strftime') else str(compra['fecha'])[:10]
                    compras_data.append([
                        fecha_formateada,
                        compra.get('proveedor', 'N/A')[:20] + ('...' if len(compra.get('proveedor', '')) > 20 else ''),
                        f"{compra.get('total_productos', 0):,}",
                        f"${compra.get('total', 0):,.2f}",
                        compra.get('usuario', 'N/A')
                    ])
                
                compras_table = Table(compras_data, colWidths=[1*inch, 2*inch, 1*inch, 1*inch, 1.5*inch])
                compras_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8)
                ]))
                
                story.append(compras_table)
            
            doc.build(story, onFirstPage=self._crear_encabezado, onLaterPages=self._crear_encabezado)
            return filename
            
        except Exception as e:
            print(f"Error generando reporte de compras: {e}")
            return None
    
    def generar_reporte_clientes(self, clientes, fecha_inicio, fecha_fin):
        """Genera reporte de clientes frecuentes"""
        try:
            filename = os.path.join(self.reportes_dir, f"clientes_{fecha_inicio}_{fecha_fin}.pdf")
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph(f"CLIENTES FRECUENTES<br/>{fecha_inicio} al {fecha_fin}", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Tabla de clientes
            if clientes:
                clientes_data = [['Pos.', 'Cliente', 'Compras', 'Total Gastado', 'Promedio', 'Última Compra']]
                
                for i, cliente in enumerate(clientes, 1):
                    ultima_compra = cliente.get('ultima_compra', '')
                    if hasattr(ultima_compra, 'strftime'):
                        ultima_compra = ultima_compra.strftime('%d/%m/%Y')
                    elif ultima_compra:
                        ultima_compra = str(ultima_compra)[:10]
                    
                    clientes_data.append([
                        f"{i}°",
                        cliente.get('nombre', 'N/A')[:25] + ('...' if len(cliente.get('nombre', '')) > 25 else ''),
                        f"{cliente.get('total_compras', 0):,}",
                        f"${cliente.get('total_gastado', 0):,.2f}",
                        f"${cliente.get('promedio_compra', 0):,.2f}",
                        ultima_compra
                    ])
                
                clientes_table = Table(clientes_data, colWidths=[0.4*inch, 2.2*inch, 0.8*inch, 1*inch, 1*inch, 1*inch])
                clientes_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightcyan),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8)
                ]))
                
                story.append(clientes_table)
            
            doc.build(story, onFirstPage=self._crear_encabezado, onLaterPages=self._crear_encabezado)
            return filename
            
        except Exception as e:
            print(f"Error generando reporte de clientes: {e}")
            return None
    
    def generar_reporte_categorias(self, categorias, fecha_inicio, fecha_fin):
        """Genera reporte de ventas por categorías"""
        try:
            filename = os.path.join(self.reportes_dir, f"categorias_{fecha_inicio}_{fecha_fin}.pdf")
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph(f"VENTAS POR CATEGORÍA<br/>{fecha_inicio} al {fecha_fin}", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Tabla de categorías
            if categorias:
                categorias_data = [['Categoría', 'Productos Vendidos', 'Unidades', 'Ingresos', '% del Total']]
                
                for categoria in categorias:
                    categorias_data.append([
                        categoria.get('nombre', 'Sin Categoría'),
                        f"{categoria.get('productos_vendidos', 0):,}",
                        f"{categoria.get('unidades_vendidas', 0):,}",
                        f"${categoria.get('ingresos', 0):,.2f}",
                        f"{categoria.get('porcentaje', 0):.1f}%"
                    ])
                
                categorias_table = Table(categorias_data, colWidths=[2*inch, 1.2*inch, 1*inch, 1.2*inch, 1*inch])
                categorias_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9)
                ]))
                
                story.append(categorias_table)
            
            doc.build(story, onFirstPage=self._crear_encabezado, onLaterPages=self._crear_encabezado)
            return filename
            
        except Exception as e:
            print(f"Error generando reporte de categorías: {e}")
            return None
    
    def generar_reporte_movimientos(self, movimientos, fecha_inicio, fecha_fin):
        """Genera reporte de movimientos de stock"""
        try:
            filename = os.path.join(self.reportes_dir, f"movimientos_{fecha_inicio}_{fecha_fin}.pdf")
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph(f"MOVIMIENTOS DE STOCK<br/>{fecha_inicio} al {fecha_fin}", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Tabla de movimientos
            if movimientos:
                movimientos_data = [['Fecha', 'Producto', 'Tipo', 'Cantidad', 'Stock Anterior', 'Stock Nuevo', 'Usuario']]
                
                for mov in movimientos:
                    fecha_formateada = mov['fecha'].strftime('%d/%m/%Y') if hasattr(mov['fecha'], 'strftime') else str(mov['fecha'])[:10]
                    
                    tipo_color = 'green' if mov.get('tipo', '') == 'entrada' else 'red'
                    
                    movimientos_data.append([
                        fecha_formateada,
                        mov.get('producto', 'N/A')[:20] + ('...' if len(mov.get('producto', '')) > 20 else ''),
                        mov.get('tipo', 'N/A').title(),
                        f"{mov.get('cantidad', 0):,}",
                        f"{mov.get('stock_anterior', 0):,}",
                        f"{mov.get('stock_nuevo', 0):,}",
                        mov.get('usuario', 'N/A')
                    ])
                
                movimientos_table = Table(movimientos_data, colWidths=[0.8*inch, 1.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch])
                movimientos_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.peachpuff),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8)
                ]))
                
                story.append(movimientos_table)
            
            doc.build(story, onFirstPage=self._crear_encabezado, onLaterPages=self._crear_encabezado)
            return filename
            
        except Exception as e:
            print(f"Error generando reporte de movimientos: {e}")
            return None