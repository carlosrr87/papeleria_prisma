# src/utils/database.py
import mysql.connector
from mysql.connector import Error
import json
import os

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.config_file = "config.json"
        self.load_config()
    
    def load_config(self):
        """Carga la configuración de la base de datos"""
        default_config = {
            "host": "localhost",
            "port": 3306,
            "database": "papeleria_prisma",
            "user": "root",
            "password": ""
        }
        
        try:
            # Intentar cargar desde archivo de configuración
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self.config = config_data.get('database', default_config)
            else:
                # Crear archivo de configuración por defecto
                config_data = {'database': default_config}
                with open(self.config_file, 'w') as f:
                    json.dump(config_data, f, indent=4)
                self.config = default_config
                print(f"Archivo de configuración creado: {self.config_file}")
                
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            self.config = default_config
    
    def connect(self):
        """Establece conexión con la base de datos"""
        try:
            if self.connection and self.connection.is_connected():
                return True
                
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=True
            )
            
            if self.connection.is_connected():
                print(f"✅ Conectado a MySQL: {self.config['database']}")
                return True
            else:
                print("❌ No se pudo establecer la conexión")
                return False
                
        except Error as e:
            print(f"❌ Error conectando a MySQL: {e}")
            self.connection = None
            return False
    
    def disconnect(self):
        """Cierra la conexión con la base de datos"""
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("🔌 Conexión MySQL cerrada")
        except Error as e:
            print(f"Error cerrando conexión: {e}")
    
    def execute_query(self, query, params=None):
        """
        Ejecuta una consulta SQL y retorna los resultados
        
        Args:
            query (str): La consulta SQL a ejecutar
            params (tuple, optional): Parámetros para la consulta
            
        Returns:
            list: Lista de diccionarios con los resultados (para SELECT)
            int: Número de filas afectadas (para INSERT, UPDATE, DELETE)
            None: En caso de error
        """
        try:
            # Asegurar conexión
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
            
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            
            # Ejecutar query
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Determinar tipo de operación
            query_type = query.strip().upper().split()[0]
            
            if query_type == 'SELECT' or query_type == 'SHOW' or query_type == 'DESCRIBE':
                # Para consultas SELECT, retornar todos los resultados
                results = cursor.fetchall()
                cursor.close()
                return results
            
            elif query_type in ['INSERT', 'UPDATE', 'DELETE']:
                # Para operaciones de modificación, retornar número de filas afectadas
                affected_rows = cursor.rowcount
                
                # Para INSERT, también retornar el ID insertado si existe
                if query_type == 'INSERT' and cursor.lastrowid:
                    cursor.close()
                    return {
                        'affected_rows': affected_rows,
                        'last_insert_id': cursor.lastrowid
                    }
                
                cursor.close()
                return affected_rows
            
            else:
                # Para otros tipos de consulta
                cursor.close()
                return True
                
        except Error as e:
            print(f"❌ Error ejecutando query: {e}")
            print(f"Query: {query}")
            if params:
                print(f"Params: {params}")
            return None
        
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return None
    
    def execute_many(self, query, data_list):
        """
        Ejecuta una consulta múltiples veces con diferentes parámetros
        
        Args:
            query (str): La consulta SQL a ejecutar
            data_list (list): Lista de tuplas con los parámetros
            
        Returns:
            int: Número total de filas afectadas
            None: En caso de error
        """
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
            
            cursor = self.connection.cursor()
            cursor.executemany(query, data_list)
            
            affected_rows = cursor.rowcount
            cursor.close()
            
            return affected_rows
            
        except Error as e:
            print(f"❌ Error ejecutando query múltiple: {e}")
            return None
    
    def get_table_info(self, table_name):
        """
        Obtiene información sobre una tabla
        
        Args:
            table_name (str): Nombre de la tabla
            
        Returns:
            dict: Información de la tabla
        """
        try:
            info = {}
            
            # Verificar si la tabla existe
            query_exists = "SHOW TABLES LIKE %s"
            exists = self.execute_query(query_exists, (table_name,))
            info['exists'] = bool(exists)
            
            if exists:
                # Obtener estructura
                query_structure = f"DESCRIBE {table_name}"
                structure = self.execute_query(query_structure)
                info['structure'] = structure
                
                # Obtener conteo de registros
                query_count = f"SELECT COUNT(*) as total FROM {table_name}"
                count_result = self.execute_query(query_count)
                info['record_count'] = count_result[0]['total'] if count_result else 0
            
            return info
            
        except Exception as e:
            print(f"❌ Error obteniendo info de tabla {table_name}: {e}")
            return {'exists': False, 'error': str(e)}
    
    def test_connection(self):
        """
        Prueba la conexión y retorna información del estado
        
        Returns:
            dict: Estado de la conexión y información de la BD
        """
        try:
            # Intentar conectar
            if not self.connect():
                return {
                    'connected': False,
                    'error': 'No se pudo establecer conexión'
                }
            
            # Obtener información de la BD
            query_version = "SELECT VERSION() as version"
            version_result = self.execute_query(query_version)
            
            query_database = "SELECT DATABASE() as current_db"
            db_result = self.execute_query(query_database)
            
            query_tables = "SHOW TABLES"
            tables_result = self.execute_query(query_tables)
            
            return {
                'connected': True,
                'mysql_version': version_result[0]['version'] if version_result else 'Unknown',
                'current_database': db_result[0]['current_db'] if db_result else 'Unknown',
                'tables_count': len(tables_result) if tables_result else 0,
                'tables': [list(table.values())[0] for table in tables_result] if tables_result else [],
                'config': self.config
            }
            
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }

