import streamlit as st
from datetime import datetime, timedelta
import csv
import io

# Función para convertir cadena "hh.mm.ss" a timedelta
def convertir_a_timedelta(cadena):
    horas_str, minutos_str, segundos_str = cadena.split('.')
    horas = int(horas_str)
    minutos = int(minutos_str)
    segundos = int(segundos_str)
    return timedelta(hours=horas, minutes=minutos, seconds=segundos)

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

# Título
st.title("Calculadora de Sueldos con Horas Especiales")

# Validar valor por hora
while True:
    valor_por_hora_input = st.text_input("Ingrese el valor por hora (Enter para usar 11.660 Gs o 'fin' para salir):", key="valor_hora")
    if valor_por_hora_input.lower() == 'fin':
        st.stop()
    if valor_por_hora_input == '':
        valor_por_hora = 11.660
        break
    try:
        valor_por_hora = float(valor_por_hora_input)
        break
    except:
        st.warning("⚠️ Valor no válido. Ingrese un número válido o 'fin'.")

registros = []

while True:
    # Nombre empleado
    nombre_empleado = st.text_input("Ingrese el nombre del empleado (o 'fin' para terminar):", key="nombre_empleado")
    if nombre_empleado.lower() == 'fin':
        st.stop()
    if nombre_empleado == '' or nombre_empleado.isdigit():
        st.warning("⚠️ Nombre inválido. Ingrese un nombre correcto o 'fin'.")
        continue

    # Días trabajados
    dias_trabajados_input = st.text_input(f"Ingrese cuántos días trabajó {nombre_empleado} (o 'fin' para salir):", key="dias_trabajados")
    if dias_trabajados_input.lower() == 'fin':
        st.stop()
    if not (dias_trabajados_input.isdigit() and int(dias_trabajados_input) > 0):
        st.warning("⚠️ Ingrese un número válido o 'fin'.")
        continue
    dias_trabajados = int(dias_trabajados_input)

    # Fecha inicial
    fecha_inicial_str = st.text_input(f"Ingrese la fecha inicial (dd/mm/aa) para {nombre_empleado} (o 'fin'):", key="fecha_inicial")
    if fecha_inicial_str.lower() == 'fin':
        st.stop()
    try:
        fecha_inicial = datetime.strptime(fecha_inicial_str, "%d/%m/%y").date()
    except:
        st.warning("⚠️ Fecha incorrecta. Intente nuevamente o 'fin'.")
        continue

    registros_empleado = []
    total_horas_empleado = 0
    total_sueldo_empleado = 0
    total_recargo_horas_especiales = 0

    for dia in range(1, dias_trabajados + 1):
        fecha_dia = fecha_inicial + timedelta(days=dia-1)
        st.write(f"Día {dia} ({fecha_dia.strftime('%d/%m/%y')}) para {nombre_empleado}")

        # Entrada
        entrada_str = st.text_input(f"Ingrese la hora de ENTRADA (hh.mm.ss) para día {dia} o 'fin':", key=f"entrada_{dia}")
        if entrada_str.lower() == 'fin':
            st.stop()
        try:
            entrada = convertir_a_timedelta(entrada_str)
        except:
            st.warning("⚠️ Hora inválida. Intente nuevamente o 'fin'.")
            break

        # Salida
        salida_str = st.text_input(f"Ingrese la hora de SALIDA (hh.mm.ss) para día {dia} o 'fin':", key=f"salida_{dia}")
        if salida_str.lower() == 'fin':
            st.stop()
        try:
            salida = convertir_a_timedelta(salida_str)
        except:
            st.warning("⚠️ Hora inválida. Intente nuevamente o 'fin'.")
            break

        duracion = salida - entrada
        if duracion.total_seconds() < 0:
            duracion += timedelta(days=1)

        horas_totales = duracion.total_seconds() / 3600
        horas_especiales = calcular_horas_especiales(entrada, salida)
        horas_normales = horas_totales - horas_especiales

        sueldo_normal = horas_normales * valor_por_hora
        recargo = horas_especiales * valor_por_hora * 0.30
        sueldo_especial = horas_especiales * valor_por_hora + recargo
        sueldo_dia = sueldo_normal + sueldo_especial

        total_horas_empleado += horas_totales
        total_sueldo_empleado += sueldo_dia
        total_recargo_horas_especiales += recargo

        registros_empleado.append({
            'nombre': nombre_empleado,
            'dia': dia,
            'fecha': fecha_dia.strftime('%d/%m/%y'),
            'entrada': entrada_str,
            'salida': salida_str,
            'horas': horas_totales,
            'horas_especiales': horas_especiales,
            'sueldo': sueldo_dia,
            'recargo': recargo,
            'feriado': False
        })

    # Feriado
    hubo_feriado = st.text_input(f"¿Hubo feriado para {nombre_empleado}? (s/n o 'fin'):", key="feriado")
    if hubo_feriado.lower() == 'fin':
        st.stop()
    if hubo_feriado.lower() not in ['s', 'n']:
        st.warning("⚠️ Respuesta inválida.")
    if hubo_feriado.lower() == 's':
        dia_feriado_input = st.text_input(f"Ingrese el número de día feriado (1 a {dias_trabajados}) o 'fin':", key="dia_feriado")
        if dia_feriado_input.lower() == 'fin':
            st.stop()
        if not (dia_feriado_input.isdigit() and 1 <= int(dia_feriado_input) <= dias_trabajados):
            st.warning("⚠️ Número de día inválido.")
        dia_feriado = int(dia_feriado_input)

        for reg in registros_empleado:
            if reg['dia'] == dia_feriado:
                reg['feriado'] = True
                sueldo_sin_recargo = reg['sueldo'] - reg['recargo']
                reg['sueldo'] = sueldo_sin_recargo * 2 + reg['recargo']
                total_sueldo_empleado += sueldo_sin_recargo

    # Retiro
    retiro = st.text_input("¿Tuvo retiro antes/después de quincena? (s/n o 'fin'):", key="retiro")
    if retiro.lower() == 'fin':
        st.stop()
    if retiro.lower() not in ['s', 'n']:
        st.warning("⚠️ Respuesta inválida.")
    if retiro.lower() == 's':
        cobro_quincena_input = st.text_input("¿Cuánto cobró de quincena? (o 'fin'):", key="cobro_quincena")
        if cobro_quincena_input.lower() == 'fin':
            st.stop()
        try:
            cobro_quincena = float(cobro_quincena_input)
        except:
            st.warning("⚠️ Monto inválido.")
            cobro_quincena = 0
    else:
        cobro_quincena = 0

    # Descuento caja
    descuento_caja = 0
    respuesta_desc_caja = st.text_input("¿Tuvo descuento por caja? (s/n o 'fin'):", key="desc_caja")
    if respuesta_desc_caja.lower() == 'fin':
        st.stop()
    if respuesta_desc_caja.lower() == 's':
        valor_desc_caja = st.text_input("Ingrese monto descuento por caja:", key="valor_desc_caja")
        try:
            descuento_caja = float(valor_desc_caja)
        except:
            st.warning("⚠️ Valor inválido para descuento caja.")
    elif respuesta_desc_caja.lower() != 'n':
        st.warning("⚠️ Respuesta inválida para descuento caja.")

    # Descuento inventario
    descuento_inventario = 0
    respuesta_desc_inventario = st.text_input("¿Tuvo descuento por inventario? (s/n o 'fin'):", key="desc_inventario")
    if respuesta_desc_inventario.lower() == 'fin':
        st.stop()
    if respuesta_desc_inventario.lower() == 's':
        valor_desc_inventario = st.text_input("Ingrese monto descuento por inventario:", key="valor_desc_inventario")
        try:
            descuento_inventario = float(valor_desc_inventario)
        except:
            st.warning("⚠️ Valor inválido para descuento inventario.")
    elif respuesta_desc_inventario.lower() != 'n':
        st.warning("⚠️ Respuesta inválida para descuento inventario.")

    # IPS
    paga_ips = st.text_input(f"¿{nombre_empleado} paga IPS? (s/n o 'fin'):", key="paga_ips")
    if paga_ips.lower() == 'fin':
        st.stop()
    if paga_ips.lower() not in ['s', 'n']:
        st.warning("⚠️ Respuesta inválida para IPS.")

    if paga_ips.lower() == 's':
        descuento_ips = total_sueldo_empleado * 0.09
        sueldo_definitivo = total_sueldo_empleado - descuento_ips + cobro_quincena - descuento_caja - descuento_inventario
    else:
        sueldo_definitivo = total_sueldo_empleado + cobro_quincena - descuento_caja - descuento_inventario

    registros.extend(registros_empleado)

    st.success(f"👉 SUELDO FINAL DE {nombre_empleado}: {sueldo_definitivo:.2f} Gs.")

    # Mostrar reporte detallado
    st.subheader("Resumen diario:")
    for reg in registros_empleado:
        st.write(reg)

    # Función para convertir registros a CSV
    def convertir_a_csv(data):
        salida = io.StringIO()
        campos = data[0].keys()
        escritor = csv.DictWriter(salida, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(data)
        return salida.getvalue()

    if registros_empleado:
        csv_data = convertir_a_csv(registros_empleado)
        st.download_button(
            label="📥 Descargar reporte CSV",
            data=csv_data,
            file_name=f"reporte_{nombre_empleado}.csv",
            mime="text/csv",
        )

    break  # Para que no entre en ciclo infinito (puedes modificar para múltiples empleados)

# Reporte general
st.subheader("======== REPORTE GENERAL ========")
empleados_unicos = set([reg['nombre'] for reg in registros])
for empleado in empleados_unicos:
    horas = sum(reg['horas'] for reg in registros if reg['nombre'] == empleado)
    sueldo = sum(reg['sueldo'] for reg in registros if reg['nombre'] == empleado)
    st.write(f"{empleado}: {horas:.2f} horas | {sueldo:.2f} Gs.")
st.write("=================================")
