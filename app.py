import streamlit as st
import pandas as pd
import numpy as np
import glob
import os
import plotly.express as px
# --------------------------------------------------
# CONFIGURACION
# --------------------------------------------------

st.set_page_config(
    page_title="Crack del Campo - Cosechadoras",
    page_icon="🚜",
    layout="wide"
)

# --------------------------------------------------
# LEER BASE
# --------------------------------------------------

df = pd.read_excel(
    "BASE DE CLIENTES POR DESAFIO(Crack del campo - Cosechadoras).xlsx"
)

# --------------------------------------------------
# HISTORICO
# --------------------------------------------------

archivos_historicos = glob.glob("historico/*.xlsx")

historico = pd.read_excel(
    archivos_historicos[0]
)

historico = historico.drop(
    columns=["Organización"],
    errors="ignore"
)

historico = historico.drop_duplicates(
    subset=["Número de serie de la máquina"]
)

df.columns = df.columns.str.strip()
historico.columns = historico.columns.str.strip()

# Detectar automáticamente la columna de serie
col_serie_df = [c for c in df.columns if "serie" in c.lower()][0]
col_serie_hist = [c for c in historico.columns if "serie" in c.lower()][0]

df = df.merge(
    historico,
    left_on=col_serie_df,
    right_on=col_serie_hist,
    how="left"
)

# Eliminar columnas duplicadas
df = df.loc[:, ~df.columns.duplicated()]

# Corregir nombres con acentos
df.columns = (
    df.columns
    .str.replace("Ã¡", "á")
    .str.replace("Ã©", "é")
    .str.replace("Ã­", "í")
    .str.replace("Ã³", "ó")
    .str.replace("Ãº", "ú")
    .str.replace("Ã±", "ñ")
)

if "Máquina_x" in df.columns:
    df = df.rename(
        columns={"Máquina_x": "Máquina"}
    )

# --------------------------------------------------
# TECNOLOGIAS
# --------------------------------------------------

df["AT"] = pd.to_numeric(
    df["AutoTrac™ Activo"],
    errors="coerce"
)

df["RS"] = pd.to_numeric(
    df["AutoTrac™ RowSense™ Activo"],
    errors="coerce"
)

df["ATA"] = pd.to_numeric(
    df["Active Terrain Adjustment™ Activado"],
    errors="coerce"
)

df["ATTA"] = pd.to_numeric(
    df["Automatización de maniobras AutoTrac™ Activo"],
    errors="coerce"
)

df["AM"] = pd.to_numeric(
    df["Auto Maintain Activado"],
    errors="coerce"
)

df["AUTOPATH"] = pd.to_numeric(
    df["AutoPath™ Activo"],
    errors="coerce"
)

df["HSA"] = pd.to_numeric(
    df["Automatización de ajustes de cosecha Activo"],
    errors="coerce"
)

df["GSA"] = pd.to_numeric(
    df["Automatización de la velocidad de avance Activo"],
    errors="coerce"
)

# --------------------------------------------------
# PUNTAJE CRACK
# --------------------------------------------------

tec_basico = [
    "AT",
    "RS",
    "ATA",
    "ATTA"
]

tec_avanzado = [
    "AT",
    "RS",
    "ATA",
    "ATTA",
    "AM",
    "AUTOPATH",
    "HSA",
    "GSA"
]

df["Puntaje Crack"] = np.nan

mask_basico = (
    df["Crack del campo"]
    .astype(str)
    .str.upper()
    .str.contains("BASICO", na=False)
)

mask_avanzado = (
    df["Crack del campo"]
    .astype(str)
    .str.upper()
    .str.contains("AVANZADO", na=False)
)

df.loc[mask_basico, "Puntaje Crack"] = (
    df.loc[mask_basico, tec_basico]
    .mean(axis=1)
)

df.loc[mask_avanzado, "Puntaje Crack"] = (
    df.loc[mask_avanzado, tec_avanzado]
    .mean(axis=1)
)

# --------------------------------------------------
# FILTROS
# --------------------------------------------------

