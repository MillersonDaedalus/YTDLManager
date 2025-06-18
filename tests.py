import ytmusicapi
import os
from dotenv import load_dotenv
from ytmusicapi import OAuthCredentials

load_dotenv()

YTMUSIC_client_id=os.getenv('YTMUSIC_CLIENT_ID')
YTMUSIC_client_secret=os.getenv('YTMUSIC_CLIENT_SECRET')

ytmusic = ytmusicapi.YTMusic("ytmusic_auth/1/oauth.json", oauth_credentials=OAuthCredentials(YTMUSIC_client_id,YTMUSIC_client_secret))

def get_artists():
    Artists = ytmusic.get_library_subscriptions(limit=500)

    for i in Artists:
        print(i)

def search_artist():
    results = ytmusic.get_library_subscriptions(limit=5)

    for i in results[:2]:
        #print(i['browseId'])
        result = ytmusic.get_artist(i['browseId'])
        for i in result:
            print(i,result[i])
        #albums = ytmusic.get_artist(result['channelId'],)


if __name__ == "__main__":
    search_artist()



