import json
import re
import requests
from http.cookiejar import MozillaCookieJar

import mqttapi as mqtt

class YouTubeThumbnail(mqtt.Mqtt):

    def initialize(self):
        self.LOGLEVEL = "DEBUG"

        self.MEDIA = self.args.get("apple_tv_entity_id")
        self.COOKIES_URL = self.args.get("cookies_url") 
        
        # MQTT topic variables
        self.youtube_thumbnail_topic = "appdaemon/youtube_thumbnail"
        self.youtube_thumbnail_status_topic = "appdaemon/youtube_thumbnail/status"

        # Discovery topic for HASS
        self.discovery_topic = "homeassistant/sensor/youtube_thumbnail/config"
        self.binary_discovery_topic = "homeassistant/binary_sensor/youtube_cookies_status/config"

        self.listen_state(self.youtube_history_callback, self.MEDIA, new="playing")
        self.log("Media player playing", level=self.LOGLEVEL)

    def publish_mqtt_discovery_config(self):
        # for watching sensor
        config_payload = {
            "name": "Watching",
            "state_topic": self.youtube_thumbnail_topic,
            "json_attributes_topic": self.youtube_thumbnail_topic,
            "unique_id": "youtube_watching",
            "object_id": "youtube_watching",
            "value_template": "{{ value_json.thumbnail }}", 
            "retain": True,
            "device": {
                "identifiers": ["youtube_thumbnail"],
                "name": "Youtube Thumbnail",
                "manufacturer": "Appdaemon",
                "model": "Thumbnail"
            }
        }
    
        self.mqtt_publish(self.discovery_topic, json.dumps(config_payload), retain=True)
        self.log("Published MQTT discovery config for YouTube Watching sensor", level=self.LOGLEVEL)

    def publish_binary_sensor_discovery_config(self):
        # Cookie expiration status
        binary_config_payload = {
            "name": "Cookies Status",
            "state_topic": self.youtube_thumbnail_status_topic,
            "value_template": "{{ value_json.cookies }}",
            "payload_on": "True",
            "payload_off": "False",
            "unique_id": "youtube_cookies_status",
            "object_id": "youtube_cookies_status",
            "device_class": "connectivity",
            "retain": True,
            "device": {
                "identifiers": ["youtube_thumbnail"],
                "name": "Youtube Thumbnail",
                "manufacturer": "Appdaemon",
                "model": "Thumbnail"
            }
        }
        self.mqtt_publish(self.binary_discovery_topic, json.dumps(binary_config_payload), retain=True)
        self.log("Published MQTT discovery config for YouTube Cookies Status binary sensor", level=self.LOGLEVEL)

    def youtube_history_callback(self, entity, attribute, old, new, kwargs):
        app_id = self.get_state(self.MEDIA, attribute="app_id")
        media_title = self.get_state(self.MEDIA, attribute="media_title")
        sensor_title = self.get_state("sensor.youtube_watching", attribute="title")

        if app_id == "com.google.ios.youtube" and media_title != sensor_title:
            self.log("Condition true; YouTube history updated", level=self.LOGLEVEL)
            self.fetch_youtube_history()
            self.publish_mqtt_discovery_config()
        else:
            self.log("No need to update state, stop .py", level=self.LOGLEVEL)

    def fetch_youtube_history(self):
        COOKIES_FILE = self.COOKIES_URL
        cookie_jar = MozillaCookieJar(COOKIES_FILE)
        try:
            cookie_jar.load(ignore_discard=True, ignore_expires=True)
        except OSError as notfound_error:
            self.error(f"WARNING: {COOKIES_FILE} not found. DEBUG: {notfound_error}")
            return

        session = requests.Session()
        session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
            "Sec-Fetch-Mode": "navigate",
        }
        session.cookies = cookie_jar

        try:
            response = session.get("https://www.youtube.com/feed/history")
        except requests.exceptions.RequestException as req_err:
            self.error(f"WARNING: YouTube Request Error: {req_err}")
            return

        cookie_jar.save(ignore_discard=True, ignore_expires=True)
        html = response.text

        # ytInitialData JSON Parsing
        try:
            REGEX = r"var ytInitialData\s*=\s*(\{.*?\});"
            match = re.search(REGEX, html, re.DOTALL)
            if not match:
                raise AttributeError("Couldn't find ytInitialData JSON in the page source.")

            json_str = match.group(1)
            data = json.loads(json_str)

            path = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"] \
                       ["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]

        except (AttributeError, json.JSONDecodeError) as e:
            self.error(f"WARNING: Can't parse ytInitialData JSON. DEBUG: {e}")
            return

        # MQTT Discovery binary_sensor
        self.publish_binary_sensor_discovery_config()

        def thumbnail(fid):
            url = f"https://img.youtube.com/vi/{fid}"
            maxres = f"{url}/maxresdefault.jpg"
            default = f"{url}/0.jpg"
            try:
                if requests.get(maxres, timeout=3).status_code == 200:
                    return maxres
            except requests.exceptions.RequestException as req_err:
                self.error(f"WARNING: thumbnail request error: {req_err}")
            return default

        video_renderer = None
        for item in path:
            if "videoRenderer" in item:
                video_renderer = item["videoRenderer"]
                break
        
        if video_renderer is None:
            self.error("No videoRenderer found in the YouTube data path")
            # Issue cookies status as False to turn off binary_sensor status
            self.mqtt_publish(self.youtube_thumbnail_status_topic, json.dumps({"cookies": "False"}), retain=True)
            return
        else:
            # binary_sensor is turned on if cookies status is True
            self.mqtt_publish(self.youtube_thumbnail_status_topic, json.dumps({"cookies": "True"}), retain=True)

        output = {
            "channel": video_renderer.get("longBylineText", {}).get("runs", [{}])[0].get("text", "N/A"),
            "title": video_renderer.get("title", {}).get("runs", [{}])[0].get("text", "N/A"),
            "video_id": video_renderer.get("videoId", "N/A"),
            "duration_string": video_renderer.get("lengthText", {}).get("simpleText", "N/A"),
            "thumbnail": thumbnail(video_renderer.get("videoId", "")),
            "original_url": f'https://www.youtube.com/watch?v={video_renderer.get("videoId", "")}',
        }

        self.mqtt_publish(self.youtube_thumbnail_topic, json.dumps(output), retain=True)
