import streamlit as st
from src.theme import page_header
import pandas as pd
from src.database import Database, Comment
from src.metrics import MetricsCalculator
from src.visualizations import Visualizations

page_header(st, "Evolução Temporal", eyebrow="Ao longo do tempo", accent="Temporal")

db = Database()
session = db.get_session()

query = session.query(Comment.published_at, Comment.sentiment, Comment.is_aggressive).filter(Comment.published_at != None).all()
session.close()

df = pd.DataFrame(query, columns=['published_at', 'sentiment', 'is_aggressive'])

if df.empty:
    st.warning("Sem dados temporais disponíveis.")
else:
    freq = st.selectbox("Agrupamento", options=["D", "W", "M"], format_func=lambda x: {"D": "Diário", "W": "Semanal", "M": "Mensal"}[x])
    
    temporal_df = MetricsCalculator.calculate_temporal_evolution(df, freq=freq)
    
    if not temporal_df.empty:
        fig = Visualizations.plot_temporal_evolution(temporal_df)
        st.plotly_chart(fig, width='stretch')
        
        st.markdown("""
        **Observações Metodológicas:**
        A variação nos índices ao longo do tempo deve ser lida em conjunto com a amostra coletada em cada período. 
        Picos podem representar a publicação de um vídeo com alta tração e não necessariamente uma mudança estrutural na opinião pública geral.
        """)
    else:
        st.info("Não foi possível gerar a evolução com a agregação selecionada.")
