import ytmusicapi
import os
from dotenv import load_dotenv
from ytmusicapi import OAuthCredentials

load_dotenv()

YTMUSIC_client_id=os.getenv('YTMUSIC_CLIENT_ID')
YTMUSIC_client_secret=os.getenv('YTMUSIC_CLIENT_SECRET')

ytmusic = ytmusicapi.YTMusic("ytmusic_auth/1/oauth.json", oauth_credentials=OAuthCredentials(YTMUSIC_client_id,YTMUSIC_client_secret))


def search_artist(channelId):
    results = ytmusic.get_library_subscriptions(limit=5)

    for i in results[:2]:
        #print(i['browseId'])
        result = ytmusic.get_artist(i['browseId'])
        for i in result:

            if type(result[i]) == dict:
                print(i,':')
                for l in result[i]:
                    #print(type(result[i][l]))
                    if type(result[i][l]) == list:
                        print('\t',l,':')
                        for n in range(len(result[i][l])):
                            print('\t\t', result[i][l][n])
                    else:
                        print('\t',l,':',result[i][l])

            else:
                print(i,':',result[i])

        #albums = ytmusic.get_artist(result['channelId'],)

def print_artist(channelId):
    artist = ytmusic.get_artist(channelId)

    for i in artist:

        if type(artist[i]) == dict:
            print(i, ':')
            for l in artist[i]:
                # print(type(artist[i][l]))
                if type(artist[i][l]) == list:
                    print('\t', l, ':')
                    for n in range(len(artist[i][l])):
                        print('\t\t', artist[i][l][n])
                else:
                    print('\t', l, ':', artist[i][l])

        else:
            print(i, ':', artist[i])

def check_for_albums(artist, type='albums'):
    return type in artist

def get_albums(artist, type='albums'):
    if check_for_albums(artist):
        if check_for_params(artist):
            albums = ytmusic.get_artist_albums(artist[type]['browseId'],artist[type]['params'])
        else:
            albums = artist[type]['results']
    else:
        albums = []
    return albums



def check_for_params(artist, type='albums'):
    return check_for_albums(artist) and 'params' in artist[type]



def get_number_albums(artist, type='albums'):
    amount = len(get_albums(artist, type))
    return amount

def data_gather():
    subs = ytmusic.get_library_subscriptions()

    Data = []
    for sub in subs:
        artist_info = ytmusic.get_artist(sub['browseId'])

        artist = Artist(artist_info)

        print(artist.name,artist.album_params,artist.singles_params)

        #print(artist['name'],'appended')

    return Data


def get_discography(artist_id):
    artist = ytmusic.get_artist(artist_id)

    if check_for_albums(artist):
        if check_for_params(artist):
            print(get_number_albums(artist))


        print(len(artist['albums']['results']))

#johnnycash = ytmusic.get_artist('UCiGs21G3KeE2tpbbMPzn9Qg')
#print(check_for_params(johnnycash))
#ghost = ytmusic.get_artist('UC08qAR-kyTJb8Xjwbo6C7ZQ')
#print(check_for_params(ghost))

if __name__ == "__main__":
    #data = data_gather()
    #for i in data:
        #print(i)
    #print_artist('UCPKWE1H6xhxwPlqUlKgHb_w')

    #artist = ytmusic.get_artist('UCPKWE1H6xhxwPlqUlKgHb_w')

    #if artist['albums']['browseId'] is None: print(True)
    #else: print(False)



    #print(ytmusic.get_artist_albums('MPADUCaapER5lCD-70_lAuf05RyQ','ggMHegUIAhoBAg%3D%3D'))
    #print_artist('UC4LjKAw10u60_hifadhaPiw')
    #print_artist('UC08qAR-kyTJb8Xjwbo6C7ZQ')
    """
    ghost = ytmusic.get_artist('UC08qAR-kyTJb8Xjwbo6C7ZQ')
    #print(ghost)

    albums = []
    if check_for_albums(ghost) and check_for_params(ghost):
        albums.extend(ytmusic.get_artist_albums(ghost['album']['browseId'], ghost['album']['params']))
    else:
        if 'albums' in ghost:
            albums.extend(ghost['albums']['results'])
    if check_for_albums(ghost, 'singles') and check_for_params(ghost, 'singles'):
        albums.extend(ytmusic.get_artist_albums(ghost['singles']['browseId'], ghost['singles']['params']))
    else:
        if 'singles' in ghost:
            albums.extend(ghost['singles']['results'])

    print(albums)

    for album in albums:
        print(album)
        print(ytmusic.get_album(album['browseId']))
    """

    #skeleta = ytmusic.get_album('MPREb_3IOalARxXic')
    #for i in skeleta:
        #print(i,':',skeleta[i])
    #satanized = ytmusic.get_album('MPREb_FY7r4dEOWDs')
    #for i in satanized:
    #    print(i,':',satanized[i])




    print(ytmusic.get_artist('UCKxC9ral9fIJnX07mErNHYw'))