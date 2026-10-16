import json
import numpy as np
import pandas as pd
from scipy import stats
from src.lexicon import detect_camp_targets

# Pandas 3 não aceita mais 'M' para mensal; mantém compatibilidade com a interface
FREQ_ALIASES = {"M": "ME"}


class MetricsCalculator:
    @staticmethod
    def camp_target_lists(df):
        """
        Campos políticos atacados em cada comentário. Usa o resultado guardado
        (coluna camp_targets, presente no banco público, que não tem texto) ou,
        na falta dele, calcula a partir do texto.
        """
        stored = df['camp_targets'] if 'camp_targets' in df.columns else pd.Series(None, index=df.index, dtype=object)
        texts = df['text_cleaned'] if 'text_cleaned' in df.columns else pd.Series('', index=df.index)
        return pd.Series(
            [json.loads(s) if isinstance(s, str) else detect_camp_targets(t if isinstance(t, str) else '')
             for s, t in zip(stored, texts)],
            index=df.index,
        )

    @staticmethod
    def text_lengths(df):
        """Tamanho de cada comentário: valor guardado ou calculado a partir do texto."""
        computed = df['text_cleaned'].str.len() if 'text_cleaned' in df.columns else pd.Series(np.nan, index=df.index)
        if 'text_length' in df.columns:
            return df['text_length'].astype(float).fillna(computed)
        return computed

    @staticmethod
    def calculate_sentiment_distribution(df):
        if df.empty:
            return pd.Series(dtype=float)
        return df['sentiment'].value_counts(normalize=True) * 100

    @staticmethod
    def calculate_aggression_rate(df):
        if df.empty:
            return 0.0
        return (df['is_aggressive'].sum() / len(df)) * 100

    @staticmethod
    def proportion_ci(successes, total, z=1.96):
        """Intervalo de confiança de Wilson (95%) para uma proporção, em %."""
        if total == 0:
            return 0.0, 0.0
        p = successes / total
        denom = 1 + z**2 / total
        center = (p + z**2 / (2 * total)) / denom
        half = z * np.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denom
        return max(0.0, center - half) * 100, min(1.0, center + half) * 100

    @staticmethod
    def calculate_aggression_categories_frequency(df):
        if df.empty:
            return pd.Series(dtype=float)

        all_categories = []
        for cats in df['aggression_categories'].dropna():
            if isinstance(cats, str):
                try:
                    cats = json.loads(cats)
                except json.JSONDecodeError:
                    cats = []
            if isinstance(cats, list):
                all_categories.extend(cats)

        if not all_categories:
            return pd.Series(dtype=float)

        return pd.Series(all_categories).value_counts(normalize=True) * 100

    @staticmethod
    def calculate_temporal_evolution(df, freq='D'):
        if df.empty or 'published_at' not in df.columns:
            return pd.DataFrame()

        df = df.copy()  # não altera o DataFrame de quem chamou
        df['published_at'] = pd.to_datetime(df['published_at'])
        freq = FREQ_ALIASES.get(freq, freq)

        # Agrupa por tempo e calcula percentual de sentimento negativo e agressividade
        temporal = df.groupby(pd.Grouper(key='published_at', freq=freq)).agg(
            total_comments=('sentiment', 'count'),
            negative_comments=('sentiment', lambda x: (x == 'Negativo').sum()),
            aggressive_comments=('is_aggressive', 'sum')
        ).reset_index()

        temporal['negative_pct'] = (temporal['negative_comments'] / temporal['total_comments']) * 100
        temporal['aggressive_pct'] = (temporal['aggressive_comments'] / temporal['total_comments']) * 100

        # Filtra períodos sem comentários
        return temporal[temporal['total_comments'] > 0]

    @staticmethod
    def calculate_camp_targets(df, group_col=None):
        """
        Polarização afetiva: proporção de comentários que usam rótulos pejorativos
        contra a Esquerda e contra a Direita.

        Retorna colunas: total_comments, esquerda_pct, direita_pct, polarized_pct
        e balance (-1 = só ataques à Direita, +1 = só ataques à Esquerda).
        """
        if df.empty:
            return pd.DataFrame()

        targets = MetricsCalculator.camp_target_lists(df)
        data = pd.DataFrame({
            'esquerda': targets.map(lambda t: 'Esquerda' in t),
            'direita': targets.map(lambda t: 'Direita' in t),
        }, index=df.index)
        data['polarized'] = data['esquerda'] | data['direita']

        keys = df[group_col] if group_col else pd.Series('Geral', index=df.index)
        grouped = data.groupby(keys).agg(
            total_comments=('polarized', 'size'),
            esquerda=('esquerda', 'sum'),
            direita=('direita', 'sum'),
            polarized=('polarized', 'sum'),
        )
        grouped['esquerda_pct'] = grouped['esquerda'] / grouped['total_comments'] * 100
        grouped['direita_pct'] = grouped['direita'] / grouped['total_comments'] * 100
        grouped['polarized_pct'] = grouped['polarized'] / grouped['total_comments'] * 100
        attacks = grouped['esquerda'] + grouped['direita']
        grouped['balance'] = np.where(attacks > 0, (grouped['esquerda'] - grouped['direita']) / attacks.where(attacks > 0, 1), 0.0)
        return grouped.reset_index().rename(columns={'index': group_col or 'grupo'})

    @staticmethod
    def sentiment_aggression_test(df):
        """
        Teste qui-quadrado de independência entre sentimento e agressividade,
        com V de Cramér como medida de tamanho de efeito (relevância prática).
        """
        valid = df[df['sentiment'].isin(['Positivo', 'Neutro', 'Negativo'])]
        table = pd.crosstab(valid['sentiment'], valid['is_aggressive'].astype(bool))
        if table.shape[0] < 2 or table.shape[1] < 2:
            return None

        chi2, p_value, dof, _ = stats.chi2_contingency(table)
        n = table.values.sum()
        cramers_v = np.sqrt(chi2 / (n * (min(table.shape) - 1)))
        aggr_by_sentiment = (table[True] / table.sum(axis=1) * 100) if True in table.columns else None
        return {
            "table": table,
            "chi2": chi2,
            "p_value": p_value,
            "dof": dof,
            "n": int(n),
            "cramers_v": cramers_v,
            "aggression_rate_by_sentiment": aggr_by_sentiment,
        }

    @staticmethod
    def correlation_with_pvalues(df_numeric):
        """Correlação de Spearman entre pares de variáveis, com p-valores."""
        cols = df_numeric.columns
        rows = []
        for i, a in enumerate(cols):
            for b in cols[i + 1:]:
                pair = df_numeric[[a, b]].dropna()
                if len(pair) < 3 or pair[a].nunique() < 2 or pair[b].nunique() < 2:
                    continue
                rho, p = stats.spearmanr(pair[a], pair[b])
                rows.append({"Variável A": a, "Variável B": b, "rho (Spearman)": rho, "p-valor": p, "n": len(pair)})
        return pd.DataFrame(rows)

    @staticmethod
    def interpret_effect_size(value):
        """Classificação convencional (Cohen) para |r| ou V de Cramér."""
        v = abs(value)
        if v < 0.1:
            return "desprezível"
        if v < 0.3:
            return "fraco"
        if v < 0.5:
            return "moderado"
        return "forte"
