import streamlit as st
import pandas as pd
from datetime import date, timedelta
import io  # Librería para manejar archivos en memoria y permitir la descarga

# ==========================================
# 1. CONFIGURACIÓN BÁSICA Y MEMORIA
# ==========================================
st.set_page_config(page_title="Gestor de CXC con Excel", page_icon="📊", layout="wide")

# Si no existe una base de datos temporal, la creamos con un caso de ejemplo
if "base_datos_falsa" not in st.session_state:
    st.session_state.base_datos_falsa = [
        {
            "Cliente/Proyecto": "Bombón - Sistema de Audio",
            "Total Venta": "$9,000.00",
            "Anticipo": "$300.00",
            "Saldo Pendiente": "$8,700.00",
            "Fechas de Cobro": "2026-05-10, 2026-05-25",
            "Estatus Legal": "Consentimiento Aprobado"
        }
    ]

# ==========================================
# 2. SELECTOR DE ROLES (Barra lateral)
# ==========================================
st.sidebar.title("👥 Control de Accesos")
rol_usuario = st.sidebar.selectbox(
    "Selecciona tu perfil:",
    ["🔒 Administrador (Jefe)", "👀 Cobrador / Visualizador"]
)

st.sidebar.divider()
st.sidebar.info("💡 **Jefe:** Registra ventas y descarga reportes en Excel.\n\n👁️ **Cobrador:** Consulta saldos y fechas.")

# ==========================================
# 3. VISTA ADMINISTRADOR
# ==========================================
if rol_usuario == "🔒 Administrador (Jefe)":
    st.title("👑 Panel de Administración (Jefe)")
    st.write("Control de altas, cálculo de anticipos, términos legales y exportación de datos.")
    
    with st.expander("📜 Aviso de Privacidad y Términos (Editable)"):
        terminos = st.text_area("Términos legales:", value="Los datos financieros se manejan bajo estricta seudonimización y confidencialidad.")
    
    acepto_legal = st.checkbox("✅ Confirmo que se cuenta con el consentimiento de privacidad del cliente.")
    
    if acepto_legal:
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Registrar Nueva Venta")
            with st.form("form_jefe", clear_on_submit=True):
                cliente = st.text_input("Nombre del Cliente / Proyecto", placeholder="Ej. Casa Barake")
                total = st.number_input("Monto Total ($)", min_value=0.0, value=12000.0, step=100.0)
                anticipo = st.number_input("Anticipo entregado ($)", min_value=0.0, value=2000.0, step=100.0)
                
                saldo = total - anticipo
                st.write(f"💰 Saldo pendiente calculado: **${saldo:,.2f}**")
                
                num_fechas = st.slider("Número de fechas de cobro", 1, 5, 3)
                lista_fechas = []
                for i in range(num_fechas):
                    f_sugerida = date.today() + timedelta(days=30 * (i + 1))
                    f_pago = st.date_input(f"Fecha de cobro #{i+1}", value=f_sugerida, key=f"f_{i}")
                    lista_fechas.append(str(f_pago))
                
                guardar = st.form_submit_button("Guardar Proyecto en el Sistema")
                
            if guardar and cliente:
                st.session_state.base_datos_falsa.append({
                    "Cliente/Proyecto": cliente,
                    "Total Venta": f"${total:,.2f}",
                    "Anticipo": f"${anticipo:,.2f}",
                    "Saldo Pendiente": f"${saldo:,.2f}",
                    "Fechas de Cobro": ", ".join(lista_fechas),
                    "Estatus Legal": "Consentimiento Aprobado"
                })
                st.success(f"¡Proyecto de {cliente} guardado con éxito!")

        with col2:
            st.subheader("📊 Base de Datos General y Exportación")
            df = pd.DataFrame(st.session_state.base_datos_falsa)
            st.dataframe(df, use_container_width=True)
            
            # --- MAGIA PARA DESCARGAR EN EXCEL ---
            # Convertimos el DataFrame a un archivo de Excel temporal en memoria
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='CuentasPorCobrar')
            excel_data = output.getvalue()
            
            # Botón de descarga web
            st.download_button(
                label="📥 Descargar reporte en Excel (.xlsx)",
                data=excel_data,
                file_name="reporte_cxc.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("⚠️ Debes marcar la casilla de confirmación legal para habilitar el registro y los reportes.")

# ==========================================
# 4. VISTA COBRADOR
# ==========================================
else:
    st.title("👁️ Panel de Cobranza (Solo Lectura)")
    st.write("Consulta rápida de saldos y fechas asignadas para visitas o llamadas de cobro.")
    
    st.divider()
    st.subheader("📅 Calendario de Cuentas por Cobrar Activas")
    
    if st.session_state.base_datos_falsa:
        df_cobros = pd.DataFrame(st.session_state.base_datos_falsa)
        st.dataframe(df_cobros, use_container_width=True)
        st.info("ℹ️ Para modificar montos o fechas, comunícate con el Administrador.")
    else:
        st.warning("No hay cuentas por cobrar registradas en este momento.")
