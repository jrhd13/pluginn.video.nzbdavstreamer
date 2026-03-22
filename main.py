import sys
import urllib.parse
import urllib.request
import re
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
    # Removed the strict video=1 filter so it returns everything!
    api_url = f"https://members.easynews.com/global5/search.html?gps={query}"
    
    try:
        auth_string = f"{EASYNEWS_USER}:{EASYNEWS_PASS}"
        base64_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        
        req = urllib.request.Request(api_url)
        req.add_header("Authorization", f"Basic {base64_auth}")
        req.add_header("User-Agent", "Mozilla/5.0")
        
        response = urllib.request.urlopen(req)
        html_data = response.read().decode('utf-8', errors='ignore')
        
        # 🚨 THE ULTIMATE SCRAPER: Ignore HTML entirely.
        # Find ANY string in the entire source code that looks like a video link.
        absolute_links = re.findall(r'["\'](https?://[^"\']*\.(?:mkv|mp4|avi)[^"\']*)["\']', html_data, re.IGNORECASE)
        relative_links = re.findall(r'["\'](/[^"\']*\.(?:mkv|mp4|avi)[^"\']*)["\']', html_data, re.IGNORECASE)
        
        unique_links = []
        for link in absolute_links:
            if link not in unique_links:
                unique_links.append(link)
                
        for link in relative_links:
            full_link = f"https://members.easynews.com{link}"
            if full_link not in unique_links:
                unique_links.append(full_link)

        # Wiretap: Tell us how many we ripped from the code
        xbmcgui.Dialog().notification('Easynews Scraper', f'Found {len(unique_links)} videos!', xbmcgui.NOTIFICATION_INFO, 3000)

        if len(unique_links) == 0:
            # If it STILL finds 0, pop up an error so we know it's completely empty
            xbmcgui.Dialog().notification('Error', 'No videos found in source code!', xbmcgui.NOTIFICATION_ERROR, 4000)
            return

        for video_link in unique_links:
            # Clean up the messy URL to make a pretty title for Kodi
            raw_filename = video_link.split('/')[-1]
            clean_title = urllib.parse.unquote(raw_filename.split('?')[0])
                
            list_item = xbmcgui.ListItem(label=clean_title)
            list_item.setInfo('video', {'title': clean_title})
            list_item.setProperty('IsPlayable', 'true')
            
            play_url = f"{addon_url}?action=play&video={urllib.parse.quote_plus(video_link)}"
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=play_url, listitem=list_item, isFolder=False)
        
        xbmcplugin.endOfDirectory(addon_handle)

    except Exception as e:
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