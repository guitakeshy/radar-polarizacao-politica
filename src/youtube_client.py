import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from src.config import Config

class YouTubeClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.YOUTUBE_API_KEY
        if not self.api_key:
            raise ValueError("YouTube API Key não configurada.")
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def search_videos(self, query, max_results=50, published_after=None, published_before=None, order="relevance"):
        """Pesquisa vídeos no YouTube."""
        try:
            request = self.youtube.search().list(
                q=query,
                part='id,snippet',
                type='video',
                maxResults=min(max_results, 50),
                relevanceLanguage='pt',
                regionCode='BR',
                order=order,
                publishedAfter=published_after,
                publishedBefore=published_before
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                videos.append({
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'description': item['snippet']['description'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                })
            return videos
            
        except HttpError as e:
            print(f"Erro na API do YouTube ao pesquisar vídeos: {e}")
            return []

    def get_comments(self, video_id, max_comments=200):
        """Coleta comentários de um vídeo específico."""
        comments = []
        try:
            request = self.youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=100,
                textFormat="plainText"
            )
            
            while request and len(comments) < max_comments:
                response = request.execute()
                
                for item in response.get("items", []):
                    top_comment = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "id": item["id"],
                        "video_id": video_id,
                        "text": top_comment["textDisplay"],
                        "published_at": top_comment["publishedAt"],
                        "parent_id": None
                    })
                    
                    # Limita respostas se já atingiu o máximo
                    if len(comments) >= max_comments:
                        break
                        
                    # Coleta respostas, se houver
                    if "replies" in item:
                        for reply in item["replies"]["comments"]:
                            reply_snippet = reply["snippet"]
                            comments.append({
                                "id": reply["id"],
                                "video_id": video_id,
                                "text": reply_snippet["textDisplay"],
                                "published_at": reply_snippet["publishedAt"],
                                "parent_id": item["id"]
                            })
                            if len(comments) >= max_comments:
                                break
                                
                request = self.youtube.commentThreads().list_next(request, response)
                
            return comments
            
        except HttpError as e:
            # Erro comum: Comentários desativados
            if e.resp.status == 403 and "commentsDisabled" in str(e.content):
                print(f"Comentários desativados para o vídeo {video_id}.")
            else:
                print(f"Erro na API do YouTube ao coletar comentários: {e}")
            return []
