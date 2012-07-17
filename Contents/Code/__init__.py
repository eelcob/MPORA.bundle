MPORA_VIDEO_PREFIX = "/video/mpora"
MPORA_PHOTO_PREFIX = "/photos/mpora"

TITLE = "Mpora"
ART = "art-default.png"
ICON = "icon-default.png"

MPORA_URL = "http://mpora.com"
BRAND_URL = MPORA_URL + "/brands/"
VIDEO_MPORA_URL = "http://mpora.com/%s"
PAGED_VIDEO_MPORA_URL = "http://mpora.com/%s%s%d"
BRAND_MPORA_URL = "http://mpora.com/%s%s%d"
PHOTO_MPORA_URL = "http://photo.mpora.com/%s"

RE_IMAGE = Regex("^background: url\((?P<image_url>.*)\)")

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

    HTTP.CacheTime = 1800

####################################################################################################
def MainMenuVideo():
    
    oc = ObjectContainer()
    oc.add(DirectoryObject(key = Callback(Sports, title = "Sport Channels"), title = "Sport Channels"))
    oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "Featured Videos", page_path = "/videos"), title = "Featured Videos"))    
    oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "Recently Added", page_path = "/videos/recent"), title = "Recently Added"))
    oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "High Def Videos", page_path = "/videos/hd"), title = "High Def Videos"))
    oc.add(DirectoryObject(key = Callback(BrandChannels, title = "Brand Channels"), title = "Brand Channels"))    
    #oc.add(DirectoryObject(key = Callback(BrandChannels, title = "Brand Channels", page_path = "/videos"), title = "Brand Channels"))    
    oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "Brand Videos", page_path = "/videos/brands"), title = "Brand Videos")) 
    oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.mpora", title = "Search...", prompt = "Search for Videos", thumb = R('search.png')))
    return oc

#########################################################
def MainMenuPictures():

    oc = ObjectContainer()
    oc.add(DirectoryObject(key = Callback(Photos, title = "Featured Photos", page_path = "/all/featured"), title = "Featured Photos")) 
    oc.add(DirectoryObject(key = Callback(Photos, title = "Popular Photos", page_path = "/all/popular"), title = "Popular Photos")) 

    AddSportsChannels(oc, video = False)

    return oc

##########################################################
def Sports(title):

    oc = ObjectContainer(title2 = title)
    AddSportsChannels(oc)
    return oc

##########################################################
def AddSportsChannels(oc, video = True):

    oc.add(DirectoryObject(key = Callback(SportChannel, title = "MTB", page_path = "/mountainbiking", video = video), title = "MTB"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Snowboard", page_path = "/snowboarding", video = video), title = "Snowboard"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Surf", page_path = "/surfing", video = video), title = "Surf"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Skate", page_path = "/skateboarding", video = video), title = "Skate"))  
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "BMX", page_path = "/bmx", video = video), title = "BMX"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Moto", page_path = "/motocross", video = video), title = "Moto"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Ski", page_path = "/skiing", video = video), title = "Ski"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Wake", page_path = "/wakeboarding", video = video), title = "Wake"))
    oc.add(DirectoryObject(key = Callback(SportChannel, title = "Outdoor", page_path = "/outdoor", video = video), title = "Outdoor"))

############################################################
def SportChannel(title, page_path, video = True):

    oc = ObjectContainer(title2 = title)
    if(video):
        oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "Featured Video",  page_path = page_path + "/videos"), title = "Featured Video"))
        oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "Recently Added",  page_path = page_path + "/videos/recent"), title = "Recently Added"))
        oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "High Def Videos",  page_path = page_path + "/videos/hd"), title = "High Def Videos"))
        oc.add(DirectoryObject(key = Callback(BrandChannels, title = "Brand Channels"), title = "Brand Channels"))
        #oc.add(DirectoryObject(key = Callback(BrandChannels, title = "Brand Channels",  page_path = page_path), title = "Brand Channels"))
        oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = "Brand Videos",  page_path = page_path + "/videos/brands"), title = "Brand Videos"))
    else:
        oc.add(DirectoryObject(key = Callback(Photos, title = "Featured Photos",  page_path = page_path + "/featured"), title = "Featured Photos"))
        oc.add(DirectoryObject(key = Callback(Photos, title = "Popular Photos",  page_path = page_path + "/popular"), title = "Popular Photos"))

    return oc

#############################################################################
def PaginatedVideos(title, page_path, page = 1):

	oc = ObjectContainer(view_group = "InfoList", title2 = title)

	url = PAGED_VIDEO_MPORA_URL % (page_path, "?page=" , page)

	html_page = HTML.ElementFromURL(url, errors='ignore')
	
	for item in html_page.xpath('//a[contains(@class, "video-thumbnail")]'):
		clip_title = item.xpath('.//h6')[0].text
		thumb = item.xpath('.//div/img')[0].get('src')
		page_url = MPORA_URL + item.xpath('.')[0].get('href')

		oc.add(VideoClipObject(
			url = page_url,
			title = clip_title,
			thumb = thumb))

	pages = html_page.xpath("//a[@class='next_page']")
	if len(pages) > 0:
		oc.add(DirectoryObject(key = Callback(PaginatedVideos, title = title,  page_path = page_path, page = page + 1), title = "More..."))

	if len(oc) == 0:
		return MessageContainer(title, "There are no titles available for the requested item.")

	return oc

#########################################################
def BrandChannels(title, page = 1):

	oc = ObjectContainer(title2 = title)

	html_page = HTML.ElementFromURL(BRAND_URL, errors='ignore')

	for item in html_page.xpath("//ul[@class='brands']/li/a"):
		title = item.xpath(".//h3")[0].text
		thumb = item.xpath(".//img")[0].get('src')
		brand = item.xpath(".")[0].get('href')
		
		oc.add(DirectoryObject(key = Callback(BrandChannel, title = title, brand = brand), title = title, thumb=thumb))


	return oc

########################################################
def BrandChannel(title, brand, page = 1):
	
	oc = ObjectContainer(view_group = "InfoList", title2 = title)
	
	url = BRAND_MPORA_URL % (brand, "/videos?page=", page)
	html_page = HTML.ElementFromURL(url, errors='ignore', timeout=20)


	for item in html_page.xpath('//a[contains(@class, "video-thumbnail")]'):
		clip_title = item.xpath('.//h6')[0].text
		thumb = item.xpath('.//div/img')[0].get('src')
		page_url = MPORA_URL + item.xpath('.')[0].get('href')

		oc.add(VideoClipObject(
			url = page_url,
			title = clip_title,
			thumb = thumb))
			
	pages = html_page.xpath("//a[@class='next_page']")
	if len(pages) > 0:
		oc.add(DirectoryObject(key = Callback(BrandChannel, title = title,  brand = brand, page = page + 1), title = "More..."))

	if len(oc) == 0:
		return MessageContainer(title, "There are no titles available for the requested item.")	
			
	return oc

#########################################################
def Photos(title, page_path):

    oc = ObjectContainer(view_group = 'Pictures', title2 = title)
    url = PHOTO_MPORA_URL % page_path
    for item in HTML.ElementFromURL(url, errors='ignore').xpath('//div[@class="contentBox many"]//div[@class="photoItem"]/a'):
        if(len(item.xpath('img')) > 0):

            # It appears that some photos are uploaded without an actual title.
            title = item.xpath('img')[0].get('alt')
            if title == None:
                title = "Photo"

            thumb = item.xpath('img')[0].get('src')
            page_url = item.get('href')

            oc.add(PhotoObject(
                url = page_url,
                title = title,
                thumb = thumb))
    return oc
