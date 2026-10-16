import streamlit as st
from src.theme import page_header
import pandas as pd
from src.database import Database, Comment
from src.metrics import MetricsCalculator
from src.visualizations import Visualizations

page_header(st, "Termômetro Emocional", eyebrow="Sentimento", accent="Emocional")

db = Database()
session = db.get_session()

# Carregar dados
query = session.query(Comment.sentiment, Comment.published_at).all()
df = pd.DataFrame(query, columns=['sentiment', 'published_at'])
session.close()

if df.empty:
    st.warning("Sem dados suficientes. Realize uma coleta primeiro.")
else:
    st.markdown("### Distribuição Geral de Sentimentos")
    dist = MetricsCalculator.calculate_sentiment_distribution(df)
    fig1 = Visualizations.plot_sentiment_distribution(dist)
    st.plotly_chart(fig1, width='stretch')
    
    st.markdown("""
    **Interpretação:**
    Este gráfico exibe o volume de opiniões classificadas pelo modelo. 
    A predominância de comentários negativos sugere um debate acalorado ou discordância com o conteúdo do vídeo, 
    mas não indica necessariamente linguagem abusiva ou polarização agressiva (para isso, veja a página de Agressividade).
    """)
