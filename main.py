# -*- coding: utf-8 -*-
# Module: default
# Author: fsegouin
# Based on https://github.com/romanvm/plugin.video.example

import os
import sys
import re
import urllib
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import xbmcaddon

__addon__       = xbmcaddon.Addon('plugin.video.btsport')
__cwd__ = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
BASE_RESOURCE_PATH = os.path.join(__cwd__, 'resources', 'lib')
sys.path.append(BASE_RESOURCE_PATH)

import requests, json

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])


def get_categories():
    """
    Get the list of video categories.

    :return: list
    """
    return ['All videos', 'Football', 'UFC', 'Moto GP', 'Rugby Union', 'BT Sport Shows', 'Tennis', 'Boxing', 'Cricket', 'More Sport', 'Action Woman', 'The Supporters Club']

def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Get video categories
    categories = get_categories()
    # Create a list for our items.
    listing = []
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        # Set additional info for the list item.
        list_item.setInfo('video', {'title': category, 'genre': category})
        # Create a URL for the plugin recursive callback.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = '{0}?action=listing&category={1}'.format(_url, category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))
    # Add our listing to Kodi.
    # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
    # instead of adding one by ove via addDirectoryItem.
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def get_videos(category):
    """
    Get the list of videofiles/streams.

    :param category: str
    :return: list
    """
    all_videos = []
    url = ''
    if category != 'All videos':
        category =  urllib.quote(category)
        url = 'http://api-search.bt.com/search/sport/select?q=AssetType:BTVideo&fq=tags:(%22' + category + '%22)%26Publist:btsport&start=0&rows=50&sort=publicationdate+desc&json.wrf=loadres&wt=json&callback=loadres'
    else:
        url = 'http://api-search.bt.com/search/sport/select?q=AssetType:BTVideo&fq=Publist:btsport&start=0&rows=50&sort=publicationdate+desc&json.wrf=loadres&wt=json&callback=loadres'
    r = requests.get(url)
    p = re.compile(ur'loadres\((.*)\)')
    m = re.match(p, r.text)
    json_response = json.loads(m.group(1))
    videos = json_response['response']['docs']
    i = 0
    for video in videos:
        i += 1
        v = {}
        print video
        v['name'] = str(i) + ' - ' + video['h1title']
        if 'imageurl' in video:
            v['thumb'] = video['imageurl']
        else:
            v['thumb'] = ''
        if 'hlsurl' in video:
            v['video'] = video['hlsurl']
        elif 'streamingurl' in video:
            v['video'] = video['streamingurl']
        if 'video' in v:
            all_videos.append(v)
    return all_videos


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: str
    """
    # Get the list of videos in the category.
    videos = get_videos(category)
    # Create a list for our items.
    listing = []
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        # list_item.setInfo('video', {'title': video['name'], 'genre': video['genre']})
        list_item.setInfo('video', {'title': video['name'], 'genre': ''})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for the plugin recursive callback.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
        url = '{0}?action=play&video={1}'.format(_url, video['video'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))
    # Add our listing to Kodi.
    # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
    # instead of adding one by ove via addDirectoryItem.
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring:
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
