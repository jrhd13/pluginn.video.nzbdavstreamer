import sys
import urllib.parse
import urllib.request
import json
import base64
import xbmc
import xbmcgui
import xbmcplugin

# ==========================================
# 🚨 YOUR EASYNEWS CREDENTIALS 🚨
# ==========================================
EASYNEWS_USER = "fmhamqhuti"
EASYNEWS_PASS = "iyzu-ypvt-nnzo"

# Kodi passes these hidden variables to our script
addon_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])

def build_main_menu():
    list_item = xbmcgui.ListItem(label="🎬 Search Easynews")
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=addon_url + "?action=search", listitem=list_item, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def search_easynews():
    keyboard = xbmc.Keyboard('', 'Enter Movie Name:')
    keyboard.doModal()
    
    if keyboard.isConfirmed() and keyboard.getText():
        search_term = keyboard.getText()
        fetch_and_display_results(search_term)

def fetch_and_display_results(search_term):
    query = urllib.parse.quote_plus(search_term)
    api_url = f"https://members.easynews.com/2.0/search/solr-search/advanced?gps={query}&pno=1&fty[]=VIDEO"
    
    try:
        auth_string = f"{EASYNEWS_USER}:{EASYNEWS_PASS}"
        base64_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        
        req = urllib.request.Request(api_url)
        req.add_header("Authorization", f"Basic {base64_auth}")
        req.add_header("User-Agent", "Mozilla/5.0")
        
        response = urllib.request.urlopen(req)
        raw_data = response.read().decode('utf-8', errors='ignore')
        
        data = json.loads(raw_data)
        items = data.get('data', [])
        
        if len(items) == 0:
            xbmcgui.Dialog().notification('Easynews', 'No movies found.', xbmcgui.NOTIFICATION_INFO, 3000)
            return

        for item in items:
            # 1. Grab the EXACT keys we found in your screenshots!
            hash_val = item.get('hash', '')
            id_val = item.get('id', '')
            fn = item.get('fn', 'Unknown')
            ext = item.get('extension', '.mkv')

            # If it's missing the security hash, we can't play it
            if not hash_val or not id_val:
                continue

            # 2. Build the pristine file name and the bulletproof streaming URL
            filename = f"{fn}{ext}"
            safe_filename = urllib.parse.quote(filename)
            
            # This is the gold-standard Easynews direct download structure
            video_link = f"https://members.easynews.com/d/{hash_val}/{id_val}/{safe_filename}"

            # 3. Present it beautifully in the Kodi menu
            list_item = xbmcgui.ListItem(label=fn)
            list_item.setInfo('video', {'title': fn})
            list_item.setProperty('IsPlayable', 'true')
            
            play_url = f"{addon_url}?action=play&video={urllib.parse.quote_plus(video_link)}"
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=play_url, listitem=list_item, isFolder=False)
        
        xbmcplugin.endOfDirectory(addon_handle)

    except Exception as e:
        xbmcgui.Dialog().notification('Search Error', str(e), xbmcgui.NOTIFICATION_ERROR, 5000)

def play_video(video_link):
    xbmcgui.Dialog().notification('Easynews', 'Starting Stream...', xbmcgui.NOTIFICATION_INFO, 2000)

    try:
        # 1. Properly inject credentials into the URL
        clean_url = video_link.replace('https://', '').replace('http://', '')
        safe_user = urllib.parse.quote_plus(EASYNEWS_USER)
        safe_pass = urllib.parse.quote_plus(EASYNEWS_PASS)
        
        # 2. Add the User-Agent "Cheat Code" at the end of the URL
        # This tells Kodi to pretend it's a web browser, which Easynews requires!
        stream_url = f"https://{safe_user}:{safe_pass}@{clean_url}|User-Agent=Mozilla/5.0"

        # 3. Create the playable item and FORCE the mime-type
        play_item = xbmcgui.ListItem(path=stream_url)
        play_item.setInfo('video', {})
        
        # This tells Kodi: "I don't care what you think this is, PLAY IT as video."
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

    except Exception as e:
        xbmcgui.Dialog().notification('Playback Error', str(e), xbmcgui.NOTIFICATION_ERROR, 5000)
def router():
    action = args.get('action', [None])[0]
    
    if action == 'search':
        search_easynews()
    elif action == 'play':
        video_link = args.get('video', [''])[0]
        play_video(video_link)
    else:
        build_main_menu()

if __name__ == '__main__':
    router()