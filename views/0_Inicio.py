import streamlit as st
import pandas as pd
from src.database import Database, Video, Comment
from src.config import Config
from src.theme import page_header

page_header(
    st,
    "Radar da Polarização Política Brasileira",
    eyebrow="Ciência de dados · Política · YouTube",
    accent="Polarização Política Brasileira",
    lead="Análise de discussões políticas públicas no YouTube para investigar padrões de polarização "
         "discursiva e a relação entre hostilidade política e linguagem agressiva.",
)

# Verifica configurações da API (só faz sentido na versão local, com coleta)
if not Config.is_public_mode() and not Config.is_api_key_configured():
    st.warning("⚠️ Chave da API do YouTube não configurada. Defina YOUTUBE_API_KEY no arquivo .env para permitir novas coletas.")

@st.cache_resource
def get_db():
    return Database()

db = get_db()
session = db.get_session()

# Coleta estatísticas gerais
total_videos = session.query(Video).count()
total_comments = session.query(Comment).count()

if total_comments > 0:
    # Carrega dados básicos
    comments_query = session.query(Comment.sentiment, Comment.is_aggressive).all()
    df_comments = pd.DataFrame(comments_query, columns=['sentiment', 'is_aggressive'])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Vídeos Analisados", total_videos)
    col2.metric("Comentários Recuperados", total_comments)

    sentiment_dist = df_comments['sentiment'].value_counts(normalize=True) * 100
    negative_pct = sentiment_dist.get('Negativo', 0.0)
    inconclusive_pct = sentiment_dist.get('Inconclusivo', 0.0)

    col3.metric("% Sentimento Negativo", f"{negative_pct:.1f}%")

    aggression_pct = (df_comments['is_aggressive'].sum() / len(df_comments)) * 100
    col4.metric("% Agressividade", f"{aggression_pct:.1f}%")

    st.info(f"Proporção de registros inconclusivos: {inconclusive_pct:.1f}%")

    if Config.is_public_mode():
        st.markdown(
            "Use o menu ao lado para explorar os resultados. "
            "Para entender como os dados foram coletados e classificados, veja a página **Sobre o Projeto**."
        )
elif Config.is_public_mode():
    st.info("Nenhum dado disponível nesta versão pública.")
else:
    st.info("Nenhum dado coletado ainda. Vá para a página de Busca e Coleta para iniciar.")

session.close()
