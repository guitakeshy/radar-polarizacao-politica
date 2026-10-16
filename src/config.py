import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env, se existir
load_dotenv()

class Config:
    """Configurações da aplicação."""
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/radar_politico.db")
    # Banco publicado no site: só resultados, sem o texto dos comentários (gerado por export_public_db.py)
    PUBLIC_DATABASE_URL = os.getenv("PUBLIC_DATABASE_URL", "sqlite:///data/radar_publico.db")
    MAX_RESULTS_PER_SEARCH = int(os.getenv("MAX_RESULTS_PER_SEARCH", "50"))
    MAX_COMMENTS_PER_VIDEO = int(os.getenv("MAX_COMMENTS_PER_VIDEO", "200"))
    
    # NLP Model configs
    SENTIMENT_MODEL = "nlptown/bert-base-multilingual-uncased-sentiment"
    ZERO_SHOT_MODEL = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

    @classmethod
    def is_api_key_configured(cls):
        return bool(cls.YOUTUBE_API_KEY and cls.YOUTUBE_API_KEY != "sua_chave_de_api_aqui")

    @classmethod
    def is_public_mode(cls):
        """
        Modo público (somente leitura): esconde a coleta de dados.
        Ativado com PUBLIC_MODE=1 ou automaticamente quando não há chave da API
        (como na hospedagem pública, onde o .env não é enviado).
        """
        explicit = os.getenv("PUBLIC_MODE", "").strip().lower()
        if explicit in ("1", "true", "sim"):
            return True
        if explicit in ("0", "false", "nao", "não"):
            return False
        return not cls.is_api_key_configured()

    @classmethod
    def get_database_url(cls):
        return cls.PUBLIC_DATABASE_URL if cls.is_public_mode() else cls.DATABASE_URL
