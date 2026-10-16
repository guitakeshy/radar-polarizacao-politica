import streamlit as st
from src.theme import page_header
import pandas as pd
from src.database import Database, Comment, Video
from src.metrics import MetricsCalculator
from src.visualizations import Visualizations

page_header(st, "Polarização e Agressividade", eyebrow="Polarização afetiva", accent="Agressividade")

db = Database()
session = db.get_session()

# Consulta agregada por vídeo
query = session.query(
    Video.id,
    Video.title,
    Comment.sentiment,
    Comment.is_aggressive,
    Comment.text_cleaned,
    Comment.camp_targets
).join(Comment, Video.id == Comment.video_id).all()

session.close()
df = pd.DataFrame(query, columns=['video_id', 'video_title', 'sentiment', 'is_aggressive', 'text_cleaned', 'camp_targets'])

if df.empty:
    st.warning("Sem dados suficientes.")
else:
    # Agregar por vídeo
    video_stats = df.groupby(['video_id', 'video_title']).agg(
        total_comments=('sentiment', 'count'),
        negative_comments=('sentiment', lambda x: (x == 'Negativo').sum()),
        aggressive_comments=('is_aggressive', 'sum')
    ).reset_index()

    video_stats['negative_pct'] = (video_stats['negative_comments'] / video_stats['total_comments']) * 100
    video_stats['aggressive_pct'] = (video_stats['aggressive_comments'] / video_stats['total_comments']) * 100

    # Filtra vídeos com poucos comentários para não distorcer o gráfico
    video_stats = video_stats[video_stats['total_comments'] >= 10]

    st.markdown("""
    ### Associação entre Negatividade e Agressividade
    Este gráfico de dispersão ajuda a investigar a hipótese: *Fóruns de discussão política mais negativos são, de fato, mais agressivos?*
    Cada bolha representa um vídeo analisado. O tamanho da bolha reflete a quantidade de comentários.
    """)

    if len(video_stats) > 1:
        fig = Visualizations.plot_scatter_polarization_aggression(video_stats)
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("É necessário coletar comentários de pelo menos 2 vídeos diferentes (com +10 comentários cada) para visualizar este gráfico.")

    # --- Polarização afetiva ---
    st.markdown("""
    ### Polarização Afetiva: quem é o alvo?
    Sentimento negativo mede *descontentamento*; polarização afetiva mede *hostilidade contra o outro lado*.
    Aqui contamos comentários que usam rótulos pejorativos partidários
    (ex.: "petralha", "mortadela" contra a esquerda; "bolsominion", "gado" contra a direita).
    """)

    overall = MetricsCalculator.calculate_camp_targets(df).iloc[0]
    col1, col2, col3 = st.columns(3)
    col1.metric("Rótulos partidários", f"{overall['polarized_pct']:.1f}%")
    col2.metric("Ataques à Esquerda", f"{overall['esquerda_pct']:.1f}%")
    col3.metric("Ataques à Direita", f"{overall['direita_pct']:.1f}%")

    camp_by_video = MetricsCalculator.calculate_camp_targets(df, group_col='video_title')
    camp_by_video = camp_by_video[camp_by_video['total_comments'] >= 10]
    if camp_by_video['polarized'].sum() > 0:
        fig_camp = Visualizations.plot_camp_targets(camp_by_video)
        st.plotly_chart(fig_camp, width='stretch')

    st.caption(
        "O índice de equilíbrio vai de -1 (só ataques à direita) a +1 (só ataques à esquerda). "
        f"Na amostra atual: **{overall['balance']:+.2f}**. "
        "Os léxicos estão em `src/lexicon.py` e devem ser revisados conforme o contexto da coleta; "
        "ironia e citações podem gerar falsos positivos."
    )
