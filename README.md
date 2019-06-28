
# Installation for development

```
pipenv install --dev
```

Copy `config_example.py` to `config.py` and fill in the values (see below for how to obtain the strava config).
Create a file `persist/strava_refresh_token`:

```bash
mkdir persist
persist/strava_refresh_token
```

# Initial setup of strava api token

Create api token at https://www.strava.com/settings/api

Set the obtained client id and client secret in `config.py`.

The token needs read_all access. To get that, go to the following link (replace YOUR_CLIENT_ID and
YOUR_URL with the appropriate values for your api):
https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_URL&response_type=code&approval_prompt=force&scope=read_all

The code that you get can be used with `strava.tokens.authorize_with_code`, in an ipython session:

```Python
import strava.tokens
strava.tokens.authorize_with_code('YOUR_CODE')
```

Check that a refresh token has been written to `persist/strava_refresh_token`. You're good to go!

