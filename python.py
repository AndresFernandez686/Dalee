import streamlit as st
from datetime import datetime, timedelta
import csv
import io

def convertir_a_timedelta(cadena):
    try:
        horas_str, minutos_str, segundos_str = cadena.split('.')
        horas = int(horas_str)
        minutos = int(minutos_str)
        segundos = int(segundos_str)
        return timedelta(hours=horas, minutes=minutos, seconds=segundos)
    except:
        return None

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

if 'empleados' not in st.session_state:
    st.session_state.empleados = []

if 'indice' not in st.session_state:
    st.session_state.indice = 0

if 'registros' not in st.session_state:
    st.session_state.registros = []

st.title("Calculadora de Sueldos con Horas Especiales - Múltiples Empleados")

# Función para resetear formulario para nuevo empleado
def reiniciar_form():
    st.session_state.pop("valor_por_hora", None)
    st.session_state.pop("nombre_empleado", None)
    st.session_state.pop("dias_trabajados", None)
    st.session_state.pop("fecha_inicial", None)
    for i in range(50):
        st.session_state.pop(f"entrada_{i}", None)
        st.session_state.pop(f"salida_{i}", None)
    st.session_state.pop("feriado_op", None)
    st.session_state.pop("dia_feriado", None)
    st.session_state.pop("retiro_op", None)
    st.session_state.pop("cobro_quincena", None)
    st.session_state.pop("desc_caja_op", None)
    st.session_state.pop("desc_caja_monto", None)
    st.session_state.pop("desc_inventario_op", None)
    st.session_state.pop("desc_inventario_monto", None)
    st.session_state.pop("paga_ips_op", None)

# Paso 1: Datos generales del empleado
with st.form("form_datos_generales"):
    valor_por_hora_input = st.text_input("Valor por hora (Enter para 11.660 Gs):", key="valor_por_hora")
    nombre_empleado = st.text_input("Nombre del empleado:", key="nombre_empleado")
    dias_trabajados_input = st.text_input("Días trabajados:", key="dias_trabajados")
    fecha_inicial_str = st.text_input("Fecha inicial (dd/mm/aa):", key="fecha_inicial")
    enviar_generales = st.form_submit_button("Siguiente")

if enviar_generales:
    errores = []
    valor_por_hora = 11660.0
    if valor_por_hora_input.strip() != "":
        try:
            valor_por_hora = float(valor_por_hora_input)
        except:
            errores.append("Valor por hora inválido.")
    if nombre_empleado.strip() == "" or nombre_empleado.isdigit():
        errores.append("Nombre de empleado inválido.")
    if not dias_trabajados_input.isdigit() or int(dias_trabajados_input) <= 0:
        errores.append("Días trabajados inválido.")
    try:
        fecha_inicial = datetime.strptime(fecha_inicial_str, "%d/%m/%y").date()
    except:
        errores.append("Fecha inicial inválida.")
    if errores:
        for e in errores:
            st.error(e)
        st.stop()
    dias_trabajados = int(dias_trabajados_input)
    st.session_state.empleados.append({
        "valor_por_hora": valor_por_hora,
        "nombre_empleado": nombre_empleado,
        "dias_trabajados": dias_trabajados,
        "fecha_inicial": fecha_inicial,
        "registro_empleado": [],
        "total_horas": 0,
        "total_sueldo": 0,
        "total_recargo": 0,
    })
    st.session_state.indice = len(st.session_state.empleados) - 1
    reiniciar_form()
    st.experimental_rerun()

# Si no hay empleados cargados, mostramos solo el formulario de datos generales
if len(st.session_state.empleados) == 0:
    st.info("Ingrese datos del primer empleado para comenzar.")
    st.stop()

# Obtenemos el empleado actual
empleado_actual = st.session_state.empleados[st.session_state.indice]

st.header(f"Empleado {st.session_state.indice + 1} de {len(st.session_state.empleados)}: {empleado_actual['nombre_empleado']}")

# Formulario para cargar horas por día
with st.form("form_horas"):
    entradas = []
    salidas = []
    for dia in range(1, empleado_actual["dias_trabajados"] + 1):
        fecha_dia = empleado_actual["fecha_inicial"] + timedelta(days=dia - 1)
        st.markdown(f"**Día {dia} ({fecha_dia.strftime('%d/%m/%y')})**")
        entrada_str = st.text_input(f"Hora ENTRADA (hh.mm.ss) día {dia}:", key=f"entrada_{dia}")
        salida_str = st.text_input(f"Hora SALIDA (hh.mm.ss) día {dia}:", key=f"salida_{dia}")
        entradas.append(entrada_str)
        salidas.append(salida_str)
    enviar_horas = st.form_submit_button("Calcular sueldo")

