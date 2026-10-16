import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ATENÇÃO: este script gera gráficos com DADOS SIMULADOS (exemplos de layout).
# Para gráficos com os dados reais coletados, use export_real_data.py.

# Create directory for output images
os.makedirs("graficos_rede_social", exist_ok=True)


def mark_simulated(fig):
    """Marca o gráfico como simulado, para não ser confundido com resultado real."""
    fig.add_annotation(
        text="DADOS SIMULADOS — apenas ilustração",
        xref="paper", yref="paper", x=0.5, y=0.5,
        showarrow=False, font=dict(size=28, color="rgba(150,150,150,0.35)"),
        textangle=-20
    )
    return fig

# 1. Termômetro Emocional
sentiment_data = pd.DataFrame({
    'Sentimento': ['Positivo', 'Neutro', 'Negativo', 'Inconclusivo'],
    'Percentual': [15.2, 22.5, 58.3, 4.0]
})
color_map = {"Positivo": "#2ecc71", "Neutro": "#95a5a6", "Negativo": "#e74c3c", "Inconclusivo": "#bdc3c7"}
fig1 = px.bar(
    sentiment_data, x='Sentimento', y='Percentual', color='Sentimento',
    color_discrete_map=color_map, title='Distribuição de Sentimentos (Amostra)',
    text=sentiment_data['Percentual'].apply(lambda x: f'{x:.1f}%')
)
fig1.update_layout(showlegend=False, width=800, height=500)
mark_simulated(fig1).write_image("graficos_rede_social/1_Termometro_Emocional.png", scale=2)

# 2. Polarização vs Agressividade
np.random.seed(42)
video_stats = pd.DataFrame({
    'video_title': [f'Vídeo Debate {i}' for i in range(1, 21)],
    'negative_pct': np.random.normal(55, 15, 20).clip(10, 90),
    'aggressive_pct': np.random.normal(25, 10, 20).clip(5, 60),
    'total_comments': np.random.randint(100, 5000, 20)
})
# correlation push
video_stats['aggressive_pct'] += video_stats['negative_pct'] * 0.3
fig2 = px.scatter(
    video_stats, x='negative_pct', y='aggressive_pct', size='total_comments',
    hover_name='video_title', title='Associação: Negatividade vs Agressividade',
    labels={'negative_pct': 'Sentimento Negativo (%)', 'aggressive_pct': 'Agressividade (%)'},
    trendline="ols"
)
fig2.update_layout(width=800, height=500)
mark_simulated(fig2).write_image("graficos_rede_social/2_Polarizacao_Agressividade.png", scale=2)

# 3. Anatomia da Agressividade
cat_data = pd.DataFrame({
    'Categoria': ['Insultos', 'Desumanização', 'Hostilidade', 'Ameaças'],
    'Percentual': [65.4, 18.2, 12.1, 4.3]
})
fig3 = px.pie(
    cat_data, values='Percentual', names='Categoria', hole=0.4,
    title='Composição da Agressividade'
)
fig3.update_traces(textposition='inside', textinfo='percent+label')
fig3.update_layout(width=800, height=500)
mark_simulated(fig3).write_image("graficos_rede_social/3_Anatomia_Agressividade.png", scale=2)

# 4. Evolução Temporal
dates = pd.date_range(start="2023-08-01", end="2023-08-30")
temporal_df = pd.DataFrame({
    'published_at': dates,
    'negative_pct': np.random.normal(50, 5, len(dates)),
    'aggressive_pct': np.random.normal(20, 3, len(dates))
})
# Simulate a spike (event)
temporal_df.loc[15:18, 'negative_pct'] += 25
temporal_df.loc[15:18, 'aggressive_pct'] += 15

fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=temporal_df['published_at'], y=temporal_df['negative_pct'], mode='lines+markers', name='Sentimento Negativo', line=dict(color='#e74c3c')))
fig4.add_trace(go.Scatter(x=temporal_df['published_at'], y=temporal_df['aggressive_pct'], mode='lines+markers', name='Agressividade', line=dict(color='#8e44ad')))
fig4.update_layout(title='Evolução Temporal nas Eleições', width=900, height=500)
mark_simulated(fig4).write_image("graficos_rede_social/4_Evolucao_Temporal.png", scale=2)

# 5. Matriz
corr_data = pd.DataFrame({
    'Sentimento': [1, -0.75, -0.2],
    'Agressividade': [-0.75, 1, 0.4],
    'Tamanho do Texto': [-0.2, 0.4, 1]
}, index=['Sentimento', 'Agressividade', 'Tamanho do Texto'])
fig5 = px.imshow(corr_data, text_auto=True, color_continuous_scale='RdBu_r', zmin=-1, zmax=1, title='Matriz de Correlação')
fig5.update_layout(width=700, height=500)
mark_simulated(fig5).write_image("graficos_rede_social/5_Matriz_Correlacao.png", scale=2)

print("Imagens geradas com sucesso.")
