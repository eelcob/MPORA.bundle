import re

MPORA_VIDEO_PREFIX = "/video/mpora"
MPORA_PHOTO_PREFIX = "/photos/mpora"

TITLE = "Mpora"
ART = "art-default.png"
ICON = "icon-default.png"

MPORA_URL = "http://mpora.com/"
VIDEO_MPORA_URL = "http://video.mpora.com/%s"
PAGED_VIDEO_MPORA_URL = "http://video.mpora.com/%s/%d"
PHOTO_MPORA_URL = "http://photo.mpora.com/%s"

####################################################################################################
def Start():
    Plugin.AddPrefixHandler(MPORA_VIDEO_PREFIX, MainMenuVideo, TITLE, ICON, ART)
    Plugin.AddPrefixHandler(MPORA_PHOTO_PREFIX, MainMenuPictures, "Mpora", ICON, ART)
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("Pictures", viewMode="Pictures", mediaType="photos")

    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = TITLE
    ObjectContainer.view_group = "List"

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)
    PhotoObject.thumb = R(ICON)
    PhotoObject.art = R(ART)

    HTTP.CacheTime = 1800

####################################################################################################
def MainMenuVideo():
    
    oc = ObjectContainer()
    oc.add(DirectoryObject(key = Callback(Sports, title = "Sport Channels"), title = "Sport Channels"))
    oc.add(DirectoryObject(key = Callback(HotVideos, title = "Popular Videos"), title = "Popular Videos"))
    oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "Featured Videos", page_path = "all/featured"), title = "Featured Videos"))    
    oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "Recently Added", page_path = "all/recent"), title = "Recently Added"))
    oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "High Def Videos", page_path = "all/hd"), title = "High Def Videos"))
    oc.add(DirectoryObject(key = Callback(BrandChannels, title = "Brand Channels", page_path = "all"), title = "Brand Channels"))    
    oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "Brand Videos", page_path = "all/brands"), title = "Brand Videos")) 
    oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.mpora", title = "Search...", prompt = "Search for Videos", thumb = R('search.png')))
    return oc

#########################################################
def MainMenuPictures():

    oc = ObjectContainer()
    oc.add(DirectoryObject(key = Callback(Photos, title = "Featured Photos", page_path = "all/featured"), title = "Featured Photos")) 
    oc.add(DirectoryObject(key = Callback(Photos, title = "Popular Photos", page_path = "all/popular"), title = "Popular Photos")) 

    AddSportsChannels(oc, video = False)

    return oc

###################################################
def HotVideos(title, url = MPORA_URL):

    oc = ObjectContainer(view_group = "InfoList", title2 = title)

    for item in HTML.ElementFromURL(url, errors='ignore').xpath('//div[@id="top10ContentContainer"]/ul/li'):
        page_url = item.xpath(".//a[@class='top10title']")[0].get('href')

        # Ensure that we filter out any results which are not from MPORA.
        if(page_url.find("http://video.mpora.com") != -1):

            # Extract the details from the page.
            title = item.xpath('.//span[@class="top10text"]//text()')[0].strip()
            summary = item.xpath('.//span[@class="top10vote_number"]')[0].get('title').strip()
            thumb = item.xpath('.//img')[0].get('src')

            oc.add(VideoClipObject(
                url = page_url,
                title = title,
                summary = summary,
                thumb = thumb))

    return oc

##########################################################
def Sports(title):

    oc = ObjectContainer(title2 = title)
    AddSportsChannels(oc)
    return oc

##########################################################
def AddSportsChannels(oc, video = True):

    oc.add(DirectoryObject(key = Callback(SportChannel, title = "MTB", page_path = "mountainbiking", video = video), title = "MTB"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Snowboard", page_path = "snowboarding", video = video), title = "Snowboard"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Surf", page_path = "surfing", video = video), title = "Surf"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Skate", page_path = "skateboarding", video = video), title = "Skate"))  
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "BMX", page_path = "bmx", video = video), title = "BMX"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Moto", page_path = "motocross", video = video), title = "Moto"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Ski", page_path = "skiing", video = video), title = "Ski"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Wake", page_path = "wakeboarding", video = video), title = "Wake"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Outdoor", page_path = "outdoor", video = video), title = "Outdoor"))

############################################################
def SportChannel(title, page_path, video = True):

    oc = ObjectContainer(title2 = title)
    if(video):
        oc.add(DirectoryObject(key = Callback(HotVideos, title = "Popular Videos",  url = MPORA_URL + page_path), title = "Popular Videos"))
        oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "Featured Video",  page_path = page_path + "/featured"), title = "Featured Video"))
        oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "Recently Added",  page_path = page_path + "/recent"), title = "Recently Added"))
        oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "High Def Videos",  page_path = page_path + "/hd"), title = "High Def Videos"))
        oc.add(DirectoryObject(key = Callback(BrandChannels, title = "Brand Channels",  page_path = page_path), title = "Brand Channels"))
        oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "Brand Videos",  page_path = page_path + "/brands"), title = "Brand Videos"))
    else:
        oc.add(DirectoryObject(key = Callback(Photos, title = "Featured Photos",  page_path = page_path + "/featured"), title = "Featured Photos"))
        oc.add(DirectoryObject(key = Callback(Photos, title = "Popular Photos",  page_path = page_path + "/popular"), title = "Popular Photos"))

    return oc

