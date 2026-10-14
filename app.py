import streamlit as st
import pandas as pd
import json
import io

# Configuración de la página
st.set_page_config(
    page_title="Snowdon Towers - Control Lean Construction",
    page_icon="🏗️",
    layout="wide"
)

# Estilos CSS (Tonos Verde Oliva y diseño institucional)
st.markdown("""
    <style>
    .main { background-color: #F7F9F5; }
    h1, h2, h3 { color: #3A4F29; }
    .stButton>button { background-color: #556B2F; color: white; border-radius: 5px; font-weight: bold; }
    .stButton>button:hover { background-color: #3F5222; color: white; }
    </style>
""", unsafe_allow_html=True)

# ==================== INICIALIZACIÓN DE ESTADO (PERSISTENCIA Y DATOS BASE) ====================
if "constraints_df" not in st.session_state:
    st.session_state["constraints_df"] = pd.DataFrame([
        {"ID": "C-01", "Tarea": "Encofrado L4 S2", "Tipo": "Trabajo previo", "Descripción": "177 m² de encofrado de L4 S2 aún sin terminar (pendiente verificar)", "Responsable": "Residente de Obra", "FechaReq": "2026-09-25", "Estado": "Pendiente"},
        {"ID": "C-02", "Tarea": "Instalaciones L4", "Tipo": "Diseño o información", "Descripción": "RFI-108 ubicación de pases sin respuesta de interventoría/diseño", "Responsable": "Director Técnico", "FechaReq": "2026-09-26", "Estado": "Pendiente"},
        {"ID": "C-03", "Tarea": "Acero L5 S1", "Tipo": "Materiales", "Descripción": "Suministro de acero de refuerzo #4 y #6", "Responsable": "Logística / Proveedor", "FechaReq": "2026-10-02", "Estado": "Liberada"},
        {"ID": "C-04", "Tarea": "Vaciado L5 S1", "Tipo": "Equipos", "Descripción": "Disponibilidad de bomba estacionaria y torre grúa", "Responsable": "Maquinaria", "FechaReq": "2026-10-05", "Estado": "Pendiente"},
        {"ID": "C-05", "Tarea": "Encofrado L5 S2", "Tipo": "Liberaciones o permisos", "Descripción": "Liberación de interventoría de armado previo", "Responsable": "Interventoría", "FechaReq": "2026-10-08", "Estado": "Pendiente"},
        {"ID": "C-06", "Tarea": "Muro cortina L2", "Tipo": "Diseño o información", "Descripción": "Aprobación de planos de taller fachada", "Responsable": "Arquitectura", "FechaReq": "2026-09-20", "Estado": "Vencida"},
        {"ID": "C-07", "Tarea": "Acero L5 S2", "Tipo": "Materiales", "Descripción": "Despacho de malla electrosoldada", "Responsable": "Compras", "FechaReq": "2026-10-10", "Estado": "Pendiente"},
        {"ID": "C-08", "Tarea": "Concreto L5 S1", "Tipo": "Mano de obra", "Descripción": "Cuadrilla de vaciado confirmada", "Responsable": "Contratista", "FechaReq": "2026-10-04", "Estado": "Liberada"},
        {"ID": "C-09", "Tarea": "Curado L4", "Tipo": "Liberaciones o permisos", "Descripción": "Protocolo de resistencia a 7 días", "Responsable": "Calidad", "FechaReq": "2026-09-28", "Estado": "Liberada"},
        {"ID": "C-10", "Tarea": "Preparación L6 S1", "Tipo": "Trabajo previo", "Descripción": "Replanteo topográfico y ejes", "Responsable": "Topografía", "FechaReq": "2026-10-12", "Estado": "Pendiente"}
    ])

