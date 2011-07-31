import re, string, datetime

MPORA_VIDEO_PREFIX      = "/video/mpora"
MPORA_PHOTO_PREFIX      = "/photos/mpora"

MPORA_URL 		  = "http://mpora.com/"
VIDEO_MPORA_URL   = "http://video.mpora.com/%s"
PAGED_VIDEO_MPORA_URL   = "http://video.mpora.com/%s/%d"

VIDEO_DETAILS = "http://api.mpora.com/tv/player/load/vid/%s"

PHOTO_MPORA_URL   = "http://photo.mpora.com/%s"
ORIGINAL_PHOTO_URL = "http://cdn1.static.mporatrons.com/photo/%s_o.jpg"
SMALL_PHOTO_URL = "http://cdn1.static.mporatrons.com/photo/%s_t.jpg"
CACHE_INTERVAL    = 1800
USE_HD_PREF_KEY = "hd"

ICON = "icon-default.png"

####################################################################################################
def Start():
    Plugin.AddPrefixHandler(MPORA_VIDEO_PREFIX, MainMenuVideo, "Mpora", ICON, "art-default.png")
    Plugin.AddPrefixHandler(MPORA_PHOTO_PREFIX, MainMenuPictures, "Mpora", ICON, "art-default.png")
    Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("Photos", viewMode="Pictures", mediaType="photos")
    MediaContainer.art = R('art-default.png')
    MediaContainer.title1 = 'Mpora'
    HTTP.SetCacheTime(CACHE_INTERVAL)

