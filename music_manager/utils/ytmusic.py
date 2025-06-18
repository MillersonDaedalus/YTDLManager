# utils/ytmusic.py
from django.core.exceptions import ObjectDoesNotExist
from ytmusicapi import YTMusic
from django.conf import settings
from music_manager.models import YtmusicAuth, YTMusicAuthError

#class YTMusicManager:
#    @classmethod
#    def get_authenticated_client(cls, user):
#        oauth_path = settings.YT_MUSIC_OAUTH_FILE / f'oauth_{user.id}.json'
#
#        if not oauth_path.exists():
#            raise FileNotFoundError("YouTube Music OAuth file not found. Please setup authentication first.")
#
#        return YTMusic(oauth_path)
#
#    @classmethod
#    def has_authentication(cls, user):
#        oauth_path = settings.YT_MUSIC_OAUTH_FILE / f'oauth_{user.id}.json'
#        return oauth_path.exists()



def get_user_ytmusic_client(user):
    """
    Helper function to get a YTMusic client for a given user
    """
    try:
        auth = YtmusicAuth.objects.get(user=user)
        return auth.get_ytmusic_client()
    except ObjectDoesNotExist:
        raise YTMusicAuthError("User has not set up YTMusic authentication")
    except Exception as e:
        raise YTMusicAuthError(f"Error getting YTMusic client: {str(e)}")