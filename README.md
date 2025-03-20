[![MIT License](https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge&logo=law)](https://opensource.org/licenses/MIT)
[![Donate with PayPal](https://img.shields.io/badge/Donate-PayPal-0070ba?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/kkqq9320)
[![Buy Me a Coffee](https://img.shields.io/badge/☕%20Buy%20Me%20a%20Coffee-orange?style=for-the-badge)](https://www.buymeacoffee.com/kkqq9320)

> [!NOTE]
Thanks to [matt8707](https://github.com/matt8707), I made this project based on [youtube-watching](https://github.com/matt8707/youtube-watching)
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
