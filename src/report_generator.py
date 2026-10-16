import pandas as pd
from datetime import datetime
from src.metrics import MetricsCalculator

class ReportGenerator:
    def __init__(self, db_session):
        self.session = db_session

    def generate_markdown_report(self, df_comments, df_videos):
        if df_comments.empty or df_videos.empty:
            return "Não há dados suficientes para gerar o relatório."
            
        total_videos = len(df_videos)
        total_comments = len(df_comments)
        
        start_date = df_comments['published_at'].min().strftime('%d/%m/%Y') if not pd.isna(df_comments['published_at'].min()) else 'N/A'
        end_date = df_comments['published_at'].max().strftime('%d/%m/%Y') if not pd.isna(df_comments['published_at'].max()) else 'N/A'
        
        sentiment_pct = df_comments['sentiment'].value_counts(normalize=True) * 100
        negative_pct = sentiment_pct.get('Negativo', 0.0)
        
        aggressive_pct = (df_comments['is_aggressive'].sum() / total_comments) * 100
        neg_lo, neg_hi = MetricsCalculator.proportion_ci(int((df_comments['sentiment'] == 'Negativo').sum()), total_comments)
        aggr_lo, aggr_hi = MetricsCalculator.proportion_ci(int(df_comments['is_aggressive'].sum()), total_comments)

        polarization_line = ""
        if 'text_cleaned' in df_comments.columns or 'camp_targets' in df_comments.columns:
            camp = MetricsCalculator.calculate_camp_targets(df_comments).iloc[0]
            polarization_line = (
                f"\n- **Polarização Afetiva:** {camp['polarized_pct']:.1f}% dos comentários usam rótulos pejorativos partidários "
                f"({camp['esquerda_pct']:.1f}% contra a esquerda, {camp['direita_pct']:.1f}% contra a direita; "
                f"índice de equilíbrio {camp['balance']:+.2f}, de -1 a +1)."
            )

        report = f"""# Relatório Analítico: Polarização e Agressividade no YouTube

## 1. Contexto e Objetivo
Este relatório apresenta os resultados da análise de discussões políticas no YouTube, investigando padrões de polarização discursiva e identificando possíveis associações entre hostilidade política e linguagem agressiva no contexto brasileiro.
*Nota: Este relatório não visa prever comportamentos individuais, mas sim observar padrões em amostras públicas de discurso.*

## 2. Origem dos Dados
- **Período Analisado:** {start_date} a {end_date}
- **Vídeos Analisados:** {total_videos}
- **Comentários Recuperados:** {total_comments}
- **Coleta:** Via YouTube Data API v3.

## 3. Metodologia
- **Análise de Sentimento:** Utilização de modelos baseados em Transformers para classificar os comentários em Positivo, Neutro, Negativo e Inconclusivo.
- **Classificação de Agressividade:** Aplicação de léxicos baseados no contexto político brasileiro (palavras inteiras, com flexões e sem depender de acentos) para detectar insultos, ameaças, desumanização e hostilidade.
- **Polarização Afetiva:** Identificação de rótulos pejorativos dirigidos a cada campo político (esquerda/direita).

## 4. Resultados Observados
- **Volume de Comentários Negativos:** {negative_pct:.1f}% dos comentários foram classificados como possuindo sentimento negativo (IC 95%: {neg_lo:.1f}%–{neg_hi:.1f}%).
- **Volume de Comentários Agressivos:** {aggressive_pct:.1f}% dos comentários apresentaram sinais de linguagem agressiva (IC 95%: {aggr_lo:.1f}%–{aggr_hi:.1f}%).{polarization_line}

## 5. Limitações
- Comentários públicos em vídeos não representam a totalidade da população brasileira.
- O classificador de agressividade, sendo baseado em heurísticas textuais e modelos de NLP, pode apresentar falsos positivos em casos de ironia, sarcasmo ou gírias contextuais.
- As correlações observadas não implicam em relações de causalidade direta.

## 6. Discussão e Conclusão
Os dados mostram a dinâmica da discussão política nos vídeos coletados, destacando a proporção entre o simples sentimento negativo (discordância, descontentamento) e o uso efetivo de linguagem hostil (insultos, desumanização). Para investigações futuras, recomenda-se correlacionar esses picos de agressividade com eventos políticos específicos do período analisado.
"""
        return report