st.sidebar.title("Filtros")

sucursal = st.sidebar.selectbox(
    "Sucursal",
    ["Todas"] + sorted(
        list(df["Sucursal"].dropna().unique())
    )
)

if sucursal != "Todas":
    df = df[df["Sucursal"] == sucursal]

razon_social = st.sidebar.selectbox(
    "Razón Social",
    ["Todas"] + sorted(
        list(df["Organización"].dropna().unique())
    )
)

if razon_social != "Todas":
    df = df[df["Organización"] == razon_social]

categoria = st.sidebar.selectbox(
    "Categoría",
    ["Todas"] + sorted(
        df["Crack del campo"].dropna().unique()
    )
)

if categoria != "Todas":
    df = df[
        df["Crack del campo"] == categoria
    ]

st.sidebar.markdown("---")

st.sidebar.subheader("Histórico")

st.sidebar.write(
    f"Archivos encontrados: {len(archivos_historicos)}"
)

for archivo in archivos_historicos:
    st.sidebar.write(
        os.path.basename(archivo)
    )

# --------------------------------------------------
# TITULO
# --------------------------------------------------

st.title("🚜 Crack del Campo - Cosechadoras")

# --------------------------------------------------
# KPI GENERALES
# --------------------------------------------------

participantes = len(df)

licencias_vigentes = (
    df["Estado Licencia"]
    .eq("Vigente")
    .sum()
)

puntaje_promedio = round(
    df["Puntaje Crack"].mean(),
    1
)

oportunidades_renovacion = (
    df["Estado Licencia"]
    .ne("Vigente")
    .sum()
)

con_actividad = (
    df["Puntaje Crack"] > 0
).sum()

sin_actividad = (
    df["Puntaje Crack"] == 0
).sum()

sin_datos = (
    df["Puntaje Crack"].isna()
).sum()

st.divider()

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    st.metric(
        "Participantes",
        participantes
    )

with col2:
    st.metric(
        "Puntaje Promedio",
        f"{puntaje_promedio:.1f}%"
    )

with col3:
    st.metric(
        "Licencias Vigentes",
        licencias_vigentes
    )

with col4:
    st.metric(
        "Oport. Renovación",
        oportunidades_renovacion
    )

with col5:
    st.metric(
        "✅ Con Actividad",
        con_actividad
    )

with col6:
    st.metric(
        "⛔ Sin Actividad",
        sin_actividad
    )

with col7:
    st.metric(
        "➖ Sin Datos",
        sin_datos
    )
st.divider()
# --------------------------------------------------
# PODIO
# --------------------------------------------------

st.subheader("🏆 Podio")

def mostrar_podio(df_podio, titulo):

    st.markdown(f"### {titulo}")

    # Eliminar registros sin puntaje
    df_podio = df_podio[
        df_podio["Puntaje Crack"].notna()
    ]

    cantidad = len(df_podio)

    if cantidad == 0:
        st.info("No hay participantes con puntaje disponible.")
        return

    if cantidad == 1:

        col1, col2, col3 = st.columns(3)

        with col2:
            st.markdown("#### 🥇 Primero")
            st.write(df_podio.iloc[0]["Organización"])
            st.markdown(
                f"## {df_podio.iloc[0]['Puntaje Crack']:.1f}%"
            )

        return

    if cantidad == 2:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 🥈 Segundo")
            st.write(df_podio.iloc[1]["Organización"])
            st.markdown(
                f"### {df_podio.iloc[1]['Puntaje Crack']:.1f}%"
            )

        with col2:
            st.markdown("#### 🥇 Primero")
            st.write(df_podio.iloc[0]["Organización"])
            st.markdown(
                f"## {df_podio.iloc[0]['Puntaje Crack']:.1f}%"
            )

        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🥈 Segundo")
        st.write(df_podio.iloc[1]["Organización"])
        st.markdown(
            f"### {df_podio.iloc[1]['Puntaje Crack']:.1f}%"
        )

    with col2:
        st.markdown("#### 🥇 Primero")
        st.write(df_podio.iloc[0]["Organización"])
        st.markdown(
            f"## {df_podio.iloc[0]['Puntaje Crack']:.1f}%"
        )

    with col3:
        st.markdown("#### 🥉 Tercero")
        st.write(df_podio.iloc[2]["Organización"])
        st.markdown(
            f"### {df_podio.iloc[2]['Puntaje Crack']:.1f}%"
        )
