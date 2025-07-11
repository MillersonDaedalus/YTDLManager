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





def check_for_albums(artist, type='albums'):
    if type in artist:
        return True
    else:
        return False

def check_for_params(artist, type='albums'):
    if check_for_albums(artist):
        if 'params' in artist[type]:
            return True
    else:
        return False

def get_albums(artist, type='albums'):
    if type == 0:
        check = 'albums'
    elif type == 1:
        check = 'singles'
    else:
        raise ValueError('type must be either 0, or 1')

    if check_for_albums(artist):
        if check_for_params(artist):
            albums = ytmusic.get_artist_albums(artist[check]['browseId'],artist[check]['params'])
        else:
            albums = artist[check]['results']
    else:
        albums = []
    return albums

def check_for_params(artist, type='albums'):
    if type == 0:
        check = 'albums'
    elif type == 1:
        check = 'singles'
    else:
        raise ValueError('type must be either 0, or 1')

    if check_for_albums(artist):
        if 'params' in artist[check]:
            return True
    else:
        return False

def get_number_albums(artist, type='albums'):
    amount = len(get_albums(artist, type))
    return amount