if enviar_horas:
    errores_horas = []
    for i in range(empleado_actual["dias_trabajados"]):
        if convertir_a_timedelta(entradas[i]) is None or convertir_a_timedelta(salidas[i]) is None:
            errores_horas.append(f"Horas inválidas en día {i+1}.")
    if errores_horas:
        for e in errores_horas:
            st.error(e)
        st.stop()

    # Reset registros para este empleado
    empleado_actual["registro_empleado"] = []
    empleado_actual["total_horas"] = 0
    empleado_actual["total_sueldo"] = 0
    empleado_actual["total_recargo"] = 0

    for dia in range(empleado_actual["dias_trabajados"]):
        fecha_dia = empleado_actual["fecha_inicial"] + timedelta(days=dia)
        entrada_td = convertir_a_timedelta(entradas[dia])
        salida_td = convertir_a_timedelta(salidas[dia])

        duracion = salida_td - entrada_td
        if duracion.total_seconds() < 0:
            duracion += timedelta(days=1)

        horas_totales = duracion.total_seconds() / 3600
        horas_especiales = calcular_horas_especiales(entrada_td, salida_td)
        horas_normales = horas_totales - horas_especiales

        sueldo_normal = horas_normales * empleado_actual["valor_por_hora"]
        recargo = horas_especiales * empleado_actual["valor_por_hora"] * 0.30
        sueldo_especial = horas_especiales * empleado_actual["valor_por_hora"] + recargo
        sueldo_dia = sueldo_normal + sueldo_especial

        empleado_actual["total_horas"] += horas_totales
        empleado_actual["total_sueldo"] += sueldo_dia
        empleado_actual["total_recargo"] += recargo

        empleado_actual["registro_empleado"].append({
            'nombre': empleado_actual['nombre_empleado'],
            'dia': dia+1,
            'fecha': fecha_dia.strftime('%d/%m/%y'),
            'entrada': entradas[dia],
            'salida': salidas[dia],
            'horas': horas_totales,
            'horas_especiales': horas_especiales,
            'sueldo': sueldo_dia,
            'recargo': recargo,
            'feriado': False
        })

    st.success(f"Sueldo calculado para {empleado_actual['nombre_empleado']}.")

    # Formulario para feriado, retiro, descuentos e IPS
    with st.form("form_descuentos"):
        feriado_op = st.radio(f"¿Hubo feriado para {empleado_actual['nombre_empleado']}?", options=["No", "Sí"], key="feriado_op")
        dia_feriado = None
        if feriado_op == "Sí":
            dia_feriado = st.number_input(f"Ingrese el día feriado (1-{empleado_actual['dias_trabajados']}):", min_value=1, max_value=empleado_actual["dias_trabajados"], step=1, key="dia_feriado")

        retiro_op = st.radio("¿Tuvo retiro antes/después de quincena?", options=["No", "Sí"], key="retiro_op")
        cobro_quincena = 0
        if retiro_op == "Sí":
            cobro_quincena = st.number_input("¿Cuánto cobró de quincena?", min_value=0.0, step=0.01, key="cobro_quincena")

        desc_caja_op = st.radio("¿Tuvo descuento por caja?", options=["No", "Sí"], key="desc_caja_op")
        descuento_caja = 0
        if desc_caja_op == "Sí":
            descuento_caja = st.number_input("Monto descuento por caja:", min_value=0.0, step=0.01, key="desc_caja_monto")

        desc_inventario_op = st.radio("¿Tuvo descuento por inventario?", options=["No", "Sí"], key="desc_inventario_op")
        descuento_inventario = 0
        if desc_inventario_op == "Sí":
            descuento_inventario = st.number_input("Monto descuento por inventario:", min_value=0.0, step=0.01, key="desc_inventario_monto")

        paga_ips_op = st.radio(f"¿{empleado_actual['nombre_empleado']} paga IPS?", options=["No", "Sí"], key="paga_ips_op")

        enviar_descuentos = st.form_submit_button("Calcular sueldo final")

    if enviar_descuentos:
        if feriado_op == "Sí" and dia_feriado is not None:
            for reg in empleado_actual["registro_empleado"]:
                if reg['dia'] == dia_feriado:
                    reg['feriado'] = True
                    sueldo_sin_recargo = reg['sueldo'] - reg['recargo']
                    reg['sueldo'] = sueldo_sin_recargo * 2 + reg['recargo']
                    empleado_actual["total_sueldo"] += sueldo_sin_recargo

        if paga_ips_op == "Sí":
            descuento_ips = empleado_actual["total_sueldo"] * 0.09
        else:
            descuento_ips = 0

        sueldo_definitivo = empleado_actual["total_sueldo"] - descuento_ips + cobro_quincena - descuento_caja - descuento_inventario
        empleado_actual["sueldo_final"] = sueldo_definitivo

        st.success(f"👉 SUELDO FINAL DE {empleado_actual['nombre_empleado']}: {sueldo_definitivo:.2f} Gs.")

        # Agregar registros a la lista global para reporte general
        st.session_state.registros.extend(empleado_actual["registro_empleado"])

        # Botón para agregar otro empleado
        if st.button("Agregar otro empleado"):
            reiniciar_form()
            st.experimental_rerun()

        # Botón para mostrar reporte general y exportar CSV
        if st.button("Mostrar reporte general y exportar CSV"):
            st.subheader("======== REPORTE GENERAL ========")
            empleados_unicos = set([reg['nombre'] for reg in st.session_state.registros])
            for empleado in empleados_unicos:
                horas = sum(reg['horas'] for reg in st.session_state.registros if reg['nombre'] == empleado)
                sueldo = sum(reg['sueldo'] for reg in st.session_state.registros if reg['nombre'] == empleado)
                st.write(f"{empleado}: {horas:.2f} horas | {sueldo:.2f} Gs.")
            st.write("=================================")

            # Exportar CSV general
            def convertir_a_csv(data):
                salida = io.StringIO()
                campos = data[0].keys()
                escritor = csv.DictWriter(salida, fieldnames=campos)
                escritor.writeheader()
                escritor.writerows(data)
                return salida.getvalue()

            if st.session_state.registros:
                csv_data = convertir_a_csv(st.session_state.registros)
                st.download_button(
                    label="📥 Descargar reporte general CSV",
                    data=csv_data,
                    file_name="reporte_general.csv",
                    mime="text/csv"
                )

