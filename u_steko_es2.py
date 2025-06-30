import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Calculadora U-Value Steko", layout="wide")
st.title("🧱 Calculadora de Transmitancia Térmica - Sistema Steko")

# =============================================
# 1. BASE DE DATOS ACTUALIZADA PARA COINCIDIR CON EXCEL
# =============================================

materiales_base = {
    # Materiales principales (con λ y densidad)
    "Vertikalschalung Fi/Ta": {"lambda": 0.12, "densidad": 470, "categoria": "Revestimiento", "R": 0},
    "Kreuzrost Fi/Ta": {"lambda": 0.12, "densidad": 470, "categoria": "Estructura", "R": 0},
    "Holzrost Fi/Ta (Hinterlüftung)": {"lambda": 0.12, "densidad": 470, "categoria": "Estructura", "R": 0},
    "Gipsfaserplatte Typ F": {"lambda": 0.32, "densidad": 1150, "categoria": "Panel"},
    "Mineralwolldämmung": {"lambda": 0.035, "densidad": 38, "categoria": "Aislamiento"},
    "Mineralwolldämmung Dissco": {"lambda": 0.04, "densidad": 150, "categoria": "Aislamiento"},
    "Steko-Modul ausgeflockt": {"lambda": 0.073, "densidad": 260, "categoria": "Núcleo"},
    "Gipskartonplatte": {"lambda": 0.21, "densidad": 650, "categoria": "Panel interior"},
    "Holzweichfaserplatte": {"lambda": 0.04, "densidad": 115, "categoria": "Aislamiento"},
    "Lehmputz": {"lambda": 0.6, "densidad": 1500, "categoria": "Acabado"},
    "CLT Fi/Ta": {"lambda": 0.12, "densidad": 470, "categoria": "Estructura"},
    
    # Elementos especiales (valores tomados directamente del Excel)
    "Übergang a": {"lambda": None, "densidad": None, "categoria": "Transición", "R": 0.04},
    "Übergang i": {"lambda": None, "densidad": None, "categoria": "Transición", "R": 0.125},
    "Fassadenbahn": {"lambda": None, "densidad": None, "categoria": "Barrera", "R": 0},
    "Dampfbremse": {"lambda": None, "densidad": None, "categoria": "Barrera", "R": 0}
}

# =============================================
# 2. CONFIGURACIONES PREDEFINIDAS (sin cambios)
# =============================================