if "lookahead_df" not in st.session_state:
    st.session_state["lookahead_df"] = pd.DataFrame([
        {"Semana": "S37", "FechaInicio": "2026-09-28", "Tarea": "Encofrado L4 S2 (reproceso/cierre)", "Nivel": "L4", "Sector": "Sector 2", "Cuadrilla": "Cuadrilla Encofrado A", "RestriccionesPendientes": "Sí (C-01)"},
        {"Semana": "S37", "FechaInicio": "2026-09-28", "Tarea": "Acero L5 S1", "Nivel": "L5", "Sector": "Sector 1", "Cuadrilla": "Cuadrilla Acero B", "RestriccionesPendientes": "No"},
        {"Semana": "S38", "FechaInicio": "2026-10-05", "Tarea": "Vaciado L5 S1", "Nivel": "L5", "Sector": "Sector 1", "Cuadrilla": "Cuadrilla Concreto", "RestriccionesPendientes": "Sí (C-04)"},
        {"Semana": "S39", "FechaInicio": "2026-10-12", "Tarea": "Encofrado L5 S2", "Nivel": "L5", "Sector": "Sector 2", "Cuadrilla": "Cuadrilla Encofrado A", "RestriccionesPendientes": "Sí (C-05)"},
        {"Semana": "S40", "FechaInicio": "2026-10-19", "Tarea": "Acero L5 S2", "Nivel": "L5", "Sector": "Sector 2", "Cuadrilla": "Cuadrilla Acero B", "RestriccionesPendientes": "Sí (C-07)"},
        {"Semana": "S41", "FechaInicio": "2026-10-26", "Tarea": "Vaciado L5 S2", "Nivel": "L5", "Sector": "Sector 2", "Cuadrilla": "Cuadrilla Concreto", "RestriccionesPendientes": "No"},
        {"Semana": "S42", "FechaInicio": "2026-11-02", "Tarea": "Replanteo y Encofrado L6 S1", "Nivel": "L6", "Sector": "Sector 1", "Cuadrilla": "Cuadrilla Encofrado A", "RestriccionesPendientes": "Sí (C-10)"}
    ])

if "commitments_df" not in st.session_state:
    st.session_state["commitments_df"] = pd.DataFrame(columns=[
        "ID", "Semana", "Tarea", "NivelSector", "Cuadrilla", "CantidadUnidad", "FechaComp", "RestriccionesLib", "CapacidadVerif", "EstadoEval", "CausaIncumplimiento", "DetalleCausa"
    ])

# ==================== BARRA LATERAL ====================
with st.sidebar:
    st.markdown("### 🏢 CMC servicios sas")
    st.markdown("**Consultoría y Gestión Lean Construction**")
    st.markdown("---")
    st.markdown("👩‍💻 **Analista:**")
    st.markdown("*Arq. Catalina Moreno Carvajal*")
    st.markdown("---")
    st.markdown("🏗️ **Proyecto Académico:**")
    st.markdown("**Snowdon Towers (Bogotá)**")
    st.markdown("""
    * *Uso mixto* (Sótano, L1 comercial, M1, L2-L5 típicos, R2, Parapeto).
    * *Estructura:* Concreto reforzado aporticado.
    * *Fachada:* Muro cortina.
    """)
    st.markdown("---")
    st.info("ℹ️ **Nota de Persistencia:** Los datos se guardan temporalmente en la sesión (`st.session_state`). Use la sección final para exportar/importar respaldos en JSON.")

# ==================== NAVEGACIÓN PRINCIPAL ====================
st.title("🏗️ Snowdon Towers - Sistema de Gestión Lean & Last Planner")
st.markdown("### Plataforma de Control de Ciclo de Losa, Productividad y Planificación Semanal")
st.divider()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. Análisis Ciclo & Desperdicios", 
    "2. Productividad & Economía", 
    "3. Lookahead (S37-S42)", 
    "4. Restricciones", 
    "5. Plan Semanal & PPC", 
    "6. Respaldo de Datos"
])

