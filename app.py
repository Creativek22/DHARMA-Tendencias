import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from datetime import datetime
import yfinance as yf
import base64

# Configuración del tema en config.toml o por defecto
st.set_page_config(page_title="Análisis de Mercados de Metales", layout="centered")

# Inyectar CSS personalizado para fondo blanco, ajuste de logo y centrado de tabla
st.markdown(
    """
    <style>
    .main {
        background-color: white;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    .dataframe-container {
        display: flex;
        justify-content: center;
    }
    .dataframe-container .stDataFrame {
        width: 90%;
    }
    .precio-container {
        text-align: center;
        font-size: 22px; /* Ajustar el tamaño de la fuente */
        font-weight: bold;
        color: darkblue; /* Cambiar el color a un azul más oscuro */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Cargar el logo de la empresa en formato webp
with open("logo.webp", "rb") as image_file:
    logo_bytes = image_file.read()
    logo_b64 = base64.b64encode(logo_bytes).decode("utf-8")

# Mostrar el logo centrado en la parte superior
st.markdown(f'<div class="logo-container"><img src="data:image/webp;base64,{logo_b64}" width="300"></div>', unsafe_allow_html=True)

# Título de la aplicación
st.title("Análisis de Mercados de Metales")

# Descripción de la aplicación
st.write("""
Asistente de IA para el análisis de tendencias de mercado en materias primas.
""")

# Monitoreo del precio del níquel en tiempo real desde Markets Insider
st.write("Monitoreando el precio del níquel en tiempo real...")
url = 'https://markets.businessinsider.com/commodities/nickel-price'

def get_nickel_price(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        price = soup.find('span', {'class': 'price-section__current-value'}).text.strip()
        return float(price.replace(',', ''))  # Convertir a float para cálculos
    except Exception as e:
        return f"Error: {e}"

precio_niquel_usd = get_nickel_price(url)
tipo_cambio = 18.5  # Ajusta según el tipo de cambio actual
precio_niquel_mxn = precio_niquel_usd * tipo_cambio

# Mostrar los precios en USD y MXN, centrados y en negrita
st.markdown(f'<div class="precio-container">{precio_niquel_usd:.2f} USD/MT<br>{precio_niquel_mxn:.2f} MXN/MT</div>', unsafe_allow_html=True)

# Selección de metal
metal = st.selectbox("Selecciona el metal", ["Petróleo", "Aluminio", "Cobre", "Níquel"])

# Selección de rango de fechas y horas
fecha_inicio = st.date_input("Fecha de inicio", pd.to_datetime("2021-01-01"))
hora_inicio = st.time_input("Hora de inicio", datetime.strptime("00:00", "%H:%M").time())
fecha_fin = st.date_input("Fecha de fin", pd.to_datetime("2023-01-01"))
hora_fin = st.time_input("Hora de fin", datetime.strptime("23:59", "%H:%M").time())

# Combinar fecha y hora para las consultas
fecha_inicio = datetime.combine(fecha_inicio, hora_inicio)
fecha_fin = datetime.combine(fecha_fin, hora_fin)

# Botón para realizar el análisis
if st.button("Analizar"):
    # Convertir las selecciones a símbolos de Yahoo Finance
    simbolos = {"Petróleo": "CL=F", "Aluminio": "ALI=F", "Cobre": "HG=F", "Níquel": "NI=F"}
    simbolo = simbolos[metal]

    # Descargar los datos
    st.write(f"Descargando datos para {metal} desde {fecha_inicio} hasta {fecha_fin}...")
    data = yf.download(simbolo, start=fecha_inicio, end=fecha_fin)
    
    # Verificar si se descargaron datos
    if data.empty:
        st.write("No se encontraron datos para las fechas seleccionadas.")
    else:
        # Calcular cambio porcentual diario
        data['% Change'] = data['Close'].pct_change() * 100
        
        # Guardar los datos en un archivo CSV
        data.to_csv(f'datos_{metal.lower()}.csv', encoding='utf-8', index=True)
        st.write(f"Datos guardados en 'datos_{metal.lower()}.csv'.")
    
        # Mostrar los datos centrados
        st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
        st.dataframe(data)
        st.markdown('</div>', unsafe_allow_html=True)
    
        # Mostrar el gráfico en USD
        plt.figure(figsize=(10, 5))
        plt.plot(data.index, data['Close'], label=f"Precio de cierre de {metal} en USD")
        plt.title(f"Tendencia de los Precios de {metal} en USD")
        plt.xlabel('Fecha')
        plt.ylabel('Precio de Cierre (USD)')
        plt.grid(True)
        st.pyplot(plt)
    
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
    
        # Guardar el gráfico como imagen
        grafico_filename = f'tendencia_precios_{metal.lower()}_mxn.png'
        plt.savefig(grafico_filename)
        st.write(f"Gráfico en MXN guardado como '{grafico_filename}'.")