configuraciones = {
    "W_01 - Gipsfaserplatte aussenseitig": [
        {"material": "Vertikalschalung Fi/Ta", "espesor": 24},
        {"material": "Kreuzrost Fi/Ta", "espesor": 48},
        {"material": "Übergang a", "espesor": 0},
        {"material": "Fassadenbahn", "espesor": 1},
        {"material": "Gipsfaserplatte Typ F", "espesor": 15},
        {"material": "Mineralwolldämmung", "espesor": 60},
        {"material": "Mineralwolldämmung", "espesor": 60},
        {"material": "Dampfbremse", "espesor": 1},
        {"material": "Steko-Modul ausgeflockt", "espesor": 160},
        {"material": "Mineralwolldämmung", "espesor": 40},
        {"material": "Gipskartonplatte", "espesor": 15},
        {"material": "Gipskartonplatte", "espesor": 15},
        {"material": "Übergang i", "espesor": 0}
    ],
    "W_02 - Flumroc Dissco-Platte 60mm": [
        {"material": "Vertikalschalung Fi/Ta", "espesor": 24},
        {"material": "Kreuzrost Fi/Ta", "espesor": 48},
        {"material": "Übergang a", "espesor": 0},
        {"material": "Fassadenbahn", "espesor": 1},
        {"material": "Mineralwolldämmung Dissco", "espesor": 60},
        {"material": "Mineralwolldämmung", "espesor": 60},
        {"material": "Dampfbremse", "espesor": 1},
        {"material": "Steko-Modul ausgeflockt", "espesor": 160},
        {"material": "Mineralwolldämmung", "espesor": 40},
        {"material": "Gipskartonplatte", "espesor": 15},
        {"material": "Gipskartonplatte", "espesor": 15},
        {"material": "Übergang i", "espesor": 0}
    ],
    "W_03 - Dissco, sin Vorsatzschale": [
        {"material": "Vertikalschalung Fi/Ta", "espesor": 24},
        {"material": "Kreuzrost Fi/Ta", "espesor": 48},
        {"material": "Übergang a", "espesor": 0},
        {"material": "Fassadenbahn", "espesor": 1},
        {"material": "Mineralwolldämmung Dissco", "espesor": 60},
        {"material": "Mineralwolldämmung", "espesor": 100},
        {"material": "Dampfbremse", "espesor": 1},
        {"material": "Steko-Modul ausgeflockt", "espesor": 160},
        {"material": "Gipskartonplatte", "espesor": 15},
        {"material": "Übergang i", "espesor": 0}
    ],
    "W_04 - CLT statt Steko": [
        {"material": "Vertikalschalung Fi/Ta", "espesor": 24},
        {"material": "Kreuzrost Fi/Ta", "espesor": 48},
        {"material": "Übergang a", "espesor": 0},
        {"material": "Fassadenbahn", "espesor": 1},
        {"material": "Gipsfaserplatte Typ F", "espesor": 15},
        {"material": "Mineralwolldämmung", "espesor": 60},
        {"material": "Mineralwolldämmung", "espesor": 80},
        {"material": "Dampfbremse", "espesor": 1},
        {"material": "CLT Fi/Ta", "espesor": 120},
        {"material": "Mineralwolldämmung", "espesor": 40},
        {"material": "Gipskartonplatte", "espesor": 15},
        {"material": "Gipskartonplatte", "espesor": 15},
        {"material": "Übergang i", "espesor": 0}
    ],
    "W_05 - Variante con Lehmputz": [
        {"material": "Vertikalschalung Fi/Ta", "espesor": 24},
        {"material": "Holzrost Fi/Ta (Hinterlüftung)", "espesor": 30},
        {"material": "Übergang a", "espesor": 0},
        {"material": "Fassadenbahn", "espesor": 0.5},
        {"material": "Mineralwolldämmung Dissco", "espesor": 60},
        {"material": "Mineralwolldämmung", "espesor": 60},
        {"material": "Dampfbremse", "espesor": 0.5},
        {"material": "Steko-Modul ausgeflockt", "espesor": 160},
        {"material": "Holzweichfaserplatte", "espesor": 60},
        {"material": "Lehmputz", "espesor": 5},
        {"material": "Übergang i", "espesor": 0}
    ]
}

# =============================================
# 3. FUNCIÓN DE CÁLCULO ACTUALIZADA PARA COINCIDIR CON EXCEL
# =============================================

def calcular_u_value(capas):
    datos = []
    resistencia_total = 0
    espesor_total = 0
    
    for capa in capas:
        material = capa["material"]
        props = materiales_base.get(material, {})
        espesor = capa["espesor"]
        espesor_total += espesor
        
        # Manejo especial de resistencias según el Excel
        if material in ["Vertikalschalung Fi/Ta", "Kreuzrost Fi/Ta", "Holzrost Fi/Ta (Hinterlüftung)",
                       "Fassadenbahn", "Dampfbremse"]:
            r_capa = 0  # Estos materiales no contribuyen a la resistencia térmica
        elif material == "Übergang a":
            r_capa = 0.04  # Valor fijo como en Excel (=1/25)
        elif material == "Übergang i":
            r_capa = 0.125  # Valor fijo como en Excel
        else:  # Para materiales normales
            lambda_val = props.get("lambda")
            if lambda_val and lambda_val > 0:
                r_capa = (espesor / 1000) / lambda_val
            else:
                r_capa = 0
        
        resistencia_total += r_capa
        
        # Cálculo de flächenlist (igual que en Excel)
        densidad = props.get("densidad")
        flachenlast = (espesor * densidad) / 100000 if densidad else 0
        
        # Preparación de datos para tabla
        datos.append({
            "Capa": material,
            "Espesor (mm)": espesor,
            "λ (W/mK)": props.get("lambda"),
            "Densidad (kg/m³)": props.get("densidad"),
            "Carga (kN/m²)": flachenlast,
            "R (m²K/W)": r_capa,
            "Contribución (%)": (r_capa/resistencia_total)*100 if resistencia_total > 0 else 0
        })
    
    u_value = 1 / resistencia_total if resistencia_total > 0 else float('inf')
    
    return pd.DataFrame(datos), resistencia_total, u_value, espesor_total

