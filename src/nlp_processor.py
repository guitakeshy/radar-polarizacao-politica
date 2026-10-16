import re
import logging
from src.config import Config
from src.lexicon import detect_aggression


class NLPProcessor:
    def __init__(self):
        self._sentiment_pipeline = None
        self._load_failed = False

    @property
    def sentiment_pipeline(self):
        # Carregamento preguiçoso: só baixa/carrega o modelo quando for realmente usado
        if self._sentiment_pipeline is None and not self._load_failed:
            try:
                from transformers import pipeline
                # Modelo multilíngue leve; retorna de 1 a 5 stars.
                self._sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model=Config.SENTIMENT_MODEL,
                    truncation=True,
                    max_length=512
                )
            except Exception as e:
                logging.error(f"Erro ao carregar modelo de NLP: {e}")
                self._load_failed = True
        return self._sentiment_pipeline

    def clean_text(self, text):
        if not text:
            return ""
        # Remove quebras de linha excessivas e espaços múltiplos
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def _label_to_sentiment(result):
        # nlptown model labels: '1 star' to '5 stars'
        stars = int(result['label'].split()[0])
        score = result['score']

        if stars <= 2:
            return "Negativo", score
        if stars == 3:
            return "Neutro", score
        return "Positivo", score

    def analyze_sentiment(self, text):
        return self.analyze_sentiments([text])[0]

    def analyze_sentiments(self, texts, batch_size=32):
        """Analisa vários textos de uma vez (muito mais rápido que um a um)."""
        results = [("Inconclusivo", 0.0)] * len(texts)
        valid = [(i, t) for i, t in enumerate(texts) if t and len(t) >= 3]
        if not valid or not self.sentiment_pipeline:
            return results

        try:
            outputs = self.sentiment_pipeline([t for _, t in valid], batch_size=batch_size)
            for (i, _), out in zip(valid, outputs):
                results[i] = self._label_to_sentiment(out)
        except Exception as e:
            logging.error(f"Erro na análise de sentimento: {e}")
        return results

    def analyze_aggression(self, text):
        """
        Classifica sinais de agressividade usando heurísticas baseadas no contexto político brasileiro.
        Não sendo um modelo de machine learning treinado especificamente para isso,
        utiliza dicionários de palavras-chave (ver src/lexicon.py) para identificar possíveis sinais.
        """
        return detect_aggression(text)

    def process_comment(self, text):
        return self.process_comments([text])[0]

    def process_comments(self, texts):
        cleaned = [self.clean_text(t) for t in texts]
        sentiments = self.analyze_sentiments(cleaned)

        results = []
        for cleaned_text, (sentiment, score) in zip(cleaned, sentiments):
            is_aggressive, categories = self.analyze_aggression(cleaned_text)
            results.append({
                "cleaned_text": cleaned_text,
                "sentiment": sentiment,
                "sentiment_score": score,
                "is_aggressive": is_aggressive,
                "aggression_categories": categories
            })
        return results
