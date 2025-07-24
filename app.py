import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Arroz con Leche - Gestión por Pedido", layout="wide")

st.title("Gestión y Ventas - Arroz con Leche")

# --- SECCIÓN 1: Registro de Inversiones por Pedido ---
st.header("Inversiones por Pedido")

# Tabla editable para registrar inversiones con pedido, fecha, concepto y valor
inv_data = st.data_editor(
    pd.DataFrame({
        "Pedido": ["Pedido 1", "Pedido 1", "Pedido 2"],
        "Fecha": ["2025-07-20", "2025-07-20", "2025-07-22"],
        "Concepto": ["Arroz", "Leche Condensada", "Canela"],
        "Valor": [5000, 3200, 2000]
    }),
    num_rows="dynamic",
    key="inv"
)

# Total invertido por pedido (agrupando)
total_inv_por_pedido = inv_data.groupby("Pedido")["Valor"].sum()

# Mostrar totales por pedido
st.subheader("Total Inversión por Pedido")
st.table(total_inv_por_pedido)

# Gráfico barras: inversión por pedido
fig_inv, ax_inv = plt.subplots()
ax_inv.bar(total_inv_por_pedido.index, total_inv_por_pedido.values, color="#5A9")
ax_inv.set_ylabel("Valor ($)")
ax_inv.set_title("Inversión Total por Pedido")
st.pyplot(fig_inv)

# --- SECCIÓN 2: Registro de Ventas por Pedido ---
st.header("Ventas por Pedido")

# Tabla editable para registrar ventas con pedido, fecha, cliente, unidades, precio unitario, pagado
ventas_data = st.data_editor(
    pd.DataFrame({
        "Pedido": ["Pedido 1", "Pedido 1", "Pedido 2"],
        "Fecha": ["2025-07-25", "2025-07-26", "2025-07-28"],
        "Cliente": ["Andrea", "Carlos", "Ana"],
        "Unidades": [10, 5, 8],
        "Precio Unitario": [1800, 1800, 2500],
        "Pagado": [18000, 9000, 20000]
    }),
    num_rows="dynamic",
    key="ventas"
)

# Calcular total venta (Unidades * Precio Unitario)
ventas_data["Total Venta"] = ventas_data["Unidades"] * ventas_data["Precio Unitario"]

# Sumar total ventas por pedido
total_ventas_por_pedido = ventas_data.groupby("Pedido")["Total Venta"].sum()

# Sumar total pagado por pedido
total_pagado_por_pedido = ventas_data.groupby("Pedido")["Pagado"].sum()

# Mostrar tabla resumen ventas y pagos por pedido
resumen_ventas = pd.DataFrame({
    "Total Ventas": total_ventas_por_pedido,
    "Total Pagado": total_pagado_por_pedido
})

st.subheader("Resumen Ventas y Pagos por Pedido")
st.table(resumen_ventas)

# Gráfico barras: total ventas por pedido
fig_ventas, ax_ventas = plt.subplots()
ax_ventas.bar(total_ventas_por_pedido.index, total_ventas_por_pedido.values, color="#69C")
ax_ventas.set_ylabel("Valor ($)")
ax_ventas.set_title("Ventas Totales por Pedido")
st.pyplot(fig_ventas)

# --- SECCIÓN 3: Cálculo de Utilidad Neta por Pedido ---
st.header("Utilidad Neta por Pedido")

# Combinar inversión y ventas en un solo DataFrame para cálculo de utilidad
df_utilidad = pd.DataFrame({
    "Inversión": total_inv_por_pedido,
    "Ingreso por Ventas": total_ventas_por_pedido
})

# Calcular utilidad neta = Ingreso por ventas - inversión (puede ser negativa si hay pérdidas)
df_utilidad["Utilidad Neta"] = df_utilidad["Ingreso por Ventas"] - df_utilidad["Inversión"]

# Mostrar la utilidad neta por pedido
st.table(df_utilidad)

# Gráfico líneas: utilidad neta por pedido
fig_utilidad, ax_utilidad = plt.subplots()
ax_utilidad.bar(df_utilidad.index, df_utilidad["Utilidad Neta"], color=["#4CAF50" if u >= 0 else "#F44336" for u in df_utilidad["Utilidad Neta"]])
ax_utilidad.set_ylabel("Utilidad Neta ($)")
ax_utilidad.set_title("Utilidad Neta por Pedido")
st.pyplot(fig_utilidad)

# Mensaje final para el usuario
st.success("Puedes editar los datos de inversión y ventas por pedido. Todos los cálculos y gráficos se actualizan automáticamente.")

