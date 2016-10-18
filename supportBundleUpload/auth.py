from boxsdk import OAuth2
import shelve

oauth = OAuth2(
    client_id='riwciru4xorb8p8ouddnq9yt9m75zvxp',
    client_secret='3AQsuW6GaK0TPYIqy5TFCcwijrzzP2ye',
    store_tokens=your_store_tokens_callback_method,
)

auth_url, csrf_token = oauth.get_authorization_url('http://0.0.0.0')

def store_tokens(access_token, refresh_token):
    # store the tokens at secure storage (e.g. Keychain)
    d.shelve =  sleve.open("db.shlv")
    d["access_token"]=access_token
    d["refresh_token"]=refresh_token
    d.close()

