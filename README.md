<<<<<<< HEAD
# 📊 Papelería PRISMA - Sistema de Gestión

Sistema completo de gestión para papelerías desarrollado en Python con interfaz gráfica Tkinter y base de datos MySQL.

## 🚀 Características

### ✅ Módulos Implementados
- **👥 Gestión de Clientes** - CRUD completo, búsqueda, historial
- **📦 Gestión de Productos** - Inventario, categorías, stock
- **🛒 Sistema de Ventas** - Procesamiento de ventas, facturación
- **🛍️ Gestión de Compras** - Compras a proveedores, stock
- **📊 Reportes PDF** - Inventario, ventas, clientes, dashboard ejecutivo
- **🔐 Sistema de Login** - Autenticación de usuarios
- **📈 Dashboard** - Estadísticas en tiempo real

### 🛠️ Tecnologías
- **Lenguaje:** Python 3.8+
- **GUI:** Tkinter (nativo)
- **Base de datos:** MySQL 8.0+
- **PDFs:** ReportLab
- **Conexión DB:** mysql-connector-python

## 📋 Requisitos

### Software necesario:
- Python 3.8 o superior
- MySQL Server 8.0+
- MySQL Workbench (recomendado)

### Dependencias Python:
```bash
mysql-connector-python>=8.0.0
reportlab>=3.6.0
```

## 🔧 Instalación

### 1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd papeleria_prisma
```

### 2. Crear entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos:
1. Crear base de datos `papeleria_prisma` en MySQL
2. Ejecutar scripts SQL de la carpeta `sql/`
3. Configurar credenciales en `config.json`

### 5. Ejecutar aplicación:
```bash
cd src
python main.py
```

## 📁 Estructura del Proyecto

```
papeleria_prisma/
├── src/
│   ├── main.py              # Aplicación principal
│   ├── utils/
│   │   └── database.py      # Conexión a base de datos
│   └── views/
│       ├── clientes_view.py # Módulo de clientes
│       ├── productos_view.py # Módulo de productos
│       ├── ventas_view.py   # Módulo de ventas
│       ├── compras_simple.py # Módulo de compras
│       ├── reportes_view.py # Centro de reportes
│       └── generador_pdf.py # Generador de PDFs
├── sql/
│   ├── create_tables.sql    # Scripts de creación
│   └── sample_data.sql      # Datos de prueba
├── reportes/                # PDFs generados
├── venv/                    # Entorno virtual
├── config.json             # Configuración (no incluido)
├── requirements.txt        # Dependencias
└── README.md
```

## 🔑 Configuración

Crear archivo `config.json` en la raíz:
```json
{
    "database": {
        "host": "localhost",
        "port": 3306,
        "database": "papeleria_prisma",
        "user": "root",
        "password": "tu_password"
    }
}
```

## 👥 Uso

### Login por defecto:
- Usuario: `admin`
- Contraseña: `admin123`

### Módulos principales:
1. **Dashboard** - Vista general del negocio
2. **Clientes** - Gestión completa de clientes
3. **Productos** - Inventario y stock
4. **Ventas** - Procesamiento de ventas
5. **Compras** - Gestión de compras
6. **Reportes** - Generación de PDFs profesionales

## 📊 Reportes Disponibles

- **Inventario:** Stock, valorización, productos con stock bajo
- **Ventas:** Por período, productos más vendidos, rentabilidad
- **Clientes:** Frecuentes, historial de compras
- **Ejecutivos:** Dashboard completo, KPIs del negocio

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Changelog

### v1.0.0 (2024-12-XX)
- ✅ Sistema de login funcional
- ✅ Módulo de clientes completo
- ✅ Módulo de productos
- ✅ Sistema de ventas
- ✅ Gestión de compras básica
- ✅ Centro de reportes PDF
- ✅ Dashboard con estadísticas

## 🐛 Problemas conocidos

- [ ] Integración pendiente entre clientes y ventas
- [ ] Módulo de usuarios en desarrollo
- [ ] Configuración de empresa pendiente

## 📞 Soporte

Para reportar bugs o solicitar funcionalidades, crear un issue en el repositorio.

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver `LICENSE` para más detalles.

---

**Desarrollado para Papelería PRISMA** 🏪
=======
"# biblioteca" 
>>>>>>> c23c1d48ba5d3739bbcaba19398c81ca3f967375
