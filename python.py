import streamlit as st
from datetime import datetime, timedelta
import csv
import io

# Función para convertir cadena "hh.mm.ss" a timedelta
def convertir_a_timedelta(cadena):
    try:
        horas_str, minutos_str, segundos_str = cadena.split('.')
        horas = int(horas_str)
        minutos = int(minutos_str)
        segundos = int(segundos_str)
        return timedelta(hours=horas, minutes=minutos, seconds=segundos)
    except:
        return None

# Función para calcular horas especiales dentro del rango 20:00 - 22:00
def calcular_horas_especiales(entrada_td, salida_td):
    inicio_especial = timedelta(hours=20)
    fin_especial = timedelta(hours=22)

    if salida_td < entrada_td:
        salida_td += timedelta(days=1)

    inicio_interseccion = max(entrada_td, inicio_especial)
    fin_interseccion = min(salida_td, fin_especial)

    if inicio_interseccion >= fin_interseccion:
        return 0

    horas_especiales = (fin_interseccion - inicio_interseccion).total_seconds() / 3600
    return horas_especiales

st.title("💼 Calculadora de Sueldos (Múltiples Empleados)")

valor_por_hora = st.number_input("Ingrese el valor por hora (Gs):", min_value=0.0, value=11660.0, step=100.0)

registros = []

cantidad_empleados = st.number_input("¿Cuántos empleados desea registrar?", min_value=1, step=1)

for emp_num in range(int(cantidad_empleados)):
    st.subheader(f"🧑 Empleado {emp_num + 1}")

    nombre_empleado = st.text_input(f"Nombre del empleado {emp_num + 1}:", key=f"nombre_{emp_num}")
    if not nombre_empleado.strip():
        st.warning("⚠️ El nombre no puede estar vacío.")
        st.stop()

    dias_trabajados = st.number_input(f"Días trabajados por {nombre_empleado}:", min_value=1, step=1, key=f"dias_{emp_num}")
    fecha_inicial = st.date_input(f"Fecha inicial de trabajo para {nombre_empleado}:", key=f"fecha_{emp_num}")

    registros_empleado = []
    total_horas = 0
    total_sueldo = 0
    total_recargo = 0

    for dia in range(1, int(dias_trabajados) + 1):
        st.markdown(f"**Día {dia}:**")

        entrada_str = st.text_input(f"Hora de ENTRADA (hh.mm.ss) para el día {dia}:", key=f"entrada_{emp_num}_{dia}")
        salida_str = st.text_input(f"Hora de SALIDA (hh.mm.ss) para el día {dia}:", key=f"salida_{emp_num}_{dia}")

        entrada_td = convertir_a_timedelta(entrada_str)
        salida_td = convertir_a_timedelta(salida_str)

        if not entrada_td or not salida_td:
            st.warning("⚠️ Formato de hora incorrecto. Use hh.mm.ss")
            st.stop()

        duracion = salida_td - entrada_td
        if duracion.total_seconds() < 0:
            duracion += timedelta(days=1)

        horas_totales = duracion.total_seconds() / 3600
        horas_especiales = calcular_horas_especiales(entrada_td, salida_td)
        horas_normales = horas_totales - horas_especiales

        sueldo_normal = horas_normales * valor_por_hora
        recargo = horas_especiales * valor_por_hora * 0.30
        sueldo_especial = horas_especiales * valor_por_hora + recargo
        sueldo_dia = sueldo_normal + sueldo_especial

        fecha_dia = fecha_inicial + timedelta(days=dia-1)

        total_horas += horas_totales
        total_sueldo += sueldo_dia
        total_recargo += recargo

        registros_empleado.append({
            'nombre': nombre_empleado,
            'dia': dia,
            'fecha': fecha_dia.strftime('%d/%m/%Y'),
            'entrada': entrada_str,
            'salida': salida_str,
            'horas': round(horas_totales, 2),
            'horas_especiales': round(horas_especiales, 2),
            'recargo': round(recargo, 2),
            'sueldo': round(sueldo_dia, 2),
            'feriado': False
        })

    hubo_feriado = st.selectbox(f"¿Hubo feriado para {nombre_empleado}?", options=['No', 'Sí'], key=f"feriado_{emp_num}")
    if hubo_feriado == 'Sí':
        dia_feriado = st.number_input(f"Ingrese número de día feriado (1 a {dias_trabajados}):", min_value=1, max_value=int(dias_trabajados), key=f"feriado_dia_{emp_num}")
        for reg in registros_empleado:
            if reg['dia'] == dia_feriado:
                sueldo_sin_recargo = reg['sueldo'] - reg['recargo']
                reg['sueldo'] = sueldo_sin_recargo * 2 + reg['recargo']
                reg['feriado'] = True
                total_sueldo += sueldo_sin_recargo

    retiro = st.selectbox(f"¿{nombre_empleado} tuvo retiro/quincena?", options=['No', 'Sí'], key=f"retiro_{emp_num}")
    cobro_quincena = st.number_input("¿Cuánto cobró de quincena? (0 si no):", min_value=0.0, key=f"quincena_{emp_num}") if retiro == 'Sí' else 0.0

    descuento_caja = st.number_input("Descuento por caja (0 si no):", min_value=0.0, key=f"desc_caja_{emp_num}")
    descuento_inventario = st.number_input("Descuento por inventario (0 si no):", min_value=0.0, key=f"desc_inventario_{emp_num}")

    paga_ips = st.selectbox(f"¿{nombre_empleado} paga IPS?", options=['No', 'Sí'], key=f"ips_{emp_num}")
    descuento_ips = total_sueldo * 0.09 if paga_ips == 'Sí' else 0

    sueldo_final = total_sueldo - descuento_ips + cobro_quincena - descuento_caja - descuento_inventario

    registros.extend(registros_empleado)

    st.success(f"✅ Sueldo final de {nombre_empleado}: {sueldo_final:,.2f} Gs.")
    st.markdown("---")

# Reporte General
if registros:
    st.subheader("📊 Reporte General")
    empleados = set(r['nombre'] for r in registros)
    for emp in empleados:
        horas = sum(r['horas'] for r in registros if r['nombre'] == emp)
        sueldo = sum(r['sueldo'] for r in registros if r['nombre'] == emp)
        st.write(f"👤 {emp}: {horas:.2f} horas | {sueldo:,.2f} Gs.")

    # Exportar a CSV
    def convertir_a_csv(data):
        salida = io.StringIO()
        campos = data[0].keys()
        escritor = csv.DictWriter(salida, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(data)
        return salida.getvalue()

    csv_data = convertir_a_csv(registros)
    st.download_button("📥 Descargar Reporte CSV", data=csv_data, file_name="reporte_general.csv", mime="text/csv")
