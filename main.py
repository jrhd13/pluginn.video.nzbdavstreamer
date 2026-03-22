import sys
import xbmcgui
import xbmcplugin

# Kodi automatically passes these hidden variables to our script when it opens
addon_url = sys.argv[0]
addon_handle = int(sys.argv[1])

def build_main_menu():
    # 1. Create a clickable list item
    list_item = xbmcgui.ListItem(label="🎬 Search Movies (Test)")
    list_item.setInfo('video', {'title': 'Search Movies', 'plot': 'This will soon search Usenet!'})
    
    # 2. Add the item to the Kodi screen
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=addon_url + "?action=search", listitem=list_item, isFolder=True)
    
    # 3. Tell Kodi we are finished drawing the menu
    xbmcplugin.endOfDirectory(addon_handle)

if __name__ == '__main__':
    build_main_menu()