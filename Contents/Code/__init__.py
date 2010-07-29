import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

MPORA_VIDEO_PREFIX      = "/video/mpora"
MPORA_PHOTO_PREFIX      = "/photos/mpora"

MPORA_URL 		  = "http://mpora.com/"
VIDEO_MPORA_URL   = "http://video.mpora.com/%s"
PAGED_VIDEO_MPORA_URL   = "http://video.mpora.com/%s/%d"

VIDEO_DETAILS = "http://api.mpora.com/tv/player/load/vid/%s"

PHOTO_MPORA_URL   = "http://photo.mpora.com/%s"
ORIGINAL_PHOTO_URL = "http://cdn.static.mpora.com/photo/%s_o.jpg"
SMALL_PHOTO_URL = "http://cdn.static.mpora.com/photo/%s_t.jpg"
CACHE_INTERVAL    = 1800
USE_HD_PREF_KEY = "usehd"

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
  dir.Append(Function(DirectoryItem(PaginatedVideos, title="Featured Videos", thumb=R(ICON)), path="all/featured"))
  dir.Append(Function(DirectoryItem(PaginatedVideos, title="Recently Added", thumb=R(ICON)), path="all/recent"))
  dir.Append(Function(DirectoryItem(PaginatedVideos, title="High Def Videos", thumb=R(ICON)), path="all/hd"))
  dir.Append(Function(DirectoryItem(BrandChannels, title="Brand Channels", thumb=R(ICON)), path="all"))
  dir.Append(Function(DirectoryItem(PaginatedVideos, title="Brand Videos", thumb=R(ICON)), path="all/brands"))
  dir.Append(Function(SearchDirectoryItem(Search, title=L("Search..."), prompt=L("Search for Videos"), thumb=R('search.png'))))
  dir.Append(PrefsItem(L("Preferences..."), thumb=R('icon-prefs.png')))
  return dir

#########################################################
def MainMenuPictures():
  dir = MediaContainer(mediaType='pictures')
  dir.Append(Function(DirectoryItem(Photos, title="Featured Photos"), path='all/featured'))
  dir.Append(Function(DirectoryItem(Photos, title="Popular Photos"), path='all/popular'))
  AddSportsChannels(dir, video=False)
  return dir

#######################################################################  
def Search(sender, query):
  path = 'search/'+query+'/relevance'
  return PaginatedVideos(sender, path, increment=21)
  
def CreatePrefs():
  Prefs.Add(id=USE_HD_PREF_KEY, type='bool', default=True, label='Display in High Def if available')
  
###################################################
def HotVideos(sender, url=MPORA_URL):
  dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
  Log("URL:"+url)
  for item in XML.ElementFromURL(url, True, errors='ignore').xpath('//div[@id="top10ContentContainer"]/ul/li'):
    pageUrl = item.xpath(".//div[@class='top10title']/a")[0].get('href')
    Log("PageURL:"+pageUrl)
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
  dir.Append(Function(DirectoryItem(SportChannel, title="MTB", thumb=R(ICON)), path='mountainbiking', video=video))
  dir.Append(Function(DirectoryItem(SportChannel, title="Snowboard", thumb=R(ICON)), path='snowboarding', video=video))
  dir.Append(Function(DirectoryItem(SportChannel, title="Surf", thumb=R(ICON)), path='surfing', video=video))
  dir.Append(Function(DirectoryItem(SportChannel, title="Skate", thumb=R(ICON)), path='skateboarding', video=video))
  dir.Append(Function(DirectoryItem(SportChannel, title="BMX", thumb=R(ICON)), path='bmx', video=video))
  dir.Append(Function(DirectoryItem(SportChannel, title="Moto", thumb=R(ICON)), path='motocross', video=video))
  dir.Append(Function(DirectoryItem(SportChannel, title="Ski", thumb=R(ICON)), path='skiing', video=video))
  dir.Append(Function(DirectoryItem(SportChannel, title="Wake", thumb=R(ICON)), path='wakeboarding', video=video))
  dir.Append(Function(DirectoryItem(SportChannel, title="Outdoor", thumb=R(ICON)), path='outdoor', video=video))
  
############################################################
def SportChannel(sender, path, video=True):
  dir = MediaContainer(title2=sender.itemTitle)
  if(video):
    dir.Append(Function(DirectoryItem(HotVideos, title="Popular Videos", thumb=R(ICON)), url=MPORA_URL+path))
    dir.Append(Function(DirectoryItem(PaginatedVideos, title="Featured Videos", thumb=R(ICON)), path=path+"/featured"))
    dir.Append(Function(DirectoryItem(PaginatedVideos, title="Recently Added", thumb=R(ICON)), path=path+"/recent"))
    dir.Append(Function(DirectoryItem(PaginatedVideos, title="High Def Videos", thumb=R(ICON)), path=path+"/hd"))
    #dir.Append(Function(DirectoryItem(PaginatedMovies, title="Movies"), path=path+"/movies"))
    dir.Append(Function(DirectoryItem(BrandChannels, title="Brand Channels", thumb=R(ICON)), path=path))
    dir.Append(Function(DirectoryItem(PaginatedVideos, title="Brand Videos", thumb=R(ICON)), path=path+"/brands"))
  else:
    dir.Append(Function(DirectoryItem(Photos, title="Featured Photos"), path=path+"/featured"))
    dir.Append(Function(DirectoryItem(Photos, title="Popular Photos"), path=path+"/popular"))
  return dir
  
