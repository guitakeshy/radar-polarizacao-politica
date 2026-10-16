import os
from sqlalchemy import create_engine, inspect, text, Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from src.config import Config

Base = declarative_base()

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    channel_title = Column(String)
    published_at = Column(DateTime)
    description = Column(Text)
    search_term = Column(String)
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    comments = relationship("Comment", back_populates="video", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(String, primary_key=True)
    video_id = Column(String, ForeignKey('videos.id'))
    text_original = Column(Text, nullable=False)
    text_cleaned = Column(Text)
    published_at = Column(DateTime)
    parent_id = Column(String, nullable=True) # Para respostas
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    # Resultados de NLP
    sentiment = Column(String) # Positivo, Neutro, Negativo, Inconclusivo
    sentiment_score = Column(Float)
    is_aggressive = Column(Boolean, default=False)
    aggression_categories = Column(String) # JSON de categorias identificadas

    # Resultados derivados do texto, guardados para o banco público (que não contém o texto)
    camp_targets = Column(String)  # JSON: campos políticos atacados com rótulos pejorativos
    text_length = Column(Integer)

    video = relationship("Video", back_populates="comments")

class Database:
    def __init__(self, db_url=None):
        db_url = db_url or Config.get_database_url()
        # Garante que o diretório data/ exista se for sqlite
        if db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self._add_missing_columns()
        self.Session = sessionmaker(bind=self.engine)

    def _add_missing_columns(self):
        """Migração simples: create_all não adiciona colunas novas a tabelas que já existem."""
        existing = {col['name'] for col in inspect(self.engine).get_columns('comments')}
        with self.engine.begin() as conn:
            for column in Comment.__table__.columns:
                if column.name not in existing:
                    conn.execute(text(f'ALTER TABLE comments ADD COLUMN {column.name} {column.type.compile(self.engine.dialect)}'))

    def get_session(self):
        return self.Session()
