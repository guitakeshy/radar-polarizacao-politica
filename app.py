import streamlit as st
from src.config import Config
from src.theme import apply_theme

st.set_page_config(
    page_title="Radar da Polarização",
    page_icon="📊",
    layout="wide"
)
apply_theme(st)

# Páginas de análise (visíveis sempre)
analysis_pages = [
    st.Page("views/0_Inicio.py", title="Início", icon="📊", default=True),
    st.Page("views/2_Termometro_Emocional.py", title="Termômetro Emocional", icon="🌡️"),
    st.Page("views/3_Polarizacao_Agressividade.py", title="Polarização e Agressividade", icon="⚔️"),
    st.Page("views/4_Anatomia_Agressividade.py", title="Anatomia da Agressividade", icon="🧬"),
    st.Page("views/5_Evolucao_Temporal.py", title="Evolução Temporal", icon="📈"),
    st.Page("views/6_Analise_Estatistica.py", title="Análise Estatística", icon="🧮"),
    st.Page("views/7_Relatorio_Analitico.py", title="Relatório Analítico", icon="📝"),
    st.Page("views/8_Sobre.py", title="Sobre o Projeto", icon="ℹ️"),
]

# A coleta só aparece na versão local (com chave da API); na versão pública fica oculta
if Config.is_public_mode():
    nav = st.navigation(analysis_pages)
else:
    collection_page = st.Page("views/1_Busca_e_Coleta.py", title="Busca e Coleta", icon="🔍")
    nav = st.navigation({"Análise": analysis_pages, "Coleta": [collection_page]})

st.sidebar.info(
    "Os dados coletados são públicos, mas as inferências automáticas possuem limitações. "
    "Veja **Sobre o Projeto**."
)

nav.run()
