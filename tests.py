import ytmusicapi
import os
from dotenv import load_dotenv

load_dotenv()

YTMUSIC_client_id=os.getenv('YTMUSIC_CLIENT_ID')
YTMUSIC_client_secret=os.getenv('YTMUSIC_CLIENT_SECRET')

ytmusicapi.setup_oauth(client_id=YTMUSIC_client_id, client_secret=YTMUSIC_client_secret, filepath="\oaut\hfilename.json", open_browser=True)