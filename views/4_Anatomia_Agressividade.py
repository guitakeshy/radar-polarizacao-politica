import streamlit as st
from src.theme import page_header
import pandas as pd
import json
from src.database import Database, Comment
from src.metrics import MetricsCalculator
from src.visualizations import Visualizations
from src.config import Config

page_header(st, "Anatomia da Agressividade", eyebrow="Categorias", accent="Agressividade")

db = Database()
session = db.get_session()

query = session.query(Comment.text_cleaned, Comment.aggression_categories, Comment.sentiment).filter(Comment.is_aggressive == True).all()
session.close()

df = pd.DataFrame(query, columns=['text_cleaned', 'aggression_categories', 'sentiment'])

if df.empty:
    st.warning("Nenhum comentário classificado como agressivo encontrado nos dados atuais.")
else:
    st.markdown("### Composição das Categorias de Agressividade")
    st.write(f"Total de comentários agressivos detectados: **{len(df)}**")
    
    cat_freq = MetricsCalculator.calculate_aggression_categories_frequency(df)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        fig = Visualizations.plot_aggression_categories(cat_freq)
        st.plotly_chart(fig, width='stretch')
        
    with col2:
        st.markdown("#### Top Categorias (%)")
        st.dataframe(cat_freq.rename("Percentual").map('{:.1f}%'.format))
        
    # Na versão pública não exibimos o texto de comentários (e o banco público nem o contém)
    if Config.is_public_mode():
        st.caption(
            "Por privacidade, a versão pública não exibe o texto dos comentários. "
            "Os exemplos usados para auditar o classificador ficam disponíveis apenas na versão local da pesquisa."
        )
        st.stop()

    st.markdown("### Exemplos Anonimizados (Revisão Humana)")
    st.markdown("Abaixo, amostras de comentários detectados pelas heurísticas. Utilize para auditar a eficácia das regras e identificar falsos positivos (ex: ironias ou citações).")
    
    sample_size = st.slider("Quantidade de exemplos", 5, 20, 10)
    sample_df = df.sample(min(sample_size, len(df)))
    
    for _, row in sample_df.iterrows():
        cats = ", ".join(json.loads(row['aggression_categories'])) if isinstance(row['aggression_categories'], str) else "N/A"
        st.info(f"**Categorias:** {cats} | **Sentimento:** {row['sentiment']}\n\n> \"{row['text_cleaned']}\"")
