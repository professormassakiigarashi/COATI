import sqlite3
import pandas as pd

DB_NAME = "projeto_agua_viva.db"

def inicializar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitoramento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ponto TEXT,
            ph REAL,
            od REAL,
            qualidade_agua TEXT
        )
    ''')
    conn.commit()
    conn.close()

def salvar_registro(ponto, ph, od, qualidade):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO monitoramento (ponto, ph, od, qualidade_agua)
        VALUES (?, ?, ?, ?)
    ''', (ponto, float(ph), float(od), qualidade))
    conn.commit()
    conn.close()

def carregar_registros():
    conn = sqlite3.connect(DB_NAME)
    df = None
    try:
        df = pd.read_sql_query("SELECT * FROM monitoramento", conn)
    except Exception as e:
        print(f"Erro ao carregar registros: {e}")
        df = None
    conn.close()
    return df

def apagar_registro(registro_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM monitoramento WHERE id = ?
    ''', (registro_id,))
    conn.commit()
    conn.close()