#############################################################################
def PaginatedVideos(title, page_path, page = 0, increment = 20):

    oc = ObjectContainer(view_group = "InfoList", title2 = title)

    # Construct a suitable url, which includes the explit page number.
    if(page == 0):
        url = VIDEO_MPORA_URL % page_path 
    else:
        url = PAGED_VIDEO_MPORA_URL % (page_path, page)

    html_page = HTML.ElementFromURL(url, errors='ignore')
    for item in html_page.xpath('//ul[contains(@class, "videoItem")]'):

        # Extract the details from the page.
        title = item.xpath('.//span[@class="videoTitle"]//text()')[0].strip()
        summary = item.xpath('.//p//text()')[0].strip()
        thumb = item.xpath('.//img')[0].get('src')
        page_url = item.xpath('.//a')[0].get('href')

        oc.add(VideoClipObject(
            url = page_url,
            title = title,
            summary = summary,
            thumb = thumb))

    # Attempt to determine the last possible page link provided by the page. We'll look at the last link and see if it has a class
    # of 'pagination_link_current'. If this is the case, we have come to the end of all possible results, and will therefore not
    # display a "More..." option.
    pages = html_page.xpath('//ul[@class="pagination"]/span/a[contains(@class,"pagination_link")]')
    if len(pages) > 0:
        last_page_link = pages[len(pages) - 1]

        if last_page_link.get('class') != "pagination_link_current":
            oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = title,  page_path = page_path, page = page + increment), title = "More..."))

    if len(oc) == 0:
        return MessageContainer(title, "There are no titles available for the requested item.")

    return oc

#########################################################
def BrandChannels(title, page_path):

    oc = ObjectContainer(title2 = title)

    url = "http://mpora.com/%s/brands" % page_path
    html_page = HTML.ElementFromURL(url, errors='ignore')
    for item in html_page.xpath('//div[contains(@class,"brandsContainer")]/div/ul/li'):

        if(item.xpath("a/img")):

            # Extract the details from the brand channel
            title = item.xpath("a/span")[0].text
            thumb = item.xpath("a/img")[0].get('src') + "#index.jpg"
            brand = item.xpath("a")[0].get('href')

            if title and len(title) > 0:
                oc.add(DirectoryObject(key = Callback(BrandChannel, title = title, brand = brand), title = title))

    return oc

########################################################
def BrandChannel(title, brand, page = 0):

    oc = ObjectContainer(view_group = "InfoList", title2 = title)

    if(page == 0):
        url = "http://mpora.com%svideos/" % brand
    else:
        url = "http://mpora.com%svideos/%d" % (brand, page)

    html_page = HTML.ElementFromURL(url, errors='ignore', timeout=20)
    for item in html_page.xpath('//div[@class="contentBox sectionTop tagsTop"]//ul'):

        # Ensure that we filter out any non-video items..
        video_item = item.xpath(".//a[@type='video']")
        if len(video_item) == 1:

            # Extract the details from the page.
            title = item.xpath('.//h3//text()')[0].strip()
            summary = item.xpath('.//p[@class="videoDescription"]//text()')[0].strip()
            page_url = item.xpath('.//a')[0].get('href')

            thumb_style = item.xpath(".//li[@class='thumbs media']")[0].get('style')
            thumb = re.match("^background: url\((?P<image_url>.*)\)", thumb_style).groupdict()['image_url']

            oc.add(VideoClipObject(
                url = page_url,
                title = title,
                summary = summary,
                thumb = thumb))

    # Attempt to determine the last possible page link provided by the page. We'll look at the last link and see if it has a class
    # of 'pagination_link_current'. If this is the case, we have come to the end of all possible results, and will therefore not
    # display a "More..." option.
    pages = html_page.xpath('//ul[@class="pagination"]/span/a[contains(@class,"pagination_link")]')
    last_page_link = pages[len(pages) - 1]

    if last_page_link.get('class') != "pagination_link_current":
        oc.add(DirectoryObject(key = Callback(BrandChannel, title = title, brand = brand, page = page + 10), title = "More..."))

    return oc

#########################################################
def Photos(title, page_path):

    oc = ObjectContainer(view_group = 'Pictures', title2 = title)
    url = PHOTO_MPORA_URL % page_path
    for item in HTML.ElementFromURL(url, errors='ignore').xpath('//div[@class="contentBox many"]//div[@class="photoItem"]/a'):
        if(len(item.xpath('img')) > 0):
            title = item.xpath('img')[0].get('alt')
            thumb = item.xpath('img')[0].get('src')
            page_url = item.get('href')

            oc.add(PhotoObject(
                url = page_url,
                title = title,
                thumb = thumb))
    return oc
