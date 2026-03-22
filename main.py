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
    # Hitting the official Solr database API for video files
    api_url = f"https://members.easynews.com/2.0/search/solr-search/advanced?gps={query}&pno=1&fty[]=VIDEO"
    
    try:
        auth_string = f"{EASYNEWS_USER}:{EASYNEWS_PASS}"
        base64_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        
        req = urllib.request.Request(api_url)
        req.add_header("Authorization", f"Basic {base64_auth}")
        req.add_header("User-Agent", "Mozilla/5.0")
        
        response = urllib.request.urlopen(req)
        raw_data = response.read().decode('utf-8', errors='ignore')
        
        # 1. Parse the pure JSON response!
        data = json.loads(raw_data)
        
        # Easynews puts all the results in an array called 'data'
        items = data.get('data', [])
        
        # 2. Wiretap: Prove how many JSON items we grabbed
        xbmcgui.Dialog().notification('Easynews API', f'Found {len(items)} items!', xbmcgui.NOTIFICATION_INFO, 3000)

        for item in items:
            # 3. Grab the file's Hash (sig) and Name (al) straight from the database
            sig = item.get('sig', '')
            filename = item.get('al', 'Unknown.mkv')
            
            # Skip empty entries
            if not sig or not filename:
                continue

            # 4. Construct the bulletproof direct streaming URL
            safe_filename = urllib.parse.quote(filename)
            video_link = f"https://members.easynews.com/dl/{sig}/{safe_filename}"
            
            # Clean up the title for the Kodi menu
            clean_title = urllib.parse.unquote(filename)
                
            list_item = xbmcgui.ListItem(label=clean_title)
            list_item.setInfo('video', {'title': clean_title})
            list_item.setProperty('IsPlayable', 'true')
            
            play_url = f"{addon_url}?action=play&video={urllib.parse.quote_plus(video_link)}"
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=play_url, listitem=list_item, isFolder=False)
        
        xbmcplugin.endOfDirectory(addon_handle)

    except Exception as e:
        # If the JSON fails to parse, it will pop up here
        xbmcgui.Dialog().notification('Search Error', str(e), xbmcgui.NOTIFICATION_ERROR, 5000)

def play_video(video_link):
    xbmcgui.Dialog().notification('Easynews', 'Starting Stream...', xbmcgui.NOTIFICATION_INFO, 2000)

    try:
        # Bypass Kodi's network security by injecting your credentials right into the URL
        clean_url = video_link.replace('https://', '').replace('http://', '')
        safe_user = urllib.parse.quote_plus(EASYNEWS_USER)
        safe_pass = urllib.parse.quote_plus(EASYNEWS_PASS)
        
        stream_url = f"https://{safe_user}:{safe_pass}@{clean_url}"

        # Tell Kodi to immediately resolve and play this URL
        play_item = xbmcgui.ListItem(path=stream_url)
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