# =============================================
# 4. INTERFAZ DE USUARIO - MODO COMPARATIVO COMPLETO
# =============================================

# Sidebar - Configuración
with st.sidebar:
    st.header("⚙ Configuración del Muro")
    
    # Selector de modo (individual/comparativo)
    modo = st.radio(
        "Modo de operación:",
        ["🔍 Análisis individual", "🔀 Comparar configuraciones"],
        index=0,
        key="modo_operacion"
    )
    
    # Configuración para modo individual
    if st.session_state.modo_operacion == "🔍 Análisis individual":
        config_seleccionada = st.selectbox(
            "Configuración predefinida:",
            ["Personalizado"] + list(configuraciones.keys()),
            index=0,
            key="config_individual"
        )
        
        # Modo personalizado
        if config_seleccionada == "Personalizado":
            num_capas = st.number_input("Número de capas:", 1, 20, 5, key="num_capas")
            capas = []
            
            for i in range(num_capas):
                st.subheader(f"Capa {i+1}")
                material = st.selectbox(
                    "Material",
                    list(materiales_base.keys()),
                    key=f"mat_{i}"
                )
                espesor_default = materiales_base.get(material, {}).get("espesor", 10)
                espesor = st.number_input(
                    "Espesor (mm)",
                    1, 1000, espesor_default,
                    key=f"esp_{i}"
                )
                capas.append({"material": material, "espesor": espesor})
        else:
            capas = configuraciones[config_seleccionada]
        
        # Resumen visual de capas
        st.subheader("🧱 Resumen de capas")
        for i, capa in enumerate(capas, 1):
            props = materiales_base.get(capa["material"], {})
            st.caption(f"{i}. {capa['material']} ({capa['espesor']}mm) - {props.get('categoria', '')}")

    # Configuración para modo comparativo
    else:
        st.subheader("🔄 Configuraciones a comparar")
        configs_comparar = st.multiselect(
            "Selecciona configuraciones (máx. 3):",
            list(configuraciones.keys()),
            default=[list(configuraciones.keys())[0], list(configuraciones.keys())[1]],
            max_selections=3,
            key="configs_comparar"
        )

