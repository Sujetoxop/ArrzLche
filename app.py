import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Gestión Arroz con Leche Mejorada", layout="wide")
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

# Columnas para inversiones y ventas
col_inv = ["Pedido", "Fecha", "Concepto", "Valor"]
col_vent = ["Pedido", "Fecha", "Cliente", "Unidades", "Precio Unitario", "Pagado"]

# Cargar datos
df_inv = cargar_datos(INV_FILE, col_inv)
df_vent = cargar_datos(VENT_FILE, col_vent)

# Sección inversiones (igual que antes)
st.header("Inversiones por Pedido")
df_inv_edit = st.data_editor(df_inv, num_rows="dynamic", key="inv_editor")
if st.button("Guardar Inversiones"):
    guardar_datos(df_inv_edit, INV_FILE)
    st.success("Datos de inversiones guardados.")

# Sección ventas con cálculo automático del Total Venta
st.header("Ventas por Pedido")

# Para evitar modificar df_vent original, creamos copia para edición
df_vent_edit = df_vent.copy()

# Para evitar errores, aseguramos que Unidades y Precio Unitario sean numéricos, si no, los reemplazamos por 0
df_vent_edit["Unidades"] = pd.to_numeric(df_vent_edit["Unidades"], errors='coerce').fillna(0)
df_vent_edit["Precio Unitario"] = pd.to_numeric(df_vent_edit["Precio Unitario"], errors='coerce').fillna(0)

# Calculamos la columna Total Venta automáticamente
df_vent_edit["Total Venta"] = df_vent_edit["Unidades"] * df_vent_edit["Precio Unitario"]

# Insertamos el editor para todas las columnas excepto Total Venta (que es calculado)
# Para esto creamos un DataFrame temporal sin "Total Venta"
df_vent_edit_display = df_vent_edit.drop(columns=["Total Venta"])

# Mostramos tabla editable
df_vent_actualizado = st.data_editor(df_vent_edit_display, num_rows="dynamic", key="vent_editor")

# Una vez editada la tabla, recalculamos Total Venta
df_vent_actualizado["Unidades"] = pd.to_numeric(df_vent_actualizado["Unidades"], errors='coerce').fillna(0)
df_vent_actualizado["Precio Unitario"] = pd.to_numeric(df_vent_actualizado["Precio Unitario"], errors='coerce').fillna(0)

df_vent_actualizado["Total Venta"] = df_vent_actualizado["Unidades"] * df_vent_actualizado["Precio Unitario"]

# Validar que columna Cliente contenga texto, y advertir si algún valor no es texto
if not df_vent_actualizado["Cliente"].apply(lambda x: isinstance(x, str)).all():
    st.warning("La columna 'Cliente' debe contener nombres (texto). Por favor, corrige valores numéricos.")

# Botón para guardar ventas
if st.button("Guardar Ventas"):
    guardar_datos(df_vent_actualizado, VENT_FILE)
    st.success("Datos de ventas guardados.")

# Mostrar resumen ventas y pagos por pedido
if not df_vent_actualizado.empty:
    total_ventas_por_pedido = df_vent_actualizado.groupby("Pedido")["Total Venta"].sum()
    total_pagado_por_pedido = df_vent_actualizado.groupby("Pedido")["Pagado"].sum()
else:
    total_ventas_por_pedido = pd.Series(dtype=float)
    total_pagado_por_pedido = pd.Series(dtype=float)

resumen_ventas = pd.DataFrame({
    "Total Ventas": total_ventas_por_pedido,
    "Total Pagado": total_pagado_por_pedido
})

st.subheader("Resumen Ventas y Pagos por Pedido")
st.table(resumen_ventas)

# Mostrar totales inversión por pedido (igual que antes)
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

# -- NUEVA SECCIÓN: Clientes con deuda pendiente global --
st.header("Clientes con Deuda Pendiente")

# Calcular saldo pendiente por venta
df_vent_actualizado["Saldo Pendiente"] = df_vent_actualizado["Total Venta"] - df_vent_actualizado["Pagado"]

# Filtrar clientes que tienen saldo pendiente mayor a 0
clientes_deudores = df_vent_actualizado[df_vent_actualizado["Saldo Pendiente"] > 0]

# Agrupar por cliente la suma de saldo pendiente
deuda_por_cliente = clientes_deudores.groupby("Cliente")["Saldo Pendiente"].sum().reset_index()

st.dataframe(deuda_por_cliente)

# Mostrar total global de deuda pendiente
total_deuda = deuda_por_cliente["Saldo Pendiente"].sum()
st.markdown(f"**Total deuda pendiente global:** ${total_deuda:,.2f}")

# Gráficos como antes
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
