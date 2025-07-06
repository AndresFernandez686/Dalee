import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# Función para calcular horas especiales
def calcular_horas_especiales(entrada_dt, salida_dt):
    inicio_especial = entrada_dt.replace(hour=20, minute=0, second=0)
    fin_especial = entrada_dt.replace(hour=22, minute=0, second=0)

    if salida_dt < entrada_dt:
        salida_dt += timedelta(days=1)

    inicio_interseccion = max(entrada_dt, inicio_especial)
    fin_interseccion = min(salida_dt, fin_especial)

    if inicio_interseccion >= fin_interseccion:
        return 0

    return (fin_interseccion - inicio_interseccion).total_seconds() / 3600

st.title("💼 Calculadora de Sueldos - Múltiples Empleados")

valor_por_hora = st.number_input("💲 Ingrese el valor por hora:", min_value=0.0, value=11660.0)

num_empleados = st.number_input("👥 ¿Cuántos empleados desea registrar?", min_value=1, step=1)

registros = []

for i in range(int(num_empleados)):
    st.header(f"Empleado {i+1}")
    nombre = st.text_input(f"Nombre del empleado {i+1}:", key=f"nombre_{i}")
    dias_trabajados = st.number_input(f"Días trabajados por {nombre}:", min_value=1, step=1, key=f"dias_{i}")
    fecha_inicial = st.date_input(f"Fecha inicial para {nombre}:", key=f"fecha_{i}")

    total_horas = 0
    total_sueldo = 0
    detalle = []

    for d in range(int(dias_trabajados)):
        st.subheader(f"Día {d+1} - {fecha_inicial + timedelta(days=d)}")
        entrada = st.time_input(f"Hora de entrada:", key=f"entrada_{i}_{d}")
        salida = st.time_input(f"Hora de salida:", key=f"salida_{i}_{d}")

        entrada_dt = datetime.combine(datetime.today(), entrada)
        salida_dt = datetime.combine(datetime.today(), salida)
        if salida_dt < entrada_dt:
            salida_dt += timedelta(days=1)

        duracion = salida_dt - entrada_dt
        horas_totales = duracion.total_seconds() / 3600
        horas_especiales = calcular_horas_especiales(entrada_dt, salida_dt)
        horas_normales = horas_totales - horas_especiales

        sueldo_normal = horas_normales * valor_por_hora
        recargo = horas_especiales * valor_por_hora * 0.30
        sueldo_especial = horas_especiales * valor_por_hora + recargo
        sueldo_dia = sueldo_normal + sueldo_especial

        detalle.append({
            "Fecha": (fecha_inicial + timedelta(days=d)).strftime('%d/%m/%Y'),
            "Entrada": entrada.strftime('%H:%M:%S'),
            "Salida": salida.strftime('%H:%M:%S'),
            "Horas": round(horas_totales, 2),
            "Horas Especiales": round(horas_especiales, 2),
            "Sueldo": round(sueldo_dia, 2)
        })

        total_horas += horas_totales
        total_sueldo += sueldo_dia

    paga_ips = st.radio(f"¿{nombre} paga IPS?", ["Sí", "No"], key=f"ips_{i}")
    ips = total_sueldo * 0.09 if paga_ips == "Sí" else 0

    retiro = st.radio(f"¿{nombre} tuvo retiro de quincena?", ["Sí", "No"], key=f"retiro_{i}")
    cobro_quincena = st.number_input("Monto de retiro de quincena:", min_value=0.0, value=0.0, key=f"quincena_{i}") if retiro == "Sí" else 0

    descuento_caja = st.number_input("Descuento por caja:", min_value=0.0, value=0.0, key=f"desc_caja_{i}")
    descuento_inventario = st.number_input("Descuento por inventario:", min_value=0.0, value=0.0, key=f"desc_inv_{i}")

    sueldo_final = total_sueldo - ips + cobro_quincena - descuento_caja - descuento_inventario

    st.success(f"✅ Sueldo total de {nombre}: {round(sueldo_final, 2)} Gs.")
    st.info(f"Total horas trabajadas: {round(total_horas, 2)} hs.")

    df = pd.DataFrame(detalle)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar resumen CSV", csv, f"{nombre}_reporte.csv", "text/csv")

    registros.append({"Nombre": nombre, "Horas Totales": round(total_horas, 2), "Sueldo Total": round(sueldo_final, 2)})

# Reporte General
if registros:
    st.header("📊 Reporte General")
    df_general = pd.DataFrame(registros)
    st.dataframe(df_general)
    csv_general = df_general.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte General CSV", csv_general, "reporte_general.csv", "text/csv")
