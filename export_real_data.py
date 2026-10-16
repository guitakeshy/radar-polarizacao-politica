import pandas as pd
from src.database import Database, Video, Comment
from src.metrics import MetricsCalculator
from src.visualizations import Visualizations
import json
import os

os.makedirs("graficos_rede_social/reais", exist_ok=True)

session = Database().get_session()

# Fetch data
videos = pd.read_sql(session.query(Video).statement, session.bind)
comments = pd.read_sql(session.query(Comment).statement, session.bind)

print(f"Total Vídeos: {len(videos)}")
print(f"Total Comentários: {len(comments)}")

if len(comments) > 0 and len(videos) > 0:
    print(f"Termo de busca usado: {videos['search_term'].iloc[0]}")
    print(f"Período: {comments['published_at'].min()} a {comments['published_at'].max()}")
    
    # 1. Termometro
    dist = MetricsCalculator.calculate_sentiment_distribution(comments)
    fig1 = Visualizations.plot_sentiment_distribution(dist)
    fig1.update_layout(width=800, height=500)
    fig1.write_image("graficos_rede_social/reais/1_Termometro.png", scale=2)
    print("Sentimentos:", dist.to_dict())
    
    # 2. Polarizacao vs Agressividade
    video_stats = comments.groupby(['video_id']).agg(
        total_comments=('sentiment', 'count'),
        negative_comments=('sentiment', lambda x: (x == 'Negativo').sum()),
        aggressive_comments=('is_aggressive', 'sum')
    ).reset_index()
    video_stats['negative_pct'] = (video_stats['negative_comments'] / video_stats['total_comments']) * 100
    video_stats['aggressive_pct'] = (video_stats['aggressive_comments'] / video_stats['total_comments']) * 100
    video_stats = video_stats.merge(videos[['id', 'title']], left_on='video_id', right_on='id')
    video_stats.rename(columns={'title': 'video_title'}, inplace=True)
    
    fig2 = Visualizations.plot_scatter_polarization_aggression(video_stats)
    fig2.update_layout(width=800, height=500)
    fig2.write_image("graficos_rede_social/reais/2_Polarizacao.png", scale=2)
    
    # 3. Anatomia
    aggr_comments = comments[comments['is_aggressive'] == True]
    if len(aggr_comments) > 0:
        cat_freq = MetricsCalculator.calculate_aggression_categories_frequency(aggr_comments)
        fig3 = Visualizations.plot_aggression_categories(cat_freq)
        fig3.update_layout(width=800, height=500)
        fig3.write_image("graficos_rede_social/reais/3_Anatomia.png", scale=2)
        print("Agressividade:", cat_freq.to_dict())
    else:
        print("Sem comentarios agressivos reais.")
        
    # 4. Evolução
    temporal = MetricsCalculator.calculate_temporal_evolution(comments, freq='W')
    if not temporal.empty:
        fig4 = Visualizations.plot_temporal_evolution(temporal)
        fig4.update_layout(width=900, height=500, title='Evolução Temporal (Agrupamento Semanal)')
        fig4.write_image("graficos_rede_social/reais/4_Evolucao_Semanal.png", scale=2)
        
    # 5. Matriz
    fig5 = Visualizations.plot_correlation_matrix(comments.dropna(subset=['text_cleaned']))
    fig5.update_layout(width=700, height=500)
    fig5.write_image("graficos_rede_social/reais/5_Matriz.png", scale=2)
    
print("Pronto!")
