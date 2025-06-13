# utils/ytmusic.py
from ytmusicapi import YTMusic
from django.conf import settings


class YTMusicManager:
    @classmethod
    def get_authenticated_client(cls, user):
        oauth_path = settings.YT_MUSIC_OAUTH_FILE / f'oauth_{user.id}.json'

        if not oauth_path.exists():
            raise FileNotFoundError("YouTube Music OAuth file not found. Please setup authentication first.")

        return YTMusic(oauth_path)

    @classmethod
    def has_authentication(cls, user):
        oauth_path = settings.YT_MUSIC_OAUTH_FILE / f'oauth_{user.id}.json'
        return oauth_path.exists()