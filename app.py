import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Gestión Arroz con Leche con Guardado Local", layout="wide")
st.title("Gestión y Ventas - Arroz con Leche")

# Archivos para guardar datos
INV_FILE = "datos_inversion.csv"
VENT_FILE = "datos_ventas.csv"

# Funciones para cargar datos o crear vacíos
def cargar_datos(filename, columnas):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=columnas)

def guardar_datos(df, filename):
    df.to_csv(filename, index=False)

# Columnas esperadas para inversiones y ventas
col_inv = ["Pedido", "Fecha", "Concepto", "Valor"]
col_vent = ["Pedido", "Fecha", "Cliente", "Unidades", "Precio Unitario", "Pagado"]

# Cargar datos al inicio
df_inv = cargar_datos(INV_FILE, col_inv)
df_vent = cargar_datos(VENT_FILE, col_vent)

# SECCIÓN INVERSIONES
st.header("Inversiones por Pedido")
df_inv_edit = st.data_editor(df_inv, num_rows="dynamic", key="inv_editor")
if st.button("Guardar Inversiones"):
    guardar_datos(df_inv_edit, INV_FILE)
    st.success("Datos de inversiones guardados.")

# SECCIÓN VENTAS
st.header("Ventas por Pedido")
df_vent_edit = st.data_editor(df_vent, num_rows="dynamic", key="vent_editor")

# Calcular total venta (Unidades * Precio Unitario)
if not df_vent_edit.empty:
    df_vent_edit["Total Venta"] = df_vent_edit["Unidades"].astype(float) * df_vent_edit["Precio Unitario"].astype(float)
else:
    df_vent_edit["Total Venta"] = []

if st.button("Guardar Ventas"):
    guardar_datos(df_vent_edit, VENT_FILE)
    st.success("Datos de ventas guardados.")

# Mostrar resumen ventas y pagos por pedido
if not df_vent_edit.empty:
    total_ventas_por_pedido = df_vent_edit.groupby("Pedido")["Total Venta"].sum()
    total_pagado_por_pedido = df_vent_edit.groupby("Pedido")["Pagado"].sum()
else:
    total_ventas_por_pedido = pd.Series(dtype=float)
    total_pagado_por_pedido = pd.Series(dtype=float)

resumen_ventas = pd.DataFrame({
    "Total Ventas": total_ventas_por_pedido,
    "Total Pagado": total_pagado_por_pedido
})

st.subheader("Resumen Ventas y Pagos por Pedido")
st.table(resumen_ventas)

# Mostrar totales inversión por pedido
if not df_inv_edit.empty:
    total_inv_por_pedido = df_inv_edit.groupby("Pedido")["Valor"].sum()
else:
    total_inv_por_pedido = pd.Series(dtype=float)

st.subheader("Total Inversión por Pedido")
st.table(total_inv_por_pedido)

# Cálculo utilidad neta (Ingreso - Inversión)
df_utilidad = pd.DataFrame({
    "Inversión": total_inv_por_pedido,
    "Ingreso por Ventas": total_ventas_por_pedido
}).fillna(0)
df_utilidad["Utilidad Neta"] = df_utilidad["Ingreso por Ventas"] - df_utilidad["Inversión"]

st.header("Utilidad Neta por Pedido")
st.table(df_utilidad)

# Gráficos

# Gráfico inversión
fig1, ax1 = plt.subplots()
ax1.bar(total_inv_por_pedido.index, total_inv_por_pedido.values, color="#5A9")
ax1.set_ylabel("Valor ($)")
ax1.set_title("Inversión Total por Pedido")
st.pyplot(fig1)

# Gráfico ventas
fig2, ax2 = plt.subplots()
ax2.bar(total_ventas_por_pedido.index, total_ventas_por_pedido.values, color="#69C")
ax2.set_ylabel("Valor ($)")
ax2.set_title("Ventas Totales por Pedido")
st.pyplot(fig2)

# Gráfico utilidad neta con colores
fig3, ax3 = plt.subplots()
colors = ["#4CAF50" if val >= 0 else "#F44336" for val in df_utilidad["Utilidad Neta"]]
ax3.bar(df_utilidad.index, df_utilidad["Utilidad Neta"], color=colors)
ax3.set_ylabel("Valor ($)")
ax3.set_title("Utilidad Neta por Pedido")
st.pyplot(fig3)
