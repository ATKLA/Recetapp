import os
import streamlit as st
import time
import random
from PIL import Image
import base64
import io

# Inicialización del estado de la sesión
if 'receta_seleccionada' not in st.session_state:
    st.session_state.receta_seleccionada = None
if 'autocompletar' not in st.session_state:
    st.session_state.autocompletar = False

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="Recetapp",
    page_icon="🍳",
    layout="centered",
    initial_sidebar_state="auto"
)

# Ocultar elementos de Streamlit
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    .st-emotion-cache-zq5wmm {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ------ESTILOS CSS---------------------------------------------------------------------------

st.markdown("""
    <style>
    .block-container {
        max-width: 800px;
        text-align: center;
    }
    
    /*No me esta cogiendo el formato polaroid, pero me gusta la etiqueta con el nombre que añade*/
    .polaroid-frame { 
        background: white;
        padding: 15px 15px 40px 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: rotate(-2deg);
        transition: all 0.3s ease;
        max-width: 450px;
        width: 100%;
        text-align: center;
    }
    .polaroid-frame:hover {
        transform: rotate(0deg) scale(1.02);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    .polaroid-image-wrapper {
        width: 100%;
        height: 300px;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f8f8f8;
        border: 1px solid #eee;
    }
    .polaroid-image-wrapper img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .polaroid-caption {
        font-family: 'Courier New', monospace;
        font-size: 1.4em;
        font-weight: bold;
        color: #333;
        margin-top: 15px;
        padding: 0 10px;
    }
    /* Estilos para los recuadros */
    .recipe-box {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        max-width: 700px;
    }
    .time-box {
        text-align: center;
        background-color: #f0f7ff;
        border-left: 5px solid #4a8cff;
    }
    .ingredients-box {
        text-align: center;
        background-color: #f5fff0;
        border-left: 5px solid #6a9a1b;
    }
    .ingredients-box ul {
        display: inline-block;
        text-align: left; 
        margin: 0 auto;
        padding-left: 20px;
        width: 90%; 
    }
    .ingredients-box li {
        text-align: left;
        list-style-position: outside; 
        margin-left: 1em;
    }
    .ingredients-box h3 {
        text-align: center; 
        margin: 0 auto 1rem auto;
    }
    .steps-box {
        text-align: center;
        background-color: #fff5f0;
        border-left: 5px solid #ff8c4a;
    }
    .steps-box ol {
        display: inline-block;
        text-align: left; 
        margin: 0 auto;
        padding-left: 20px;
        width: 90%; 
    }
    .steps-box li {
        text-align: left;
        list-style-position: outside; 
        margin-left: 1em;
    }
    .steps-box h3 {
        text-align: center; 
        margin: 0 auto 1rem auto;
    }
    /* Centrado completo de listas */
    .ingredients-box ul, .steps-box ol {
        display: inline-block;
        text-align: left;
        padding-left: 20px;
        margin: 0 auto;
    }
    /* Alineación de viñetas/números con el texto */
    .ingredients-box li, .steps-box li {
        text-align: left;
        list-style-position: inside;
        padding-left: 0;
    }
    .stMultiSelect, .stSlider {
        margin: 0 auto !important;
        max-width: 500px;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATOS DE RECETAS --------------------------------------------------------------------------
RECETAS = {
    "Revuelto de tofu": {
        "ingredientes": ["Huevos", "Cebolla", "Tofu", "Jengibre"],
        "tiempo": 20,
        "imagen": os.path.join("images/revuelto_tofu.jpg"),
        "preparacion": [
            "Secar el tofu y desmenuzarlo en un bol",
            "Salpimentar el tofu y añadir especias al gusto",
            "Sofrito de cebolla y jengibre picado",
            "Cuando el sofrito este dorado añadimos el tofu",
            "Rompemos un par de huevos en la sarten y mezclar un par de minutos"
        ]
    },
    "Ensalada de mango": {
        "ingredientes": ["Mango", "Tomates", "Cebolla", "Aguacates"],
        "tiempo": 15,
        "imagen": os.path.join("images/ensalada_mango.jpg"),
        "preparacion": [
            "Lavar, pelar y cortar los ingredientes",
            "Mezclar todos los ingredientes en un bol",
            "Aliñar con aceite de oliva y sal"
        ]
    },
    "Tosta de salmón picantón": {
        "ingredientes": ["Salmón ahumado", "Queso Cottage", "Wasabi", "Aguacates", "Salsa de soja"],
        "tiempo": 10,
        "imagen": os.path.join("images/tosta_salmon.jpg"),
        "preparacion": [
            "Cortar el aguacate y mezclarlo con el queso cottage en un bol",
            "Añadimos un poco de wasabi y un toque de salsa de soja",
            "Ponemos esta mezcla como base de la tosta",
            "Colocamos el salmón ahumado encima"
        ]
    }
}
# ------------------------------------------------------------------------------------------------
# --- INTERFAZ PRINCIPAL ---
st.markdown('<div class="centered-content">', unsafe_allow_html=True)
st.title("Recetapp 🍳")
st.header("¿Qué cocinamos hoy?")
st.markdown("</div>", unsafe_allow_html=True)

# Formulario de búsqueda
# ----------------INGREDIENTES----------------------------------------------------------------
if st.session_state.get('autocompletar', False) and st.session_state.get('receta_seleccionada'):
    try:
        # Forzar la actualización de los widgets
        st.session_state.ingredientes_autocompletados = RECETAS[st.session_state.receta_seleccionada]["ingredientes"]
        st.session_state.tiempo_autocompletado = RECETAS[st.session_state.receta_seleccionada]["tiempo"]
    except KeyError:
        pass

ingredientes = st.multiselect(
    "Ingredientes: ",
    options=["Huevos", "Mango", "Yogurt", "Queso Cottage", "Pepinillos", "Zanahorias",
             "Hummus", "Aguacates", "Brócoli", "Jengibre", "Salmón ahumado", "Salsa de soja", "Wasabi",
             "Calabacines", "Lechuga", "Tomates", "Cebolla", "Champiñones", "Tofu"],
    default=st.session_state.get('ingredientes_autocompletados', []),
    key="ingredientes_widget"
)

duracion = st.slider(
    "¿Cuánto tiempo tienes (minutos)?",
    5, 120,
    value=st.session_state.get('tiempo_autocompletado', 5),
    help="Selecciona el tiempo disponible para preparar la receta",
    key="tiempo_widget"
)

if st.session_state.get('autocompletar', False):
    st.session_state.autocompletar = False
    # Ejecutar automáticamente la búsqueda si queremos
    # st.session_state.ejecutar_busqueda = True
# --------------------------------------------------------------------------------------------

if st.button("🔍 Buscar receta", type="primary"):
    if not ingredientes:
        st.warning("Por favor, selecciona al menos un ingrediente")
    else:
        # Filtrar recetas posibles
        recetas_posibles = [
            (nombre, datos) for nombre, datos in RECETAS.items()
            if all(ing in ingredientes for ing in datos["ingredientes"])
               and datos["tiempo"] <= duracion
        ]

        # Animación de búsqueda
        with st.empty():
            search_container = st.container()
            with search_container:
                st.markdown('<div class="searching-animation">', unsafe_allow_html=True)
                st.markdown("<h3> 🤔 Pensando la receta perfecta para ti...</h3>", unsafe_allow_html=True)

                # Barra de progreso animada
                progress_bar = st.progress(0)
                for percent in range(100):
                    time.sleep(0.03)
                    progress_bar.progress(percent + 1)

                st.markdown("</div>", unsafe_allow_html=True)

        time.sleep(0.5)  # Pequeña pausa dramática

        # Limpiar animación de búsqueda
        search_container.empty()

        if not recetas_posibles:
            # Mensaje cuando NO encuentra receta
            st.markdown('<div class="centered-content">', unsafe_allow_html=True)
            st.error("""
            🧐 No encontré recetas con los ingredientes seleccionados.

            Prueba con:
            - Añadir más ingredientes
            - Aumentar el tiempo disponible
            """)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Seleccionar receta aleatoria
            nombre_receta, receta = random.choice(recetas_posibles)

            # Efecto de éxito (solo si encuentra receta)
            st.markdown('<div class="centered-content">', unsafe_allow_html=True)
            st.success("¡Receta encontrada! 🎉")
            st.balloons()
            st.markdown("</div>", unsafe_allow_html=True)

            # Mostrar receta--------------------------------------------------------------------------------------
            # Crea columnas para centrar el contenido
            col1, col2, col3 = st.columns([1, 3, 1])

            with col2:
                # Marco polaroid
                st.markdown(f"""
                <div class="polaroid-frame">
                    <div class="polaroid-caption">{nombre_receta}</div>
                </div>
                """, unsafe_allow_html=True)

                # Imagen con estilo personalizado
                st.markdown("""
                <style>
                    div[data-testid="stImage"] {
                        margin: -50px auto 0 auto !important;
                        max-width: 90% !important;
                        border: 1px solid #eee !important;
                        padding: 10px !important;
                        background: white !important;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
                    }
                    div[data-testid="stImage"] > img {
                        max-height: 300px !important;
                        object-fit: cover !important;
                    }
                </style>
                """, unsafe_allow_html=True)

                st.image(receta["imagen"], use_container_width=True)

            # Recuadro 1: Tiempo
            st.markdown(f"""
                        <div class="recipe-box time-box">
                            <h3 style="margin-top: 0; color: #4a8cff;">⏲️ Tiempo de preparación</h3>
                            <p style="font-size: 24px; text-align: center;">{receta['tiempo']} minutos</p>
                        </div>
                        """, unsafe_allow_html=True)

            # Recuadro 2: Ingredientes
            ingredientes_html = "\n".join([f"<li>{ing}</li>" for ing in receta["ingredientes"]])
            st.markdown(f"""
                        <div class="recipe-box ingredients-box">
                            <h3 style="margin-top: 0; color: #6a9a1b;">🫚 Ingredientes</h3>
                            <ul>{ingredientes_html}</ul>
                        </div>
                        """, unsafe_allow_html=True)

            # Recuadro 3: Preparación
            pasos_html = "\n".join([f"<li>{paso}</li>" for paso in receta["preparacion"]])
            st.markdown(f"""
                        <div class="recipe-box steps-box">
                            <h3 style="margin-top: 0; color: #ff8c4a;">👩🏼‍🍳 Preparación</h3>
                            <ol>{pasos_html}</ol>
                        </div>
                        """, unsafe_allow_html=True)

            # Mensaje final
            st.markdown('<div class="centered-content">', unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("### ¡Buen provecho! 😋🍽️")
            st.markdown("---")
            st.markdown("</div>", unsafe_allow_html=True)

# Expander del Recetario (siempre visible)
with st.expander("📚 Recetario completo", expanded=False):
    opcion = st.selectbox(
        "Selecciona una receta:",
        options=[""] + list(RECETAS.keys()),
        index=0,
        key="select_receta",
        label_visibility="collapsed"
    )

    if opcion and opcion != st.session_state.get('opcion_anterior', ''):
        st.session_state.receta_seleccionada = opcion
        st.session_state.opcion_anterior = opcion
        st.session_state.autocompletar = True
        st.rerun()


# -----FOOTER------------------------------------------------------------------------------------
st.markdown("---")
st.caption("© 2025 Recetapp by ATKLA - Recetas resultonas para quién no tiene horas.")