# Área principal de resultados
if st.session_state.modo_operacion == "🔍 Análisis individual":
    if st.button("Calcular U-Value", type="primary", key="btn_individual"):
        df, r_total, u_value, espesor_total = calcular_u_value(capas)
        
        # Resultados principales
        st.success(f"**U-Value calculado:** {u_value:.3f} W/m²K")
        col1, col2, col3 = st.columns(3)
        col1.metric("Resistencia Total", f"{r_total:.3f} m²K/W")
        col2.metric("Espesor Total", f"{espesor_total} mm")
        col3.metric("Cumple Passivhaus?", "✅ Sí" if u_value <= 0.15 else "❌ No")
        
        # Tabla detallada
        st.subheader("📋 Detalle por capas")
        st.dataframe(
            df.style.format({
                "λ (W/mK)": "{:.3f}",
                "Carga (kN/m²)": "{:.4f}",
                "R (m²K/W)": "{:.3f}",
                "Contribución (%)": "{:.1f}"
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Gráfico de contribución
        st.subheader("📊 Contribución al aislamiento")
        fig = px.bar(
            df, 
            x="R (m²K/W)", 
            y="Capa",
            orientation='h',
            color="Capa",
            title="Resistencia térmica por capa"
        )
        st.plotly_chart(fig, use_container_width=True)

else:  # Modo comparativo
    if "configs_comparar" in st.session_state and st.session_state.configs_comparar:
        st.header("📊 Comparación de configuraciones")
        
        # 1. Tarjetas superiores con U-Values
        st.subheader("🔍 Comparación de U-Values")
        cols = st.columns(len(st.session_state.configs_comparar))
        datos_comparacion = []
        
        for i, config in enumerate(st.session_state.configs_comparar):
            with cols[i]:
                # Calcular valores
                df, r_total, u_value, espesor_total = calcular_u_value(configuraciones[config])
                
                # Mostrar tarjeta
                st.metric(
                    label=f"**{config}**",
                    value=f"{u_value:.3f} W/m²K",
                    delta=f"Espesor: {espesor_total} mm" if i == 0 else None,
                    delta_color="off"
                )
                
                # Guardar datos
                datos_comparacion.append({
                    "Configuración": config,
                    "U-Value": u_value,
                    "Espesor (mm)": espesor_total,
                    "Resistencia (m²K/W)": r_total
                })
        
        # 2. Gráficos comparativos
        st.subheader("📈 Visualización comparativa")
        df_comparacion = pd.DataFrame(datos_comparacion)
        
        # Gráfico de U-Values
        fig_u = px.bar(
            df_comparacion,
            x="Configuración",
            y="U-Value",
            color="Configuración",
            text_auto=".3f",
            title="U-Value por configuración"
        )
        fig_u.add_hline(y=0.15, line_dash="dash", line_color="red", annotation_text="Límite Passivhaus")
        st.plotly_chart(fig_u, use_container_width=True)
        
        # Gráfico combinado
        fig_combi = px.bar(
            df_comparacion.melt(id_vars="Configuración", value_vars=["Espesor (mm)", "Resistencia (m²K/W)"]),
            x="Configuración",
            y="value",
            color="variable",
            barmode="group",
            title="Espesor vs Resistencia",
            labels={"value": "Valor", "variable": "Métrica"}
        )
        st.plotly_chart(fig_combi, use_container_width=True)
        
        # 3. Tablas detalladas (en pestañas)
        st.subheader("📝 Detalles por configuración")
        tabs = st.tabs([f"**{config}**" for config in st.session_state.configs_comparar])
        
        for i, tab in enumerate(tabs):
            with tab:
                df_config, _, _, _ = calcular_u_value(configuraciones[st.session_state.configs_comparar[i]])
                st.dataframe(
                    df_config.style.format({
                        "λ (W/mK)": "{:.3f}",
                        "Carga (kN/m²)": "{:.4f}",
                        "R (m²K/W)": "{:.3f}",
                        "Contribución (%)": "{:.1f}"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        
        # 4. Exportación
        st.download_button(
            "📤 Exportar comparación (CSV)",
            df_comparacion.to_csv(index=False, sep=";", decimal=",").encode("utf-8"),
            "comparacion_uvalues.csv",
            "text/csv"
        )
    else:
        st.warning("⚠️ Selecciona al menos una configuración para comparar")


# Información adicional
with st.expander("📚 Guía de Uso"):
    st.markdown("""
    ### ¿Cómo usar esta calculadora?
    1. **Selecciona una configuración predefinida** o elige "Personalizado"
    2. **Ajusta los materiales y espesores** según tu diseño
    3. **Haz clic en 'Calcular U-Value'** para obtener resultados
    
    ### Interpretación de resultados:
    - **U-Value**: Coeficiente de transmitancia térmica (menor = mejor aislamiento)
    - **Resistencia Total (R)**: Suma de resistencias térmicas (mayor = mejor)
    - **Contribución %**: Qué porcentaje del aislamiento aporta cada capa
    
    ### Valores de referencia:
    | Estándar         | U-Value Máximo |
    |------------------|----------------|
    | Passivhaus       | ≤ 0.15 W/m²K   |
    | CTE España       | ≤ 0.30 W/m²K   |
    | MINERGIE (Suiza) | ≤ 0.20 W/m²K   |
    """)

with st.expander("ℹ️ Sobre las configuraciones"):
    st.markdown("""
    ### Configuraciones disponibles:
    - **W_01**: Gipsfaserplatte exterior + doble capa de lana mineral
    - **W_02**: Placa Dissco exterior (λ=0.04)
    - **W_03**: Versión simplificada sin doble placa de yeso
    - **W_04**: Usa CLT en lugar de Steko
    - **W_05**: Variante con Lehmputz y Holzrost
    
    ### Diferencias clave:
    - **W_03** tiene mayor espesor de lana mineral (100mm)
    - **W_05** usa materiales naturales (Lehmputz)
    - **W_04** es más masivo (CLT en lugar de Steko)
    """)