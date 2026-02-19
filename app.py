import streamlit as st
import sqlite3
import pandas as pd
import folium
from streamlit_folium import st_folium
from utils import endereco_para_latlon

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

def inserir_monitoramento(ponto, ph, od, qualidade):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO monitoramento (ponto, ph, od, qualidade_agua)
        VALUES (?, ?, ?, ?)
    ''', (ponto, float(ph), float(od), qualidade))
    conn.commit()
    conn.close()

def get_monitoramentos():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM monitoramento", conn)
    conn.close()
    return df

def apagar_registro(registro_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM monitoramento WHERE id = ?', (registro_id,))
    conn.commit()
    conn.close()

# --- Inicialização do banco ---
inicializar_banco()

# --- Interface ---
st.title('Projeto Água Viva - Monitoramento')
menu = st.sidebar.selectbox('Menu', ['Cadastro', 'Ver Mapa', 'Gerenciar Registros'])

if menu == 'Cadastro':
    st.header('Cadastro de Monitoramento de Água')
    with st.form('formulario'):
        ponto = st.text_input("Local (endereço completo)")
        ph = st.text_input("pH", max_chars=10)
        od = st.text_input("OD (mg/L)", max_chars=10)
        qualidade = st.selectbox("Qualidade da Água", ['Boa', 'Regular', 'Péssima'])
        enviado = st.form_submit_button("Salvar")

    if enviado:
        if not ponto or not ph or not od:
            st.error("Preencha todos os campos!")
        else:
            try:
                inserir_monitoramento(ponto, ph, od, qualidade)
                st.success('SUCESSO! Cadastro realizado.')
            except Exception as e:
                st.error(f"Erro ao salvar: {str(e)}")

elif menu == 'Ver Mapa':
    st.header('Mapa dos Pontos Cadastrados')
    df_cad = get_monitoramentos()
    if df_cad.empty:
        st.warning('Nenhum ponto cadastrado ainda.')
    else:
        # Geocoding dos endereços
        lat_list, lon_list, cor_list = [], [], []
        for idx, row in df_cad.iterrows():
            try:
                lat, lon = endereco_para_latlon(row['ponto'])
                lat_list.append(lat)
                lon_list.append(lon)
                if row['qualidade_agua'] == 'Boa':
                    cor_list.append('green')
                elif row['qualidade_agua'] == 'Regular':
                    cor_list.append('orange')
                else:
                    cor_list.append('red')
            except Exception:
                lat_list.append(None)
                lon_list.append(None)
                cor_list.append('gray')

        df_cad['lat'] = lat_list
        df_cad['lon'] = lon_list
        df_cad['cor'] = cor_list

        mapa = folium.Map(location=[-14.2, -51.9], zoom_start=4)
        for _, row in df_cad.dropna(subset=['lat', 'lon']).iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=f"{row['ponto']} ({row['qualidade_agua']})",
                icon=folium.Icon(color=row['cor'], icon="tint"),
            ).add_to(mapa)
        st_folium(mapa, width=700, height=500)

    st.subheader('Tabela dos pontos cadastrados')
    st.dataframe(df_cad[['id', 'ponto', 'ph', 'od', 'qualidade_agua', 'lat', 'lon']])

elif menu == 'Gerenciar Registros':
    st.header('Gerenciamento dos Registros')
    df = get_monitoramentos()
    if df.empty:
        st.warning('Nenhum ponto cadastrado ainda.')
    else:
        st.dataframe(df[['id', 'ponto', 'ph', 'od', 'qualidade_agua']])
        with st.form('apagar_form'):
            registro_id = st.text_input("Digite o ID do registro que deseja apagar")
            apagar = st.form_submit_button("Apagar")
            if apagar:
                if not registro_id.isdigit():
                    st.error("Por favor, digite um ID válido (número inteiro).")
                else:
                    registro_id_int = int(registro_id)
                    # Verifica se esse ID existe
                    if registro_id_int in df['id'].values:
                        apagar_registro(registro_id_int)
                        st.success(f"Registro de ID {registro_id_int} apagado com sucesso!")
                        st.rerun()
                    else:
                        st.error("ID não encontrado na lista de registros.")