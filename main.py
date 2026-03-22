import sys
import xbmc
import xbmcgui
import xbmcplugin
import urllib.parse

# Kodi passes these variables to our script
addon_url = sys.argv[0]
addon_handle = int(sys.argv[1])
# This line grabs the secret "?action=search" from the URL
args = urllib.parse.parse_qs(sys.argv[2][1:])

def build_main_menu():
    list_item = xbmcgui.ListItem(label="🎬 Search Movies")
    list_item.setInfo('video', {'title': 'Search Movies', 'plot': 'Search Usenet!'})
    
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=addon_url + "?action=search", listitem=list_item, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def search_usenet():
    # 1. Pop up the built-in Kodi keyboard
    keyboard = xbmc.Keyboard('', 'Enter Movie Name:')
    keyboard.doModal()
    
    # 2. Check if the user typed something and hit 'Done'
    if keyboard.isConfirmed() and keyboard.getText():
        search_term = keyboard.getText()
        
        # 3. For now, just pop up a notification confirming we captured the text!
        xbmcgui.Dialog().notification('NzbDAV Streamer', f'You searched for: {search_term}', xbmcgui.NOTIFICATION_INFO, 3000)
        
        # (Next step: We will send this search_term to your Indexer API!)

def router():
    # The Traffic Cop: Check what action Kodi is asking for
    action = args.get('action', [None])[0]
    
    if action == 'search':
        search_usenet()
    else:
        build_main_menu()

if __name__ == '__main__':
    router()