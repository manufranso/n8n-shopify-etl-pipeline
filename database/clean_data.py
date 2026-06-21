import re
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from database.connection import get_connection

def clean_html_tags(text: str) -> str:
    """Elimina etiquetas HTML simples que puedan venir en la descripción original."""
    if not text or pd.isna(text):
        return ""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', str(text)).strip()

def detect_outliers_iqr(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Detecta outliers usando el método estadístico de Rangos Intercuartílicos (IQR)."""
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return df[(df[column] < lower_bound) | (df[column] > upper_bound)]

def clean_data_pipeline():
    conn = get_connection()
    try:
        # 1. Extraer los datos actuales
        print("[-] Obteniendo datos de la tabla 'productos'...")
        df_original = pd.read_sql("SELECT * FROM productos", conn)
        
        if df_original.empty:
            print("[!] La tabla 'productos' está vacía. Fin de la ejecución.")
            return

        print(f"[*] Registros cargados: {len(df_original)}")
        
        # Copia para realizar transformaciones
        df = df_original.copy()
        
        # 2. Limpieza básica de tipos y nulos
        df['current_price'] = pd.to_numeric(df['current_price'], errors='coerce').fillna(0.0)
        df['original_price'] = pd.to_numeric(df['original_price'], errors='coerce')
        
        # 3. Limpieza de Texto (Text Standardization)
        df['title'] = df['title'].fillna("Producto Sin Nombre").astype(str).str.strip()
        df['title'] = df['title'].str.replace(r'\s+', ' ', regex=True)
        df['description'] = df['description'].apply(clean_html_tags)
        
        # 4. Reglas de Negocio de Precios y Descuentos
        # Precio actual no puede ser menor a cero
        df['current_price'] = df['current_price'].clip(lower=0.0)
        
        # Si el precio original es nulo o menor al precio actual, se iguala al actual
        df['original_price'] = np.where(
            df['original_price'].isna() | (df['original_price'] < df['current_price']),
            df['current_price'],
            df['original_price']
        )
        
        # Recalcular porcentaje de descuento consistentemente
        df['discount_percentage'] = np.where(
            df['original_price'] > 0,
            np.round(((df['original_price'] - df['current_price']) / df['original_price']) * 100, 2),
            0.0
        )
        
        # Asegurar consistencia en stock_status (Disponible / Agotado)
        df['stock_status'] = df['stock_status'].fillna('Agotado').astype(str).str.strip().str.capitalize()
        df['stock_status'] = np.where(df['stock_status'] == 'Disponible', 'Disponible', 'Agotado')
        
        # 5. Detección Analítica de Outliers (Para reportar al negocio)
        outliers = detect_outliers_iqr(df, 'current_price')
        if not outliers.empty:
            print(f"\n[ALERTA DE NEGOCIO] Se han identificado {len(outliers)} productos con precios atípicos (Outliers estadísticos por IQR):")
            print(outliers[['external_id', 'title', 'current_price']].to_string(index=False))
            print("-" * 80)
        
        # 6. Identificar qué filas realmente han cambiado para evitar updates innecesarios
        # Para comparar de forma segura, llenamos nulos temporales en strings
        cols_to_compare = ['title', 'current_price', 'original_price', 'discount_percentage', 'stock_status', 'description']
        
        changed_mask = False
        for col in cols_to_compare:
            orig_col = df_original[col].fillna('') if df_original[col].dtype == object else df_original[col].fillna(0.0)
            new_col = df[col].fillna('') if df[col].dtype == object else df[col].fillna(0.0)
            changed_mask = changed_mask | (orig_col != new_col)
            
        df_to_update = df[changed_mask]
        
        # 7. Persistencia de cambios en PostgreSQL
        if not df_to_update.empty:
            print(f"[-] Registros modificados detectados: {len(df_to_update)} de {len(df)}")
            
            # Ejecutar el update en lote usando una transacción
            update_query = """
                UPDATE productos 
                SET 
                    title = %s,
                    current_price = %s,
                    original_price = %s,
                    discount_percentage = %s,
                    stock_status = %s,
                    description = %s,
                    last_scraped_at = CURRENT_TIMESTAMP
                WHERE external_id = %s;
            """
            
            # Preparar los parámetros en el orden correcto
            update_data = [
                (
                    row['title'],
                    float(row['current_price']),
                    float(row['original_price']),
                    float(row['discount_percentage']),
                    row['stock_status'],
                    row['description'],
                    str(row['external_id'])
                )
                for _, row in df_to_update.iterrows()
            ]
            
            with conn.cursor() as cur:
                # Ejecutar actualización por lotes
                cur.executemany(update_query, update_data)
                conn.commit()
                print(f"[+] Éxito: {len(df_to_update)} productos actualizados y corregidos en PostgreSQL.")
        else:
            print("[+] Todos los datos de la base de datos se encuentran limpios y consistentes.")
            
    except Exception as e:
        conn.rollback()
        print(f"[!] Error durante el proceso de limpieza: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    clean_data_pipeline()