# Crear instancia global
db = DatabaseConnection()

# Funciones de conveniencia para compatibilidad
def get_connection():
    """Retorna la conexión actual"""
    return db.connection

def execute_query(query, params=None):
    """Función de conveniencia para ejecutar queries"""
    return db.execute_query(query, params)

def connect_db():
    """Función de conveniencia para conectar"""
    return db.connect()

def disconnect_db():
    """Función de conveniencia para desconectar"""
    return db.disconnect()

# Función de prueba
def test_database():
    """Función para probar la base de datos"""
    print("🔍 Probando conexión de base de datos...")
    
    # Test de conexión
    connection_info = db.test_connection()
    
    if connection_info['connected']:
        print("✅ Conexión exitosa!")
        print(f"📊 MySQL Version: {connection_info['mysql_version']}")
        print(f"🗃️ Base de datos: {connection_info['current_database']}")
        print(f"📋 Tablas encontradas: {connection_info['tables_count']}")
        
        if connection_info['tables']:
            print("📝 Tablas disponibles:")
            for table in connection_info['tables']:
                print(f"  - {table}")
        
        # Test específico de tabla clientes
        print("\n🔍 Verificando tabla 'clientes'...")
        clientes_info = db.get_table_info('clientes')
        
        if clientes_info['exists']:
            print(f"✅ Tabla 'clientes' existe con {clientes_info['record_count']} registros")
            
            # Mostrar algunos registros de muestra
            sample_query = "SELECT id, nombre, telefono, email FROM clientes LIMIT 3"
            sample_data = db.execute_query(sample_query)
            
            if sample_data:
                print("📋 Registros de muestra:")
                for cliente in sample_data:
                    print(f"  - ID: {cliente['id']}, Nombre: {cliente['nombre']}")
            else:
                print("⚠️ No hay datos en la tabla clientes")
        else:
            print("❌ Tabla 'clientes' no existe")
            
    else:
        print(f"❌ Error de conexión: {connection_info['error']}")
        print("🔧 Verifique la configuración en config.json")
    
    return connection_info['connected']

if __name__ == "__main__":
    test_database()