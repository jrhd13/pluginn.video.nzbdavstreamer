import sys
import urllib.parse
import urllib.request
import json
import base64
import xbmc
import xbmcgui
import xbmcplugin

# ==========================================
# 🚨 EASYNEWS CREDENTIALS (REPLACE THESE) 🚨
# ==========================================
USER = "fmhamqhuti"
PASS = "iyzu-ypvt-nnzo"

# Kodi Setup
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])

def build_menu():
    li = xbmcgui.ListItem(label="🎬 Search Easynews")
    url = f"{base_url}?action=search"
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def do_search():
    kb = xbmc.Keyboard('', 'Search Movie:')
    kb.doModal()
    if kb.isConfirmed() and kb.getText():
        term = kb.getText()
        run_api(term)

def run_api(search_term):
    query = urllib.parse.quote_plus(search_term)
    # The optimized Solr API endpoint
    api_url = f"https://members.easynews.com/2.0/search/solr-search/advanced?gps={query}&pno=1&fty[]=VIDEO"
    
    try:
        # Auth Header
        user_pass = f"{USER}:{PASS}"
        auth = base64.b64encode(user_pass.encode('utf-8')).decode('utf-8')
        
        req = urllib.request.Request(api_url)
        req.add_header("Authorization", f"Basic {auth}")
        req.add_header("User-Agent", "Mozilla/5.0")
        
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode('utf-8', errors='ignore'))
        items = data.get('data', [])

        if not items:
            xbmcgui.Dialog().notification('Easynews', 'No results.', xbmcgui.NOTIFICATION_INFO, 3000)
            return

        for i in items:
            h = i.get('hash', '')
            id_val = i.get('id', '')
            name = i.get('fn', 'Movie')
            ext = i.get('extension', '.mkv')
            
            if not h or not id_val: continue

            full_name = f"{name}{ext}"
            # Construct the exact URL Easynews expects for direct streaming
            stream_link = f"https://members.easynews.com/d/{h}/{id_val}/{urllib.parse.quote(full_name)}"
            
            li = xbmcgui.ListItem(label=name)
            li.setInfo('video', {'title': name})
            li.setProperty('IsPlayable', 'true')
            
            # The URL passed to our 'play' action
            u = f"{base_url}?action=play&video={urllib.parse.quote_plus(stream_link)}"
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=li, isFolder=False)
            
        xbmcplugin.endOfDirectory(addon_handle)

    except Exception as e:
        xbmcgui.Dialog().ok("API Error", str(e))

def play_file(url):
    try:
        # Create the final authenticated link for the player
        # We strip the https:// and rebuild it with user:pass@ format
        clean = url.replace('https://', '')
        final_url = f"https://{urllib.parse.quote_plus(USER)}:{urllib.parse.quote_plus(PASS)}@{clean}|User-Agent=Mozilla/5.0"
        
        item = xbmcgui.ListItem(path=final_url)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=item)
    except Exception as e:
        xbmcgui.Dialog().ok("Playback Error", str(e))

# Router
action = args.get('action', [None])[0]
if action == 'search':
    do_search()
elif action == 'play':
    play_file(args.get('video', [''])[0])
else:
    build_menu()