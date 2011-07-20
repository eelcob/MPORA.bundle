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
  #Log("URL:"+url)
  for item in HTML.ElementFromURL(url, errors='ignore').xpath('//div[@id="top10ContentContainer"]/ul/li'):
    pageUrl = item.xpath(".//a[@class='top10title']")[0].get('href')
    #Log("PageURL:"+pageUrl)
    if(pageUrl.find("http://video.mpora.com") != -1):
        VideoItemExtraction(dir, pageUrl)
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
    #dir.Append(Function(DirectoryItem(PaginatedMovies, title="Movies"), pagePath=pagePath+"/movies"))
    dir.Append(Function(DirectoryItem(BrandChannels, title="Brand Channels", thumb=R(ICON)), pagePath=pagePath))
    dir.Append(Function(DirectoryItem(PaginatedVideos, title="Brand Videos", thumb=R(ICON)), pagePath=pagePath+"/brands"))
  else:
    dir.Append(Function(DirectoryItem(Photos, title="Featured Photos"), pagePath=pagePath+"/featured"))
    dir.Append(Function(DirectoryItem(Photos, title="Popular Photos"), pagePath=pagePath+"/popular"))
  return dir
  
#############################################################################
def PaginatedVideos(sender, pagePath, page=0, increment=20):
  dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
  
  if(page == 0):
    url = VIDEO_MPORA_URL % pagePath 
  else:
    url = PAGED_VIDEO_MPORA_URL % (pagePath, page)
  for item in HTML.ElementFromURL(url, errors='ignore').xpath('//ul[contains(@class, "videoItem")]/li/a'):
    if(item.xpath('img')):
      videoUrl = item.get('href')
      VideoItemExtraction(dir, videoUrl)

  # Attempt to determine the last possible page link provided by the page. We'll look at the last link and see if it has a class
  # of 'pagination_link_current'. If this is the case, we have come to the end of all possible results, and will therefore not
  # display a "More..." option.
  pages = HTML.ElementFromURL(url, errors='ignore').xpath('//ul[@class="pagination"]/span/a[contains(@class,"pagination_link")]')
  last_page_link = pages[len(pages) - 1]

  if last_page_link.get('class') != "pagination_link_current":
    dir.Append(Function(DirectoryItem(PaginatedVideos, title="More...", thumb=R(ICON)), pagePath=pagePath, page=page+increment))

  return dir


#############################################################################
# TODO: add extraction of movie details, which appears different than video (URL starts with tv)
#       The movie links don't work on the site (18/6) and don't work directly, so leave alone for
#       now
#
def PaginatedMovies(sender, pagePath, page=0):
  dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
  if(page == 0):
    url = VIDEO_MPORA_URL % pagePath
  else:
    url = PAGED_VIDEO_MPORA_URL % (pagePath, page)
  for item in HTML.ElementFromURL(url, errors='ignore').xpath('//div[@class="contentBox triple large"]/div/ul/li/a'):
    if(item.xpath('img')):
      videoUrl = item.get('href')
      dir.Append(MovieItem(videoUrl))
      
  dir.Append(Function(DirectoryItem(PaginatedMovies, title="More..."), pagePath=pagePath, page=page+20))
  return dir

#########################################################
def BrandChannels(sender, pagePath):
  dir = MediaContainer(title2=sender.itemTitle)
  url = "http://mpora.com/%s/brands" % pagePath
  for item in HTML.ElementFromURL(url, errors='ignore').xpath('//div[contains(@class,"brandsContainer")]/div/ul/li'):
    if(item.xpath("a/img")):
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
  
  for item in HTML.ElementFromURL(url, errors='ignore').xpath('//div[@class="contentBox sectionTop tagsTop"]/div/ul/li/a'):
    if(item.get('type') == 'video'):
      videoUrl = item.get('href')
      VideoItemExtraction(dir, videoUrl)
  for item in HTML.ElementFromURL(url, errors='ignore').xpath('//ul[@class="pagination"]/li/a'):
    if(item.text.startswith('Next')):
      dir.Append(Function(DirectoryItem(BrandChannel, title="More...", thumb=R(ICON)), brand=brand, page=page+10))
      break
  return dir
  
  
####################################################
# Extract the actual meta-data from destination page. 
#
def VideoItemExtraction(dir, pageUrl):
  subtitle = None
  
  end = len(pageUrl)
  alreadyHd = pageUrl[end-4:end] == '/hd/'
  if(alreadyHd):
    subtitle = "High Def\n" 
  else:
    # If video is available in HD and user hasn't switched it off, then use it. 
    #hdAvailable = len(HTML.ElementFromURL(pageUrl, errors='ignore').xpath('//h3[@class="definitionLink hd"]')) > 0
    #Log("HD Available:"+str(hdAvailable)+" from "+pageUrl)
    #if(hdAvailable):
    if(Prefs[USE_HD_PREF_KEY]):
        #subtitle = "High Def\n"   
        pageUrl = pageUrl +"hd/"
  
  title = HTML.ElementFromURL(pageUrl, errors='ignore').xpath('//meta[@name="title"]')[0].get('content').strip()
  summary = HTML.ElementFromURL(pageUrl, errors='ignore').xpath('//meta[@name="description"]')[0].get('content').strip()
  thumb = HTML.ElementFromURL(pageUrl, errors='ignore').xpath('//link[@rel="image_src"]')[0].get('href').strip() + "#index.jpg"
  duration = ExtractDuration(pageUrl)
  dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=subtitle, summary=summary, thumb=thumb, duration=duration), pageUrl=pageUrl))
  
####################################################
# Extracts video duration in ms or None if 0 or not available
def ExtractDuration(pageUrl):
  titles = HTML.ElementFromURL(pageUrl, errors='ignore').xpath('//div[@class="contentBox mainInfo"]/div/ul/li[@class="details"]/dl/dt')
  defs = HTML.ElementFromURL(pageUrl, errors='ignore').xpath('//div[@class="contentBox mainInfo"]/div/ul/li[@class="details"]/dl/dd')
  count = 0
  for title in titles:
    if(title.text.find('Time') > -1):
      timeTokens = defs[count].text.strip().split()
      hours = 0
      mins = 0
      sec = 0
      for token in timeTokens:
        if(token.find('h') > -1):
          hours = int(token.strip('h'))
        if(token.find('m') > -1):
          mins = int(token.strip('m'))
        if(token.find('s') > -1):
          sec = int(token.strip('s'))
          
      duration = hours*60*60 + mins*60 + sec
      if(duration > 0):
        return 1000 * duration
        
    count = count + 1
  
  return None

#####################################
def PlayVideo(sender, pageUrl):
  hd = False
  end = len(pageUrl)
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
      #Log("Photo page URL:"+photoPageUrl)
      id = photoPageUrl.replace("http://photo.mpora.com/photo/","").replace("/","")
      #id = photoPageUrl[index+1:len(photoPageUrl)]
      #Log("Photo ID:"+id)
      photoUrl = ORIGINAL_PHOTO_URL % id
      thumb = SMALL_PHOTO_URL % id
      dir.Append(PhotoItem(photoUrl, title=title, Summary=None, thumb=thumb))
  return dir
  
