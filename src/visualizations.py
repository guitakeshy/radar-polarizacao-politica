import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src import theme  # registra o template Plotly do site como padrão
from src.metrics import MetricsCalculator

class Visualizations:

    @staticmethod
    def plot_sentiment_distribution(sentiment_pct):
        if sentiment_pct.empty:
            return go.Figure()

        df = sentiment_pct.reset_index()
        df.columns = ['Sentimento', 'Percentual']

        fig = px.bar(
            df,
            x='Sentimento',
            y='Percentual',
            color='Sentimento',
            color_discrete_map=theme.SENTIMENT_COLORS,
            title='Distribuição de Sentimentos nos Comentários',
            text=df['Percentual'].apply(lambda x: f'{x:.1f}%')
        )
        fig.update_traces(marker_cornerradius=8, textfont=dict(size=14, color=theme.INK), textposition='outside', cliponaxis=False)
        fig.update_layout(showlegend=False, xaxis_title='', yaxis_title='% dos comentários')
        return fig

    @staticmethod
    def plot_temporal_evolution(temporal_df):
        if temporal_df.empty:
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=temporal_df['published_at'],
            y=temporal_df['negative_pct'],
            mode='lines+markers',
            name='% Sentimento Negativo',
            line=dict(color=theme.ORANGE, width=3)
        ))

        fig.add_trace(go.Scatter(
            x=temporal_df['published_at'],
            y=temporal_df['aggressive_pct'],
            mode='lines+markers',
            name='% Agressividade',
            line=dict(color=theme.BLUE, width=3)
        ))

        fig.update_layout(
            title='Evolução Temporal: Negatividade e Agressividade',
            xaxis_title='Data',
            yaxis_title='Percentual (%)',
            hovermode='x unified',
            legend=dict(orientation='h', y=-0.2)
        )
        return fig

    @staticmethod
    def plot_aggression_categories(categories_pct):
        if categories_pct.empty:
            return go.Figure()

        df = categories_pct.reset_index()
        df.columns = ['Categoria', 'Percentual']

        fig = px.pie(
            df,
            values='Percentual',
            names='Categoria',
            title='Composição das Categorias de Agressividade',
            hole=0.55,
            color_discrete_sequence=theme.CATEGORY_SEQUENCE
        )
        fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
        fig.update_layout(showlegend=False)
        return fig

    @staticmethod
    def plot_correlation_matrix(df):
        if df.empty or len(df) < 2:
            return go.Figure()

        # Preparando dados quantitativos para correlação
        # Mapeando sentimento para valor numérico
        sent_map = {"Positivo": 1, "Neutro": 0, "Negativo": -1, "Inconclusivo": None}

        df_corr = pd.DataFrame()
        df_corr['sentimento_num'] = df['sentiment'].map(sent_map)
        df_corr['agressivo'] = df['is_aggressive'].astype(int)
        df_corr['tamanho_texto'] = MetricsCalculator.text_lengths(df)

        # Spearman: sentimento é ordinal e agressividade é binária, então Pearson não é o mais adequado
        corr_matrix = df_corr.corr(method='spearman', numeric_only=True)

        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            aspect="auto",
            title="Matriz de Correlação entre Variáveis",
            color_continuous_scale=theme.DIVERGING_SCALE,
            zmin=-1, zmax=1
        )
        return fig

    @staticmethod
    def plot_scatter_polarization_aggression(video_stats_df):
        """
        Gráfico de dispersão entre % Sentimento Negativo vs % Agressividade
        Agrupado por vídeo.
        """
        if video_stats_df.empty:
            return go.Figure()

        fig = px.scatter(
            video_stats_df,
            x='negative_pct',
            y='aggressive_pct',
            size='total_comments',
            hover_name='video_title',
            title='Associação entre Negatividade e Agressividade por Vídeo',
            labels={
                'negative_pct': 'Sentimento Negativo (%)',
                'aggressive_pct': 'Agressividade (%)',
                'total_comments': 'Volume de Comentários'
            },
            trendline="ols", # Necessário statsmodels
            trendline_color_override=theme.ORANGE
        )
        fig.update_traces(selector=dict(mode='markers'), marker=dict(color=theme.BLUE, opacity=0.7, line=dict(color='#ffffff', width=1)))
        return fig

    @staticmethod
    def plot_camp_targets(camp_df, label_col='video_title', top_n=15):
        """
        Barras horizontais: % de comentários com rótulos pejorativos contra
        cada campo político, por vídeo (os mais polarizados no topo).
        """
        if camp_df.empty:
            return go.Figure()

        df = camp_df.sort_values('polarized_pct', ascending=True).tail(top_n)
        labels = df[label_col].str.slice(0, 60)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=labels, x=df['esquerda_pct'], orientation='h',
            name='Ataques à Esquerda', marker_color=theme.ORANGE
        ))
        fig.add_trace(go.Bar(
            y=labels, x=df['direita_pct'], orientation='h',
            name='Ataques à Direita', marker_color=theme.BLUE
        ))
        fig.update_traces(marker_cornerradius=4)
        fig.update_layout(
            barmode='group',
            title='Alvos de Rótulos Pejorativos Partidários por Vídeo',
            xaxis_title='% dos comentários do vídeo',
            yaxis_title='',
            height=max(400, 32 * len(df) + 120),
            legend=dict(orientation='h', y=-0.15)
        )
        return fig
