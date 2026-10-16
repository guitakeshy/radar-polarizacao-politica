import streamlit as st
from src.theme import page_header
import pandas as pd
from src.database import Database, Comment, Video
from src.report_generator import ReportGenerator

page_header(st, "Relatório Analítico", eyebrow="Conclusões", accent="Analítico")

db = Database()
session = db.get_session()

comments_query = session.query(Comment.published_at, Comment.sentiment, Comment.is_aggressive, Comment.text_cleaned, Comment.camp_targets).all()
videos_query = session.query(Video.id, Video.title).all()

session.close()

df_comments = pd.DataFrame(comments_query, columns=['published_at', 'sentiment', 'is_aggressive', 'text_cleaned', 'camp_targets'])
df_videos = pd.DataFrame(videos_query, columns=['id', 'title'])

if df_comments.empty or df_videos.empty:
    st.warning("Sem dados suficientes para gerar o relatório.")
else:
    generator = ReportGenerator(None)
    report = generator.generate_markdown_report(df_comments, df_videos)
    
    st.markdown("### Relatório Gerado")
    st.markdown(report)
    
    st.download_button(
        label="📥 Baixar Relatório (Markdown)",
        data=report,
        file_name="relatorio_radar_polarizacao.md",
        mime="text/markdown"
    )
    
    st.info("Utilize este relatório como base para artigos ou publicações. Os resultados apresentados devem ser sempre contextualizados com as limitações da coleta.")
