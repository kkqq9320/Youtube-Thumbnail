[![MIT License](https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge&logo=law)](https://opensource.org/licenses/MIT)
[![Donate with PayPal](https://img.shields.io/badge/Donate-PayPal-0070ba?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/kkqq9320)
[![Buy Me a Coffee](https://img.shields.io/badge/☕%20Buy%20Me%20a%20Coffee-orange?style=for-the-badge)](https://www.buymeacoffee.com/kkqq9320)

> [!NOTE]
Thanks to [matt8707](https://github.com/matt8707), I made this project based on [youtube-watching](https://github.com/matt8707/youtube-watching)

<details>

<summary><b>If you prefer not to depend on AppDaemon, or you want to add the `entity_picture` attribute to the Apple TV</b></summary>

  Check [this](https://community.home-assistant.io/t/creating-a-youtube-thumbnail-sensor-in-home-assistant/866552)

  1. A `cookies.txt` file is still required
  2. Your version of `yt-dlp` must be `2025.03.31` or later. Even if your Home Assistant core version is `2025.4.1`, you still need to update it.

     2-1. Log in to the console window. It’s not an ssh addon or putty!

     2-2. Run `login`

     2-3. Run `docker exec -it homeassistant /bin/bash`

     2-4. Run `pip install -U yt-dlp`

     2-5. Run `python3 -c "import yt_dlp; print(yt_dlp.version.__version__)"` (Verify that the update is complete. If it outputs 2025.03.31, then it’s OK.)

  3. In the `/config(homeassistant)/python(any folder name)/`, create two files: `youtube_thumbnail.py` and `set_entity_picture.py`.
  4. Insert the following code into `youtube_thumbnail.py`:
```
import json

URL = "https://www.youtube.com/feed/history"

ydl_opts = {
   "cookiefile": "/config/python/.cookies.txt",
   "skip_download": True,
   "playlist_items": "1",
   "quiet": True,
   "no_warnings": True,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
   info = ydl.extract_info(URL, download=False)
   data = ydl.sanitize_info(info)
   entry = data.get("entries", [data])[0]
   print(
       json.dumps(
           {
               "channel": entry.get("channel"),
               "title": entry.get("fulltitle"),
               "video_id": entry.get("id"),
               "thumbnail": entry.get("thumbnail"),
               "original_url": entry.get("original_url"),
           },
           indent=2,
       )
   )
```
  5. Insert the following code into set_entity_picture.py:
    But I found that from secrets import get_secret didn’t work, so I just put the `TOKEN` and `HOST` right in.
```
import argparse
import requests
from secrets import get_secret

HOST = get_secret("ha_host")
TOKEN = get_secret("ha_token")


def update_entity_picture(entity_id, entity_picture):
    url = f"{HOST}/api/states/{entity_id}"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        data["attributes"]["entity_picture"] = entity_picture
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("ok")
        else:
            print("Error posting update: ", response.text)
    else:
        print("Error retrieving state: ", response.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="update entity_picture")
    parser.add_argument("--entity_id", required=True, help="entity_id")
    parser.add_argument("--entity_picture", required=True, help="entity_picture")
    args = parser.parse_args()
    update_entity_picture(args.entity_id, args.entity_picture)
```
  6. Add the following `command_line` sensor to `/config/configuration.yaml:`
```
command_line:
  - sensor:
      name: youtube_thumbnail
      command: "python3 /config/python/youtube_thumbnail.py"
      value_template: "{{ value_json.thumbnail }}"
      json_attributes:
        - channel
        - title
        - video_id
        - thumbnail
        - original_url
      scan_interval: 86400
```

  7. Add the following shell_command to `/config/configuration.yaml:`
```
shell_command:
  set_entity_picture: "python3 /config/python/set_entity_picture.py --entity_id '{{ entity_id }}' --entity_picture '{{ entity_picture }}'"
```
  8. Create an automation.
```
alias: Set youtube entity_picture
triggers:
  - trigger: state
    entity_id:
      - media_player.sovrum
      - media_player.vardagsrum
    to:
      - playing
      - paused
conditions:
  - condition: template
    value_template: >
      {% set entity_id = trigger.entity_id %}
      {% set youtube = 'sensor.youtube_thumbnail' %}

      {{ is_state_attr(entity_id, 'app_id', 'com.google.ios.youtube')
      and (state_attr(entity_id, 'media_artist') != state_attr(youtube, 'channel')) 
      and (state_attr(entity_id, 'media_title') != state_attr(youtube, 'title')) }}
actions:
  - action: homeassistant.update_entity
    data:
      entity_id:
        - sensor.youtube_thumbnail
  - action: shell_command.set_entity_picture
    data:
      entity_id: >
        {{ trigger.entity_id }}
      entity_picture: >
        {{ states('sensor.youtube_thumbnail') }}
mode: single
```
  9. It’s done. Now, when you play or pause the Apple TV, the `media_player.apple_tv (used as a trigger in the automation)` will have an `entity_picture` attribute.


</details>


# Youtube-Thumbnail

Make a thumbnail of a recently watched youtube video on apple tv as a homeassistant sensor 



## Prerequisites
#### Homeassistant
- You need an [MQTT integration](https://www.home-assistant.io/integrations/mqtt/) for `MQTT discovery` and a server running the `MQTT broker`.
#### Cookies
- To authenticate with youtube, you need to set a HTTP Cookie File.
> In order to extract cookies from browser use any conforming browser extension for exporting cookies. For example, Get [cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) (for Chrome) or [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) (for Firefox).

> [!TIP] 
for `Chrome`
> 1. Open a new Incognito tab.
> 2. Open cookies.txt LOCALLY.
> 3. Export the cookies with Export Format: Netscape (You can also copy them if you prefer).
> 4. Close the Incognito tab.
> 5. Save the `.txt` file as `/homeassistant/.youtube_cookies.txt`

> [!WARNING]
If you do not obtain cookies in an incognito tab, the cookies may expire very quickly.















## Installation
Use [HACS](https://github.com/hacs/integration) or [Download](https://github.com/kkqq9320/Youtube-Thumbnail/releases) the `youtube_thumbnail.py` file from inside the `apps` directory to your local `apps` directory. then add the configuration to enable the `youtube_thumbnail` module.

### HACS 
1. To use appdaemon, you must make appdaemon visible in your HACS settings. [CHECK](https://www.hacs.xyz/docs/use/repositories/type/appdaemon/)
2. You can now see appdaemon in the `HACS` tab. go to `HACS` tab
3. Three dots in the upper right > custom repositories > <br>Add `https://github.com/kkqq9320/Youtube-Thumbnail` , type is `appdaemon`
4. Search `Youtube-Thumbnail` and install
5. If you're having trouble, [CHECK](https://www.hacs.xyz/docs/faq/custom_repositories/)
6. go to [Next step](#next-step)

### Manual
1. [Download](https://github.com/kkqq9320/Youtube-Thumbnail/releases) source code.zip and unzip.
2. go to [Next step](#next-step)

### Next step
**Choose only one.**
#### Change `app_dir:`
- Add `app_dir: /homeassistant/appdaemon/apps` on `appdaemon.yaml`

#### Copy `youtube_thumbnail.py` on default directory
1. Copy `Youtube-Thumbnail/apps/youtube_thumbnail.py` or `/homeassistant/appdaemon/apps/Youtube-Thumbnail/youtube_thumbnail.py`
1. Now you need to take this and paste it into your `addon_config` directory.
2. Paste file to `/addon_configs/a0d7b954_appdaemon/apps/`
3. `/addon_config` is one level above `/homeassistant` in the file structure.
[CHECK](https://github.com/hassio-addons/addon-appdaemon/releases/tag/v0.15.0)


## Appdamon configuration
> [!CAUTION]
Note: `/config` will not work. Use `/homeassistant` instead, as `/homeassistant = /config`.

### apps.yaml
key | required | type | default | description
-- | -- | -- | -- | --
`module` | Yes | string | youtube_thumbnail | The module name of the app.
`class` | Yes | string | YouTubeThumbnail | The name of the Class.
`apple_tv_entity_id` | Yes | string | `media_player.apple_tv` | Enter your Apple TV `entity ID`. Only one Apple TV is supported.
`cookies_url` | Yes | string | `/homeassistant/.youtube_cookies.txt` | Specify the path where you saved the `.txt` file.

```yaml
## apps.yaml
youtube_thumbnail:
  module: youtube_thumbnail
  class: YouTubeThumbnail
  apple_tv_entity_id: media_player.4k
  cookies_url: /homeassistant/.youtube_cookies.txt
```
## Supproted sensor types
### Cookies Status Binary Sensor
![image](https://github.com/user-attachments/assets/6a8c4ade-a0e6-4db5-b967-08925249956d)

### Watching Thumbnail Sensor
![image](https://github.com/user-attachments/assets/2ac8013a-035b-465f-886a-7f2957bf4f34)
  - Thumbnail URL
    - Channel
    - Title
    - Video ID
    - Duration String
    - Thumbnail
    - Original url