if categoria == "Todas":

    podio_avanzado = (
        df[
            df["Crack del campo"]
            .astype(str)
            .str.contains("Avanzado", na=False)
        ]
        .sort_values(
            "Puntaje Crack",
            ascending=False
        )
        .head(3)
    )

    podio_basico = (
        df[
            df["Crack del campo"]
            .astype(str)
            .str.contains("Basico", na=False)
        ]
        .sort_values(
            "Puntaje Crack",
            ascending=False
        )
        .head(3)
    )

    mostrar_podio(
        podio_avanzado,
        "🏆 Categoría Avanzado"
    )

    st.divider()

    mostrar_podio(
        podio_basico,
        "🏆 Categoría Básico"
    )

else:

    podio = (
        df.sort_values(
            "Puntaje Crack",
            ascending=False
        )
        .head(3)
    )

    mostrar_podio(
        podio,
        f"🏆 {categoria}"
    )

# --------------------------------------------------
# ADOPCION TECNOLOGICA
# --------------------------------------------------

st.divider()

st.subheader("📈 Adopción Tecnológica")

if categoria == "Basico":

    tecnologias_grafico = {
        "AT": df["AT"].mean(),
        "RS": df["RS"].mean(),
        "ATA": df["ATA"].mean(),
        "ATTA": df["ATTA"].mean()
    }

    tecnologias_adopcion = [
        "AT",
        "RS",
        "ATA",
        "ATTA"
    ]

elif categoria == "Avanzado":

    tecnologias_grafico = {
        "AT": df["AT"].mean(),
        "RS": df["RS"].mean(),
        "ATA": df["ATA"].mean(),
        "ATTA": df["ATTA"].mean(),
        "AM": df["AM"].mean(),
        "AUTOPATH": df["AUTOPATH"].mean(),
        "HSA": df["HSA"].mean(),
        "GSA": df["GSA"].mean()
    }

    tecnologias_adopcion = [
        "AT",
        "RS",
        "ATA",
        "ATTA",
        "AM",
        "AUTOPATH",
        "HSA",
        "GSA"
    ]

else:

    tecnologias_grafico = {
        "AT": df["AT"].mean(),
        "RS": df["RS"].mean(),
        "ATA": df["ATA"].mean(),
        "ATTA": df["ATTA"].mean(),
        "AM": df["AM"].mean(),
        "AUTOPATH": df["AUTOPATH"].mean(),
        "HSA": df["HSA"].mean(),
        "GSA": df["GSA"].mean()
    }

    tecnologias_adopcion = [
        "AT",
        "RS",
        "ATA",
        "ATTA",
        "AM",
        "AUTOPATH",
        "HSA",
        "GSA"
    ]
# -------------------------
# USO PROMEDIO
# -------------------------

uso_promedio = pd.DataFrame(
    list(tecnologias_grafico.items()),
    columns=["Tecnología", "Promedio"]
)

uso_promedio = uso_promedio.sort_values(
    "Promedio",
    ascending=False
)

# -------------------------
# ADOPCION
# -------------------------

adopcion_real = {}

total_maquinas = len(df)

for tec in tecnologias_adopcion:

    maquinas_que_usan = (
        df[tec].fillna(0) > 0
    ).sum()

    if total_maquinas > 0:

        adopcion_real[tec] = (
            maquinas_que_usan
            / total_maquinas
            * 100
        )

    else:

        adopcion_real[tec] = 0

adopcion_df = pd.DataFrame(
    {
        "Tecnología": list(adopcion_real.keys()),
        "Adopción": list(adopcion_real.values())
    }
)

