import sys
import urllib.parse
import urllib.request
import json
import xbmc
import xbmcgui
import xbmcplugin

# ==========================================
# 🚨 1. YOUR NZBHYDRA2 DETAILS HERE 🚨
# ==========================================
INDEXER_API_URL = "https://jrhd13-nzbhydra.elfhosted.party/api" 
API_KEY = "4OQA7GS2H7D8BK57JQ2MPABL3T"

# Kodi passes these hidden variables to our script
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
    query = urllib.parse.quote_plus(search_term)
    api_url = f"{INDEXER_API_URL}?t=search&q={query}&apikey={API_KEY}&o=json"
    
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))
        
        items = data.get('channel', {}).get('item', [])
        if not isinstance(items, list):
            items = [items]

        for item in items:
            title = item.get('title', 'Unknown Title')
            nzb_link = item.get('link', '')
            
            list_item = xbmcgui.ListItem(label=title)
            list_item.setInfo('video', {'title': title})
            
            play_url = f"{addon_url}?action=play&nzb={urllib.parse.quote_plus(nzb_link)}"
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=play_url, listitem=list_item, isFolder=False)
        
        xbmcplugin.endOfDirectory(addon_handle)

    except Exception as e:
        xbmcgui.Dialog().notification('Search Error', str(e), xbmcgui.NOTIFICATION_ERROR, 5000)

def play_nzb(nzb_link):
    # ==========================================
    # 🚨 2. YOUR NZBDAV DETAILS HERE 🚨
    # ==========================================
    NZBDAV_API_URL = "https://jrhd13-nzbdav.elfhosted.party/api"
    NZBDAV_API_KEY = "330b44d5f7a34f0992f8d25c44286a55"
    
    # URL-Encode credentials so special characters don't break the link!
    WEBDAV_USER = urllib.parse.quote_plus("elfhosted")
    WEBDAV_PASS = urllib.parse.quote_plus("elfhosted")
    
    # Pointing straight to the root to avoid Emby symlink folders!
    WEBDAV_HOST = "jrhd13-nzbdav.elfhosted.party/" 
    
    # Build the secret davs:// link
    WEBDAV_BASE_URL = f"davs://{WEBDAV_USER}:{WEBDAV_PASS}@{WEBDAV_HOST}"

    xbmcgui.Dialog().notification('NzbDAV', 'Sending to NzbDAV...', xbmcgui.NOTIFICATION_INFO, 2000)

    try:
        # 1. Fire the link to NzbDAV
        safe_nzb_link = urllib.parse.quote_plus(nzb_link)
        inject_url = f"{NZBDAV_API_URL}?mode=addurl&name={safe_nzb_link}&apikey={NZBDAV_API_KEY}"
        
        req = urllib.request.Request(inject_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        
        # 2. Read NzbDAV's actual reply and pop it up on screen!
        nzbdav_reply = response.read().decode('utf-8')
        xbmcgui.Dialog().notification('NzbDAV Reply:', nzbdav_reply[:40], xbmcgui.NOTIFICATION_INFO, 3000)
        
        # 3. Give NzbDAV 4 seconds to mount the raw file
        xbmc.sleep(4000)
        
        # 4. Open the root WebDAV folder wrapped in quotes!
        xbmcgui.Dialog().notification('Success!', 'Opening NzbDAV Stream...', xbmcgui.NOTIFICATION_INFO, 2000)
        xbmc.executebuiltin(f'ActivateWindow(Videos,"{WEBDAV_BASE_URL}",return)')

    except Exception as e:
        xbmcgui.Dialog().notification('Playback Error', str(e), xbmcgui.NOTIFICATION_ERROR, 5000)

def router():
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