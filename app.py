import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from datetime import datetime
import yfinance as yf

# Configuración del tema en config.toml o por defecto
st.set_page_config(page_title="Análisis de Mercados de Metales", layout="centered")

# Inyectar CSS personalizado para fondo blanco, ajuste de logo, centrado de tabla y personalización del título
st.markdown(
    """
    <style>
    .main {
        background-color: white;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .title-text {
        font-size: 32px; /* Cambia el tamaño de la fuente aquí */
        color: #4d4d4d;  /* Cambia el color a gris oscuro */
        text-align: center; /* Alinea el texto al centro */
    }
    .dataframe-container {
        display: flex;
        justify-content: center;
    }
    .dataframe-container .stDataFrame {
        width: 100%; /* Cambiar a 100% para ocupar todo el ancho */
    }
    .precio-container {
        text-align: center;
        font-size: 22px; /* Ajustar el tamaño de la fuente */
        font-weight: bold;
        color: darkblue; /* Cambiar el color a un azul más oscuro */
    }
    @media (max-width: 768px) {
        .logo-container {
            margin-bottom: 10px;
        }
        .title-text {
            font-size: 24px; /* Reducir el tamaño de la fuente en dispositivos móviles */
        }
        .precio-container {
            font-size: 18px; /* Ajustar el tamaño de la fuente para móviles */
        }
        .stButton button {
            width: 100%; /* Asegura que los botones sean completamente visibles en móviles */
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Cargar el logo de la empresa
logo = Image.open("logo.webp")

# Mostrar el logo centrado en la parte superior
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image(logo, width=400)  # Ajustar el ancho según sea necesario
st.markdown('</div>', unsafe_allow_html=True)

# Título de la aplicación
st.markdown(
    """
    <h1 style='text-align: center; color: darkgray; font-size: 28px;'>Análisis de Mercados de Metales</h1>
    """,
    unsafe_allow_html=True
)

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
    
        # Guardar el gráfico como imagen en USD
        grafico_usd_filename = f'tendencia_precios_{metal.lower()}_usd.png'
        plt.savefig(grafico_usd_filename)
        
        # Botón de descarga para gráfico en USD
        with open(grafico_usd_filename, "rb") as file:
            st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
            st.download_button(
                label="Descargar gráfico en USD",
                data=file,
                file_name=grafico_usd_filename,
                mime="image/png"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
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
            st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
            st.download_button(
                label="Descargar gráfico en MXN",
                data=file,
                file_name=grafico_mxn_filename,
                mime="image/png"
            )
            st.markdown('</div>', unsafe_allow_html=True)