adopcion_df = adopcion_df.sort_values(
    "Adopción",
    ascending=False
)

col1, col2 = st.columns([3,1])

with col1:

    st.markdown("#### Uso promedio de la tecnología")

    fig = px.bar(
        uso_promedio,
        x="Tecnología",
        y="Promedio",
        text="Promedio",
        title="Promedio de utilización por tecnología"
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig.update_layout(
        yaxis_title="Uso (%)",
        xaxis_title="",
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "Este indicador refleja el promedio de uso de cada tecnología considerando únicamente las máquinas con datos registrados para dicha tecnología."
    )

    st.markdown("#### Adopción de la tecnología")

    fig2 = px.bar(
        adopcion_df,
        x="Tecnología",
        y="Adopción",
        text="Adopción",
        title="Porcentaje de máquinas que utilizan la tecnología"
    )

    fig2.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig2.update_layout(
        yaxis_title="Adopción (%)",
        xaxis_title="",
        height=500
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.caption(
        "La adopción representa el porcentaje de máquinas con datos registrados que presentan utilización de la tecnología."
    )

with col2:

    st.markdown("### 📖 Referencias")

    if categoria == "Basico":

        st.markdown("""
**AT** → AutoTrac™

**RS** → RowSense™

**ATA** → Active Terrain Adjustment™

**ATTA** → Automatización de Maniobras AutoTrac™
""")

    else:

        st.markdown("""
**AT** → AutoTrac™

**RS** → RowSense™

**ATA** → Active Terrain Adjustment™

**ATTA** → Automatización de Maniobras AutoTrac™

**AM** → Auto Maintain

**AUTOPATH** → AutoPath™

**HSA** → Harvest Settings Automation

**GSA** → Ground Speed Automation
""")

# --------------------------------------------------
# RANKING GENERAL
# --------------------------------------------------

st.subheader(
    "🏆 Ranking Crack del Campo"
)

ranking = (
    df.sort_values(
        "Puntaje Crack",
        ascending=False
    )
    .reset_index(drop=True)
)

ranking.insert(
    0,
    "Posición",
    range(1, len(ranking) + 1)
)

# Eliminar columnas duplicadas
ranking = ranking.loc[:, ~ranking.columns.duplicated()]

st.dataframe(
    ranking[
        [
            "Posición",
            "Organización",
            "Máquina",
            "Crack del campo",
            "Puntaje Crack",
            "Estado Licencia"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

st.caption(
    "El Puntaje Crack se calcula utilizando el promedio de adopción de las tecnologías disponibles para cada categoría. Los valores 0 se consideran en el cálculo. Los valores vacíos (NaN) no participan del promedio."
)
# --------------------------------------------------
# OPORTUNIDADES RENOVACION
# --------------------------------------------------

st.divider()

st.subheader(
    "🔄 Oportunidades de Renovación"
)

renovacion = df[
    df["Estado Licencia"] != "Vigente"
].copy()

# Eliminar columnas duplicadas
renovacion = renovacion.loc[:, ~renovacion.columns.duplicated()]

st.dataframe(
    renovacion[
        [
            "Organización",
            "Máquina",
            "Licencia",
            "Vencimiento Licencia"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# DETALLE COMPLETO
# --------------------------------------------------

st.divider()

st.subheader(
    "📋 Detalle Completo"
)

detalle = df.loc[:, ~df.columns.duplicated()].copy()

columnas_detalle = [
    "Organización",
    "Máquina",
    "Número de serie de la máquina",
    "Nombre Operador",
    "Contacto/Whatsapp",
    "Sucursal",
    "Crack del campo",
    "Licencia",
    "Vencimiento Licencia",
    "Estado Licencia",
    "AT",
    "RS",
    "ATA",
    "ATTA",
    "AM",
    "AUTOPATH",
    "HSA",
    "GSA",
    "Puntaje Crack"
]

columnas_detalle = [
    col for col in columnas_detalle
    if col in detalle.columns
]

st.dataframe(
    detalle[columnas_detalle],
    use_container_width=True,
    hide_index=True
)