#############################################################################
def PaginatedVideos(sender, path, page=0, increment=20):
  dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
  
  if(page == 0):
    url = VIDEO_MPORA_URL % path 
  else:
    url = PAGED_VIDEO_MPORA_URL % (path, page)
  for item in XML.ElementFromURL(url, True, errors='ignore').xpath('//div[@class="contentBox double featured"]/div/ul/li/a'):
    if(item.xpath('img')):
      videoUrl = item.get('href')
      VideoItemExtraction(dir, videoUrl)
  for item in XML.ElementFromURL(url,True, errors='ignore').xpath('//ul[@class="pagination"]/li/a'):
    if(item.text.startswith('Next')):
      dir.Append(Function(DirectoryItem(PaginatedVideos, title="More...", thumb=R(ICON)), path=path, page=page+increment))
      break
  return dir
  
#############################################################################
# TODO: add extraction of movie details, which appears different than video (URL starts with tv)
#       The movie links don't work on the site (18/6) and don't work directly, so leave alone for
#       now
#
def PaginatedMovies(sender, path, page=0):
  dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
  if(page == 0):
    url = VIDEO_MPORA_URL % path
  else:
    url = PAGED_VIDEO_MPORA_URL % (path, page)
  for item in XML.ElementFromURL(url,True, errors='ignore').xpath('//div[@class="contentBox triple large"]/div/ul/li/a'):
    if(item.xpath('img')):
      videoUrl = item.get('href')
      dir.Append(MovieItem(videoUrl))
      
  dir.Append(Function(DirectoryItem(PaginatedMovies, title="More..."), path=path, page=page+20))
  return dir

#########################################################
def BrandChannels(sender, path):
  dir = MediaContainer(title2=sender.itemTitle)
  url = "http://mpora.com/%s/brands" % path
  for item in XML.ElementFromURL(url,True, errors='ignore').xpath('//div[@class="contentBox double featured proTeam"]/div/ul/li'):
    if(item.xpath("a/img")):
      title = item.xpath("h3/a")[0].text
      thumb = item.xpath("a/img")[0].get('src') + "#index.jpg"
      brand = item.xpath("h3/a")[0].get('href')
      dir.Append(Function(DirectoryItem(BrandChannel, title=title, thumb=thumb), brand=brand))
  return dir
  
########################################################
def BrandChannel(sender, brand, page=0):
  dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
  if(page == 0):
    url = "http://mpora.com%svideos/" % brand
  else:
    url = "http://mpora.com%svideos/%d" % (brand, page)
  
  for item in XML.ElementFromURL(url,True, errors='ignore').xpath('//div[@class="contentBox triple sixteenNine large"]/div/ul/li/a'):
    if(item.xpath('img')):
      videoUrl = item.get('href')
      VideoItemExtraction(dir, videoUrl)
  for item in XML.ElementFromURL(url,True, errors='ignore').xpath('//ul[@class="pagination"]/li/a'):
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
    hdAvailable = XML.ElementFromURL(pageUrl,True, errors='ignore').xpath('//h3[@class="definitionLink hd"]')
    if(hdAvailable):
      if(Prefs.Get(USE_HD_PREF_KEY)):
        subtitle = "High Def\n"   
        pageUrl = pageUrl +"hd/"
  
  title = XML.ElementFromURL(pageUrl,True, errors='ignore').xpath('//meta[@name="title"]')[0].get('content').strip()
  summary = XML.ElementFromURL(pageUrl,True, errors='ignore').xpath('//meta[@name="description"]')[0].get('content').strip()
  thumb = XML.ElementFromURL(pageUrl,True, errors='ignore').xpath('//link[@rel="image_src"]')[0].get('href').strip() + "#index.jpg"
  duration = ExtractDuration(pageUrl)
  dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=subtitle, summary=summary, thumb=thumb, duration=duration), pageUrl=pageUrl))
  
####################################################
# Extracts video duration in ms or None if 0 or not available
def ExtractDuration(pageUrl):
  titles = XML.ElementFromURL(pageUrl,True, errors='ignore').xpath('//div[@class="contentBox mainInfo"]/div/ul/li[@class="details"]/dl/dt')
  defs = XML.ElementFromURL(pageUrl,True, errors='ignore').xpath('//div[@class="contentBox mainInfo"]/div/ul/li[@class="details"]/dl/dd')
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
  rssUrl = XML.ElementFromURL(rssPageUrl,True, errors='ignore').xpath('//response/configuration/video')[0].get('url')
  videoUrl = XML.ElementFromURL(rssUrl,True, errors='ignore').xpath('//rss/channel/item/enclosure')[0].get('url')
  return Redirect(videoUrl)

#########################################################
def Photos(sender, path):
  dir = MediaContainer(viewGroup='Photos', title2=sender.itemTitle)
  url = PHOTO_MPORA_URL % path
  for item in XML.ElementFromURL(url,True, errors='ignore').xpath('//div[@class="contentBox many"]/div/ul/li/a'):
    if(item.xpath('img')):
      title = item.get('title')
      photoPageUrl = item.get('href')
      index = photoPageUrl.rfind("/")
      id = photoPageUrl[index+1:len(photoPageUrl)]
      photoUrl = ORIGINAL_PHOTO_URL % id
      thumb = SMALL_PHOTO_URL % id
      dir.Append(PhotoItem(photoUrl, title=title, Summary=None, thumb=thumb))
  return dir
  
