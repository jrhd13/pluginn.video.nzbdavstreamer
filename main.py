import sys
import urllib.parse
import urllib.request
import json
import xbmc
import xbmcgui
import xbmcplugin

# 🚨 PUT YOUR NZBHYDRA2 DETAILS HERE 🚨
INDEXER_API_URL = "https://jrhd13-nzbhydra.elfhosted.party/:5076/api" 
API_KEY = "4OQA7GS2H7D8BK57JQ2MPABL3T"

# Kodi passes these variables to our script
addon_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])

def build_main_menu():
    list_item = xbmcgui.ListItem(label="🎬 Search Movies")
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=addon_url + "?action=search", listitem=list_item, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def search_usenet():
    keyboard = xbmc.Keyboard('', 'Enter Movie Name:')
    keyboard.doModal()
    
    if keyboard.isConfirmed() and keyboard.getText():
        search_term = keyboard.getText()
        fetch_and_display_results(search_term)

def fetch_and_display_results(search_term):
    # 1. Build the exact Newznab API URL
    query = urllib.parse.quote_plus(search_term)
    api_url = f"{INDEXER_API_URL}?t=search&q={query}&apikey={API_KEY}&o=json"
    
    try:
        # 2. Shoot the request to the indexer and grab the JSON data
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))
        
        # 3. Drill down into the Newznab JSON to find the actual releases
        # Newznab usually puts results inside 'channel' -> 'item'
        items = data.get('channel', {}).get('item', [])
        
        # If there's only 1 result, it might not be a list, so we force it to be one
        if not isinstance(items, list):
            items = [items]

        # 4. Loop through the releases and draw them on the screen!
        for item in items:
            title = item.get('title', 'Unknown Title')
            nzb_link = item.get('link', '')
            
            list_item = xbmcgui.ListItem(label=title)
            list_item.setInfo('video', {'title': title})
            
            # The next action is 'play'. We pack the NZB link secretly into the URL!
            play_url = f"{addon_url}?action=play&nzb={urllib.parse.quote_plus(nzb_link)}"
            
            # isFolder=False means clicking this will trigger a video player, not a new menu!
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=play_url, listitem=list_item, isFolder=False)
        
        xbmcplugin.endOfDirectory(addon_handle)

    except Exception as e:
        xbmcgui.Dialog().notification('Error', 'Failed to fetch from indexer', xbmcgui.NOTIFICATION_ERROR, 3000)

def play_nzb(nzb_link):
    # 🚨 PUT YOUR NZBDAV DETAILS HERE 🚨
    NZBDAV_API_URL = "https://jrhd13-nzbdav.elfhosted.party/api"
    NZBDAV_API_KEY = "330b44d5f7a34f0992f8d25c44286a55"
    
    # Optional: If your WebDAV requires a username/password to stream
    WEBDAV_USER = "username"
    WEBDAV_PASS = "password"
    WEBDAV_BASE_URL = f"https://{WEBDAV_USER}:{WEBDAV_PASS}@YOURNAME-nzbdav.elfhosted.party/usenet"

    xbmcgui.Dialog().notification('NzbDAV', 'Sending to NzbDAV...', xbmcgui.NOTIFICATION_INFO, 2000)

    try:
        # 1. Fire the NZB link into NzbDAV (mimicking the SABnzbd addurl command)
        safe_nzb_link = urllib.parse.quote_plus(nzb_link)
        inject_url = f"{NZBDAV_API_URL}?mode=addurl&name={safe_nzb_link}&apikey={NZBDAV_API_KEY}"
        
        req = urllib.request.Request(inject_url, headers={'User-Agent': 'Mozilla/5.0'})
        urllib.request.urlopen(req)
        
        # Give NzbDAV 2 seconds to instantly mount the pieces of the file
        xbmc.sleep(2000)
        
        # 2. Tell Kodi to open your WebDAV folder so you can click the movie!
        # (Because the exact video filename inside the NZB is unknown until it mounts, 
        # the safest way is to open the NzbDAV folder directly on screen)
        xbmcgui.Dialog().notification('Success!', 'Opening NzbDAV Stream...', xbmcgui.NOTIFICATION_INFO, 2000)
        xbmc.executebuiltin(f'ActivateWindow(Videos,{WEBDAV_BASE_URL},return)')

    except Exception as e:
        xbmcgui.Dialog().notification('Error', 'Failed to send to NzbDAV', xbmcgui.NOTIFICATION_ERROR, 3000)

def router():
    # The Traffic Cop
    action = args.get('action', [None])[0]
    
    if action == 'search':
        search_usenet()
    elif action == 'play':
        nzb_link = args.get('nzb', [''])[0]
        play_nzb(nzb_link)
    else:
        build_main_menu()

if __name__ == '__main__':
    router()