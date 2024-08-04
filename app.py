import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import base64
import os
import requests
from bs4 import BeautifulSoup

# Configuración del tema de Streamlit
st.set_page_config(page_title="Análisis de Mercados de Metales", layout="centered", initial_sidebar_state="collapsed")

# Mostrar el logo de la empresa centrado y con el tamaño original
logo_path = 'logo/logo.webp'
try:
    with open(logo_path, "rb") as image_file:
        logo_bytes = image_file.read()
    logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")

    st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center;">
            <img src="data:image/webp;base64,{logo_base64}">
        </div>
    """, unsafe_allow_html=True)
except FileNotFoundError:
    st.error("No se encontró el logo en la ruta especificada.")

# Título de la aplicación
st.markdown("# Análisis de Mercados de Metales")

# Monitoreo del precio del níquel en tiempo real desde Markets Insider
st.write("Monitoreando el precio del níquel en tiempo real...")
url_nickel = 'https://markets.businessinsider.com/commodities/nickel-price'

def get_nickel_price(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        price = soup.find('span', {'class': 'price-section__current-value'}).text.strip()
        return float(price.replace(',', ''))  # Convertir a float para cálculos
    except Exception as e:
        return f"Error: {e}"

precio_niquel_usd = get_nickel_price(url_nickel)
tipo_cambio = 18.5  # Ajusta según el tipo de cambio actual
precio_niquel_mxn = precio_niquel_usd * tipo_cambio

# Crear dos columnas para los valores del níquel
col1, col2 = st.columns(2)

# Mostrar los precios en USD y MXN, centrados y en negrita
col1.markdown(f"""
    <div style="text-align: center;">
        <span style="font-size: 22px; font-weight: bold; color: green;">{precio_niquel_usd:,.2f} USD/MT</span>
    </div>
    """, unsafe_allow_html=True)

col2.markdown(f"""
    <div style="text-align: center;">
        <span style="font-size: 22px; font-weight: bold; color: green;">{precio_niquel_mxn:,.2f} MXN/MT</span>
    </div>
    """, unsafe_allow_html=True)

# Resto de la interfaz de usuario
st.write("### Análisis de otros metales")

# Selección de metal
metal = st.selectbox("Selecciona el metal", ["Oro", "Plata", "Cobre"])

# Crear dos columnas para fecha y hora de inicio y fin
col1, col2 = st.columns(2)

with col1:
    fecha_inicio = st.date_input("Fecha de inicio", pd.to_datetime("2021-01-01"))
    hora_inicio = st.time_input("Hora de inicio", datetime.strptime("00:00", "%H:%M").time())

with col2:
    fecha_fin = st.date_input("Fecha de fin", pd.to_datetime("2023-01-01"))
    hora_fin = st.time_input("Hora de fin", datetime.strptime("23:59", "%H:%M").time())

# Combinar fecha y hora para las consultas
fecha_inicio = datetime.combine(fecha_inicio, hora_inicio)
fecha_fin = datetime.combine(fecha_fin, hora_fin)

# Mapeo de metales a sus símbolos en Yahoo Finance
simbolos = {
    "Oro": "GC=F",
    "Plata": "SI=F",
    "Cobre": "HG=F"
}

# Botón para realizar el análisis
if st.button("Analizar"):
    simbolo = simbolos[metal]
    tipo_cambio = 18.5  # Ajusta según el tipo de cambio actual

    st.write(f"Descargando datos para {metal} desde {fecha_inicio} hasta {fecha_fin}...")
    data = yf.download(simbolo, start=fecha_inicio, end=fecha_fin)
    
    if data.empty:
        st.write("No se encontraron datos para las fechas seleccionadas.")
    else:
        data['% Change'] = data['Close'].pct_change() * 100
        data.to_csv(f'datos_{metal.lower()}.csv', encoding='utf-8', index=True)
        st.write(f"Datos guardados en 'datos_{metal.lower()}.csv'.")

        st.dataframe(data)

        # Mostrar el gráfico en USD
        plt.figure(figsize=(10, 5))
        plt.plot(data.index, data['Close'], label=f"Precio de cierre de {metal} en USD")
        plt.title(f"Tendencia de los Precios de {metal} en USD")
        plt.xlabel('Fecha')
        plt.ylabel('Precio de Cierre (USD)')
        plt.grid(True)
        st.pyplot(plt)
    
        # Guardar el gráfico como imagen en USD
        grafico_usd_filename = f'tendencia_precios_{metal.lower()}_usd.png'
        plt.savefig(grafico_usd_filename)
        
        # Botón de descarga para gráfico en USD
        with open(grafico_usd_filename, "rb") as file:
            st.download_button(label="Descargar gráfico en USD", data=file, file_name=grafico_usd_filename, mime="image/png")
        
        # Conversión a Pesos Mexicanos
        data['Close_MXN'] = data['Close'] * tipo_cambio
        
        # Mostrar el gráfico en Pesos Mexicanos
        plt.figure(figsize=(10, 5))
        plt.plot(data.index, data['Close_MXN'], label=f"Precio de cierre de {metal} en MXN")
        plt.title(f"Tendencia de los Precios de {metal} en MXN")
        plt.xlabel('Fecha')
        plt.ylabel('Precio de Cierre (MXN)')
        plt.grid(True)
        st.pyplot(plt)
    
        # Guardar el gráfico como imagen en MXN
        grafico_mxn_filename = f'tendencia_precios_{metal.lower()}_mxn.png'
        plt.savefig(grafico_mxn_filename)
        
        # Botón de descarga para gráfico en MXN
        with open(grafico_mxn_filename, "rb") as file:
            st.download_button(label="Descargar gráfico en MXN", data=file, file_name=grafico_mxn_filename, mime="image/png")