# ==================== TAB 1: CICLO Y DESPERDICIOS ====================
with tab1:
    st.header("1. Análisis del Ciclo de Losa (Entregable 1 - Caso Base Anexo D)")
    st.markdown("Comparativa entre el caso de prueba estándar y el registro operativo en campo.")
    
    # Datos fijos Anexo D
    va_d = 51.0
    nnv_d = 34.0
    desp_d = 26.0
    esperas_d = 23.0
    total_d = 111.0
    ef_d = (va_d / total_d) * 100
    p_desp_d = (desp_d / total_d) * 100
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Ciclo Total", f"{total_d} h")
    c2.metric("Agrega Valor (VA)", f"{va_d} h", f"{va_d/total_d*100:.1f}%")
    c3.metric("Necesarias Sin Valor", f"{nnv_d} h", f"{nnv_d/total_d*100:.1f}%")
    c4.metric("Desperdicios", f"{desp_d} h", f"{p_desp_d:.1f}%")
    c5.metric("Eficiencia del Ciclo", f"{ef_d:.1f}%")
    
    st.markdown("---")
    st.subheader("Desglose del Caso Base (Anexo D)")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        * **Actividades que Agrega Valor (51 h):**
          * Encofrado: 22 h
          * Acero: 18 h
          * Instalaciones embebidas: 6 h
          * Vaciado: 5 h
        * **Actividades Necesarias sin Valor - NNV (34 h):**
          * Transporte de formaleta: 6 h
          * Inspección: 4 h
          * Curado: 24 h
        """)
    with col_b:
        st.markdown("""
        * **Desperdicios / Esperas (26 h total / 23 h en 3 esperas):**
          * Espera de formaleta: 10 h
          * Espera de acero: 8 h
          * Espera de concreto: 5 h
          * Reproceso (niveles): 3 h
        """)
        
    st.markdown("---")
    st.subheader("🚨 Ranking de Desperdicios Registrados")
    df_ranking = pd.DataFrame({
        "Desperdicio registrado": [
            "Espera por liberación de formaleta",
            "Espera por entrega de acero",
            "Espera por programación de concreto",
            "Reproceso: corrección de niveles"
        ],
        "Horas": [10.0, 8.0, 5.0, 3.0],
        "Impacto en Ciclo (%)": ["9.0%", "7.2%", "4.5%", "2.7%"]
    })
    st.dataframe(df_ranking, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🎯 Meta Propuesta: Reducción de Esperas")
    st.markdown("Si se logra reducir las esperas de **23 h a 8 h** (manteniendo las demás actividades estables):")
    
    nuevo_esperas = 8.0
    nuevo_desp = 3.0 + nuevo_esperas # 11 h
    nuevo_total = va_d + nnv_d + nuevo_desp # 51 + 34 + 11 = 96 h
    nueva_ef = (va_d / nuevo_total) * 100
    
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Ciclo Proyectado", f"{nuevo_total:.1f} h", delta="-15.0 h")
    mc2.metric("Eficiencia Proyectada", f"{nueva_ef:.1f}%", delta=f"+{(nueva_ef - ef_d):.1f}%")
    mc3.metric("Desperdicios Reducidos", f"{nuevo_desp} h", delta="-15 h")
    
    st.info("💡 **Nota metodológica:** La reducción de esperas a 8 h es una **meta propuesta** y un escenario proyectado, no una mejora ya alcanzada en obra.")

    st.markdown("---")
    st.subheader("📋 Justificación del Frente y Estado Actual del Proyecto")
    st.markdown("""
    * **Participación Estructural:** La estructura representa el **27%** del presupuesto directo.
    * **Avance Real vs Programado:** Avance real del **22%** frente a un **45%** programado.
    * **Duración por Piso:** **4,5 semanas** reales por piso frente a **3 semanas** previstas contractualmente.
    * *(Nota: Estas cifras corresponden a las condiciones del caso y no deben confundirse con el porcentaje de desperdicio).*
    """)

# ==================== TAB 2: PRODUCTIVIDAD Y ECONOMÍA ====================
with tab2:
    st.header("2. Productividad de Encofrado e Interpretación Económica")
    st.markdown("Cálculo estricto de horas-hombre por metro cuadrado ($h-h/m²$) y análisis de ahorros potenciales.")
    
    with st.form("form_prod"):
        st.subheader("Captura de Datos en Campo para Encofrado")
        p_area = st.number_input("Área de encofrado ejecutada (m²)", min_value=0.1, value=590.0, step=10.0)
        p_trab = st.number_input("Número de trabajadores participantes", min_value=1, value=12, step=1)
        p_horas = st.number_input("Horas efectivamente dedicadas al encofrado por cada trabajador", min_value=0.1, value=40.0, step=1.0)
        
        submitted_prod = st.form_submit_button("Calcular Rendimiento de Encofrado")
        
    if submitted_prod:
        if p_area <= 0:
            st.error("El área ejecutada debe ser mayor a cero.")
        else:
            total_hh = p_trab * p_horas
            rendimiento_real = total_hh / p_area
            
            st.success("Cálculo realizado correctamente.")
            rc1, rc2, rc3, rc4 = st.columns(4)
            rc1.metric("Total Horas-Hombre (h-h)", f"{total_hh:.1f} h-h")
            rc2.metric("Área Ejecutada", f"{p_area} m²")
            rc3.metric("Rendimiento Obtenido", f"{rendimiento_real:.3f} h-h/m²")
            rc4.metric("Línea Base", "0.820 h-h/m²")
            
            st.markdown("---")
            st.subheader("📊 Comparativa con Metas y Referencias")
            df_comp = pd.DataFrame({
                "Indicador / Referencia": ["Rendimiento Obtenido", "Línea Base", "Meta Contractual", "Referencia Aspiracional"],
                "Valor (h-h/m²)": [f"{rendimiento_real:.3f}", "0.820", "≤ 0.650", "0.550"],
                "Estado": [
                    "Actual en campo", 
                    "Histórico inicial", 
                    "Límite contractual", 
                    "Objetivo Lean aspiracional"
                ]
            })
            st.dataframe(df_comp, use_container_width=True)
            
            st.markdown("---")
            st.subheader("💰 Análisis Económico para un Sector de 590 m²")
            area_sector = 590.0
            dif_ref = (0.82 - 0.55) * area_sector
            ahorro_meta = (0.82 - 0.65) * area_sector
            
            ec1, ec2 = st.columns(2)
            ec1.metric("Diferencia vs. Referencia Presupuestal", f"{dif_ref:.1f} h-h adicionales", help="(0.82 - 0.55) * 590 m²")
            ec2.metric("Ahorro Potencial vs. Meta Contractual", f"{ahorro_meta:.1f} h-h", help="(0.82 - 0.65) * 590 m²")
            
            st.markdown("""
            * **Nota sobre valoración en dinero:** Para expresar este ahorro en pesos, es requisito obligatorio solicitar un costo por hora-hombre debidamente sustentado, indicando su fuente y supuestos. *El dato aislado de que la mano de obra representa el 32% del costo directo de estructura no es suficiente por sí solo para valorar un sector.*
            """)

# ==================== TAB 3: LOOKAHEAD ====================
with tab3:
    st.header("3. Lookahead de Seis Semanas (S37 - S42)")
    st.markdown("Programación intermedia con inicio en S37 (28 de septiembre de 2026). Las tareas con restricciones pendientes **no** se califican automáticamente como listas para el plan semanal.")
    
    # Mostrar tabla editable
    st.markdown("### Tabla Lookahead (Editable)")
    edited_lookahead = st.data_editor(st.session_state["lookahead_df"], num_rows="dynamic", use_container_width=True)
    st.session_state["lookahead_df"] = edited_lookahead
    
    st.info("⚠️ **Regla Last Planner:** Una tarea que muestre restricciones pendientes en el Lookahead no debe liberarse para el Plan Semanal hasta que su condición restrictiva esté resuelta y confirmada.")

# ==================== TAB 4: RESTRICCIONES ====================
with tab4:
    st.header("4. Registro y Control de Restricciones")
    st.markdown("Control de las 10 restricciones del Anexo E, incluyendo los obstáculos identificados en S36 (177 m² de encofrado L4 S2 sin terminar y RFI-108 sin respuesta).")
    
    st.markdown("### Listado de Restricciones Activas")
    edited_constraints = st.data_editor(
        st.session_state["constraints_df"], 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Tipo": st.column_config.SelectboxColumn(
                "Tipo de Restricción",
                options=["Materiales", "Equipos", "Mano de obra", "Diseño o información", "Trabajo previo", "Liberaciones o permisos"],
                required=True
            ),
            "Estado": st.column_config.SelectboxColumn(
                "Estado",
                options=["Pendiente", "Liberada", "Vencida"],
                required=True
            )
        }
    )
    st.session_state["constraints_df"] = edited_constraints

# ==================== TAB 5: PLAN SEMANAL Y PPC ====================
with tab5:
    st.header("5. Plan Semanal y Captura de Cumplimiento (PPC)")
    st.markdown("Seleccione el modo de operación para verificar el cálculo del PPC con el caso S36 o gestionar compromisos semanales reales.")
    
    modo_ppc = st.radio("Seleccionar Modo:", ["Verificación Caso S36 (Prueba)", "Plan Semanal Operativo (S37 en adelante)"], horizontal=True)
    
    if modo_ppc == "Verificación Caso S36 (Prueba)":
        st.subheader("📋 Verificación Caso S36 (Datos de Prueba del Anexo E)")
        s36_total = 12
        s36_cumplidos = 7
        s36_incumplidos = 5
        s36_ppc = (s36_cumplidos / s36_total) * 100
        
        pc1, pc2, pc3, pc4 = st.columns(4)
        pc1.metric("Total Compromisos S36", s36_total)
        pc2.metric("Compromisos Cumplidos", s36_cumplidos)
        pc3.metric("Compromisos Incumplidos", s36_incumplidos)
        pc4.metric("PPC Obtenido", f"{s36_ppc:.1f}%", "Esperado: 58.3%")
        
        st.markdown("---")
        st.subheader("📊 Agrupación de Causas de Incumplimiento (S36)")
        df_causas_s36 = pd.DataFrame({
            "Causa de Incumplimiento": [
                "Materiales no disponibles",
                "Mano de obra insuficiente",
                "Diseño o RFI sin respuesta",
                "Actividad previa sin terminar"
            ],
            "Cantidad de Compromisos": [2, 1, 1, 1]
        })
        st.dataframe(df_causas_s36, use_container_width=True)
        st.info("ℹ️ La semana S36 sirve exclusivamente para verificar el cálculo del PPC y no reemplaza el plan propio de S37.")
        
    else:
        st.subheader("🛠️ Elaboración y Evaluación de Plan Semanal (8 a 15 compromisos)")
        st.markdown("Agregue o edite los compromisos de la semana actual. **Regla:** Solo se permite aprobar compromisos cuyas restricciones estén liberadas y exista capacidad verificada.")
        
        # Editor de compromisos
        edited_commitments = st.data_editor(
            st.session_state["commitments_df"],
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "RestriccionesLib": st.column_config.CheckboxColumn("¿Restricciones Liberadas?"),
                "CapacidadVerif": st.column_config.CheckboxColumn("¿Capacidad Verificada?"),
                "EstadoEval": st.column_config.SelectboxColumn("Evaluación", options=["Pendiente", "Sí", "No"]),
                "CausaIncumplimiento": st.column_config.SelectboxColumn(
                    "Causa (si es No)",
                    options=[
                        "Ninguna",
                        "Materiales no disponibles",
                        "Mano de obra insuficiente",
                        "Equipos no disponibles",
                        "Diseño o RFI sin respuesta",
                        "Actividad previa sin terminar",
                        "Liberaciones o permisos pendientes",
                        "Otras"
                    ]
                )
            }
        )
        st.session_state["commitments_df"] = edited_commitments
        
        if not st.session_state["commitments_df"].empty:
            df_c = st.session_state["commitments_df"]
            pendientes_eval = len(df_c[df_c["EstadoEval"] == "Pendiente"])
            total_c = len(df_c)
            
            st.markdown("---")
            st.subheader("📈 Cálculo de PPC de la Semana")
            if pendientes_eval > 0:
                st.warning(f"⚠️ **Atención:** Hay {pendientes_eval} compromisos pendientes de evaluar (de un total de {total_c}). El indicador actual es **provisional** hasta que se evalúen todos los compromisos.")
            
            cumplidos_reales = len(df_c[df_c["EstadoEval"] == "Sí"])
            evaluados = total_c - pendientes_eval
            ppc_real = (cumplidos_reales / evaluados * 100) if evaluados > 0 else 0.0
            
            rc_col1, rc_col2, rc_col3 = st.columns(3)
            rc_col1.metric("Total Compromisos", total_c)
            rc_col2.metric("Compromisos Evaluados", evaluados)
            rc_col3.metric("PPC Actual", f"{ppc_real:.1f}%")

# ==================== TAB 6: RESPALDO DE DATOS ====================
with tab6:
    st.header("6. Exportación e Importación de Datos (Respaldo)")
    st.markdown("Para evitar la pérdida de información en `st.session_state`, descargue un respaldo en formato JSON o cargue un archivo previo.")
    
    # Exportar datos
    data_to_export = {
        "constraints": st.session_state["constraints_df"].to_dict(orient="records"),
        "lookahead": st.session_state["lookahead_df"].to_dict(orient="records"),
        "commitments": st.session_state["commitments_df"].to_dict(orient="records")
    }
    json_str = json.dumps(data_to_export, indent=4, ensure_ascii=False)
    
    st.download_button(
        label="📥 Descargar Respaldo de Datos (JSON)",
        data=json_str,
        file_name="snowdon_towers_lean_backup.json",
        mime="application/json"
    )
    
    st.markdown("---")
    # Importar datos
    uploaded_file = st.file_uploader("📤 Cargar Respaldo Previo (JSON)", type=["json"])
    if uploaded_file is not None:
        try:
            imported_data = json.load(uploaded_file)
            st.session_state["constraints_df"] = pd.DataFrame(imported_data.get("constraints", []))
            st.session_state["lookahead_df"] = pd.DataFrame(imported_data.get("lookahead", []))
            st.session_state["commitments_df"] = pd.DataFrame(imported_data.get("commitments", []))
            st.success("¡Datos importados y restaurados con éxito en la sesión!")
        except Exception as e:
            st.error(f"Error al leer el archivo JSON: {e}")