####################################################################################################
def MainMenuVideo():
    dir = MediaContainer(mediaType='video')
    dir.Append(Function(DirectoryItem(Sports, title="Sport Channels", thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(HotVideos, title="Popular Videos", thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(PaginatedVideos, title="Featured Videos", thumb=R(ICON)), pagePath="all/featured"))
    dir.Append(Function(DirectoryItem(PaginatedVideos, title="Recently Added", thumb=R(ICON)), pagePath="all/recent"))
    dir.Append(Function(DirectoryItem(PaginatedVideos, title="High Def Videos", thumb=R(ICON)), pagePath="all/hd"))
    dir.Append(Function(DirectoryItem(BrandChannels, title="Brand Channels", thumb=R(ICON)), pagePath="all"))
    dir.Append(Function(DirectoryItem(PaginatedVideos, title="Brand Videos", thumb=R(ICON)), pagePath="all/brands"))
    dir.Append(Function(InputDirectoryItem(Search, title=L("Search..."), prompt=L("Search for Videos"), thumb=R('search.png'))))
    dir.Append(PrefsItem(L("Preferences..."), thumb=R('icon-prefs.png')))
    return dir

#########################################################
def MainMenuPictures():
    dir = MediaContainer(mediaType='pictures')
    dir.Append(Function(DirectoryItem(Photos, title="Featured Photos"), pagePath='all/featured'))
    dir.Append(Function(DirectoryItem(Photos, title="Popular Photos"), pagePath='all/popular'))
    AddSportsChannels(dir, video=False)
    return dir

#######################################################################  
def Search(sender, query):
    pagePath = 'search/'+query+'/relevance'
    return PaginatedVideos(sender, pagePath, increment=21)

###################################################
def HotVideos(sender, url=MPORA_URL):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    
    for item in HTML.ElementFromURL(url, errors='ignore').xpath('//div[@id="top10ContentContainer"]/ul/li'):
        pageUrl = item.xpath(".//a[@class='top10title']")[0].get('href')
        
        # Ensure that we filter out any results which are not from MPORA.
        if(pageUrl.find("http://video.mpora.com") != -1):
            
            # Extract the details from the page.
            title = item.xpath('.//span[@class="top10text"]//text()')[0].strip()
            summary = item.xpath('.//span[@class="top10vote_number"]')[0].get('title').strip()
            thumb = item.xpath('.//img')[0].get('src')
            dir.Append(Function(VideoItem(PlayVideo, title=title, summary=summary, thumb=thumb), pageUrl=pageUrl))
    
    return dir

##########################################################
def Sports(sender):
    dir = MediaContainer(title2=sender.itemTitle)
    AddSportsChannels(dir)
    return dir

##########################################################
def AddSportsChannels(dir, video=True):
    dir.Append(Function(DirectoryItem(SportChannel, title="MTB", thumb=R(ICON)), pagePath='mountainbiking', video=video))
    dir.Append(Function(DirectoryItem(SportChannel, title="Snowboard", thumb=R(ICON)), pagePath='snowboarding', video=video))
    dir.Append(Function(DirectoryItem(SportChannel, title="Surf", thumb=R(ICON)), pagePath='surfing', video=video))
    dir.Append(Function(DirectoryItem(SportChannel, title="Skate", thumb=R(ICON)), pagePath='skateboarding', video=video))
    dir.Append(Function(DirectoryItem(SportChannel, title="BMX", thumb=R(ICON)), pagePath='bmx', video=video))
    dir.Append(Function(DirectoryItem(SportChannel, title="Moto", thumb=R(ICON)), pagePath='motocross', video=video))
    dir.Append(Function(DirectoryItem(SportChannel, title="Ski", thumb=R(ICON)), pagePath='skiing', video=video))
    dir.Append(Function(DirectoryItem(SportChannel, title="Wake", thumb=R(ICON)), pagePath='wakeboarding', video=video))
    dir.Append(Function(DirectoryItem(SportChannel, title="Outdoor", thumb=R(ICON)), pagePath='outdoor', video=video))

############################################################
def SportChannel(sender, pagePath, video=True):
    dir = MediaContainer(title2=sender.itemTitle)
    if(video):
        dir.Append(Function(DirectoryItem(HotVideos, title="Popular Videos", thumb=R(ICON)), url=MPORA_URL+pagePath))
        dir.Append(Function(DirectoryItem(PaginatedVideos, title="Featured Videos", thumb=R(ICON)), pagePath=pagePath+"/featured"))
        dir.Append(Function(DirectoryItem(PaginatedVideos, title="Recently Added", thumb=R(ICON)), pagePath=pagePath+"/recent"))
        dir.Append(Function(DirectoryItem(PaginatedVideos, title="High Def Videos", thumb=R(ICON)), pagePath=pagePath+"/hd"))
        dir.Append(Function(DirectoryItem(BrandChannels, title="Brand Channels", thumb=R(ICON)), pagePath=pagePath))
        dir.Append(Function(DirectoryItem(PaginatedVideos, title="Brand Videos", thumb=R(ICON)), pagePath=pagePath+"/brands"))
    else:
        dir.Append(Function(DirectoryItem(Photos, title="Featured Photos"), pagePath=pagePath+"/featured"))
        dir.Append(Function(DirectoryItem(Photos, title="Popular Photos"), pagePath=pagePath+"/popular"))
    return dir

#############################################################################
def PaginatedVideos(sender, pagePath, page=0, increment=20):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    
    # Construct a suitable url, which includes the explit page number.
    if(page == 0):
        url = VIDEO_MPORA_URL % pagePath 
    else:
        url = PAGED_VIDEO_MPORA_URL % (pagePath, page)
    
    html_page = HTML.ElementFromURL(url, errors='ignore')
    for item in html_page.xpath('//ul[contains(@class, "videoItem")]'):
        
        # Extract the details from the page.
        title = item.xpath('.//span[@class="videoTitle"]//text()')[0].strip()
        summary = item.xpath('.//p//text()')[0].strip()
        thumb = item.xpath('.//img')[0].get('src')
        pageUrl = item.xpath('.//a')[0].get('href')
        dir.Append(Function(VideoItem(PlayVideo, title=title, summary=summary, thumb=thumb), pageUrl=pageUrl))
    
    # Attempt to determine the last possible page link provided by the page. We'll look at the last link and see if it has a class
    # of 'pagination_link_current'. If this is the case, we have come to the end of all possible results, and will therefore not
    # display a "More..." option.
    pages = html_page.xpath('//ul[@class="pagination"]/span/a[contains(@class,"pagination_link")]')
    if len(pages) > 0:
        last_page_link = pages[len(pages) - 1]
    
        if last_page_link.get('class') != "pagination_link_current":
            dir.Append(Function(DirectoryItem(PaginatedVideos, title="More...", thumb=R(ICON)), pagePath=pagePath, page=page+increment))

    if len(dir) == 0:
        return MessageContainer(sender.itemTitle, "There are no titles available for the requested item.")
                
    return dir

#########################################################
def BrandChannels(sender, pagePath):
    dir = MediaContainer(title2=sender.itemTitle)
    
    url = "http://mpora.com/%s/brands" % pagePath
    html_page = HTML.ElementFromURL(url, errors='ignore')
    for item in html_page.xpath('//div[contains(@class,"brandsContainer")]/div/ul/li'):
        
        if(item.xpath("a/img")):
            
            # Extract the details from the brand channel
            title = item.xpath("a/span")[0].text
            thumb = item.xpath("a/img")[0].get('src') + "#index.jpg"
            brand = item.xpath("a")[0].get('href')
            
            if title and len(title) > 0:
                dir.Append(Function(DirectoryItem(BrandChannel, title=title, thumb=thumb), brand=brand))
    
    return dir

########################################################
def BrandChannel(sender, brand, page=0):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    
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
            pageUrl = item.xpath('.//a')[0].get('href')
            
            thumb_style = item.xpath(".//li[@class='thumbs media']")[0].get('style')
            thumb = re.match("^background: url\((?P<image_url>.*)\)", thumb_style).groupdict()['image_url']
            
            dir.Append(Function(VideoItem(PlayVideo, title=title, summary=summary, thumb=thumb), pageUrl=pageUrl))
    
    # Attempt to determine the last possible page link provided by the page. We'll look at the last link and see if it has a class
    # of 'pagination_link_current'. If this is the case, we have come to the end of all possible results, and will therefore not
    # display a "More..." option.
    pages = html_page.xpath('//ul[@class="pagination"]/span/a[contains(@class,"pagination_link")]')
    last_page_link = pages[len(pages) - 1]
    
    if last_page_link.get('class') != "pagination_link_current":
        dir.Append(Function(DirectoryItem(BrandChannel, title="More...", thumb=R(ICON)), brand=brand, page=page+10))
    
    return dir

#####################################
def PlayVideo(sender, pageUrl):
    end = len(pageUrl)
    
    # If the user has set the preference to 'HD', then we must attempt to load this video type..
    alreadyHd = pageUrl[end-4:end] == '/hd/'
    if alreadyHd == False:
        if (Prefs[USE_HD_PREF_KEY]):
            pageUrl + 'hd/'
    
    hd = False
    
    if(pageUrl[end-4:end] == '/hd/'):
        hd = True
        end = end - 4
    elif(pageUrl[end-1:end] == '/'):
        end = end - 1
    start = 1 + pageUrl.rfind("/", 0, end-1)
    
    key = pageUrl[start:end]
    rssPageUrl = VIDEO_DETAILS%key
    if(hd):
        rssPageUrl = rssPageUrl + "/hd/true"
    rssUrl = HTML.ElementFromURL(rssPageUrl, errors='ignore').xpath('//response/configuration/video')[0].get('url')
    videoUrl = HTML.ElementFromURL(rssUrl, errors='ignore').xpath('//rss/channel/item/enclosure')[0].get('url')
    return Redirect(videoUrl)

#########################################################
def Photos(sender, pagePath):
    dir = MediaContainer(viewGroup='Photos', title2=sender.itemTitle)
    url = PHOTO_MPORA_URL % pagePath
    for item in HTML.ElementFromURL(url, errors='ignore').xpath('//div[@class="contentBox many"]//div[@class="photoItem"]/a'):
        if(len(item.xpath('img')) > 0):
            title = item.xpath('img')[0].get('alt')
            photoPageUrl = item.get('href')
            Log("Photo page URL:"+photoPageUrl)
            id = photoPageUrl.replace("http://photo.mpora.com/photo/","").replace("/","")
            #id = photoPageUrl[index+1:len(photoPageUrl)]
            Log("Photo ID:"+id)
            photoUrl = ORIGINAL_PHOTO_URL % id
            thumb = SMALL_PHOTO_URL % id
            dir.Append(PhotoItem(photoUrl, title=title, Summary=None, thumb=thumb))
    return dir
