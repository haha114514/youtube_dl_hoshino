import datetime
import typing
import yt_dlp as youtube_dl
from aiocqhttp.message import MessageSegment
from hoshino import Service


cool_down = datetime.timedelta(minutes=1)  # 冷却时间
expire = datetime.timedelta(minutes=2)

temp = {}
last_check = {}

opt_path = '/root/youtube/' #你的视频下载地址
aria2c = '/usr/local/bin/aria2c'#你的aria2文件位置
your_url = 'https://114514.com/' #你的网页下载位置
sv = Service('下载youtube视频', help_='''
youtube下载+网页地址
'''.strip())

async def search_youtube(youtube_link):
  ydl_opts = {
        'format': 'mp4',
        'outtmpl': f'{opt_path}%(id)s.mp4'
    }

  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(youtube_link, download=False)
        if 'entries' in result:
          return 0
        else:
          return result


@sv.on_prefix(('偷视频'))
async def fetch_info(bot, ev):
    youtube_link = []
    for msg_seg in ev.message:
        if msg_seg.type == 'text' and msg_seg.data['text']:
            youtube_link.append(msg_seg.data['text'].strip())
    if not youtube_link:
        await bot.send(ev, '你想下什么呀?', at_sender=True)
    else:
        
        youtube_link = ''.join(youtube_link)
        video_info = await search_youtube(youtube_link)
        if video_info == 0:
           await bot.send(ev, '暂时不支持下载多个视频呀', at_sender=True)
           
        elif video_info['extractor'] == 'twitter':
           await bot.send(ev, '获取推特视频信息中！')
          
           id = video_info['id']
           title = video_info['title']
           uploader = video_info['uploader']
           thumbnail = video_info['thumbnail']
           msg = '[CQ:image,file='+ str(thumbnail) +']\n标题：' + str(title) + '\n作者：' + str(uploader) +'\n请回复"音乐下载","QQ下载"或者"网页下载"'
           key = f'{ev.group_id}-{ev.user_id}'
           temp["key"] = key
           temp["youtube_link"] =  youtube_link    
           await bot.send(ev, msg)

        elif video_info['extractor'] == 'netease:mv':
           await bot.send(ev, '获取网易云MV信息中！')
          
           id = video_info['id']
           title = video_info['title']
           uploader = video_info['creator']
           thumbnail = video_info['thumbnail']
           msg = '[CQ:image,file='+ str(thumbnail) +']\n歌名：' + str(title) + '\n作者：' + str(uploader) +'\n请回复"音乐下载","QQ下载"或者"网页下载"'
           key = f'{ev.group_id}-{ev.user_id}'
           temp["key"] = key
           temp["youtube_link"] =  youtube_link    
           await bot.send(ev, msg)
           
        elif video_info['extractor'] == 'TikTok':
           await bot.send(ev, '获取TikTok视频信息中！')
          
           id = video_info['id']
           title = video_info['description']
           uploader = video_info['title']
           thumbnail = video_info['thumbnail']
           msg = '[CQ:image,file='+ str(thumbnail) +']\n标题：' + str(title) + '\n作者：' + str(uploader) +'\n请回复"音乐下载","QQ下载"或者"网页下载"'
           key = f'{ev.group_id}-{ev.user_id}'
           temp["key"] = key
           temp["youtube_link"] =  youtube_link    
           await bot.send(ev, msg)
           
        elif video_info['extractor'] == 'youtube':
           await bot.send(ev, '获取油管视频信息中！')
          
           id = video_info['id']
           title = video_info['title']
           uploader = video_info['uploader']
           thumbnail = video_info['thumbnail'] #webp格式，电脑端显示可能有点问题
           #thumbnail = 'https://i.ytimg.com/vi/' + str(id) +'/hqdefault.jpg?sqp=-oaymwEZCNACELwBSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLBTdBfxLI18e8Vv5m2jf8ViQKlD2A'
           msg = '[CQ:image,file='+ str(thumbnail) +']\n标题：' + str(title) + '\n作者：' + str(uploader) +'\n请回复"音乐下载","QQ下载"或者"网页下载"'
           key = f'{ev.group_id}-{ev.user_id}'
           temp["key"] = key
           temp["youtube_link"] =  youtube_link    
           await bot.send(ev, msg)
        else:
           await bot.send(ev, '是不支持的平台呢')


           
@sv.on_prefix(('QQ下载'))
async def qq_download(bot, ev):
 global temp
 key = f'{ev.group_id}-{ev.user_id}'
 if "key" not in temp:
  await bot.send(ev, '请先发送"偷视频"搜索需要下载的视频哦！')
 else:
  await spend_gold(bot, ev)
  await bot.send(ev, '请稍等片刻~,视频正在下载中')
  url = temp['youtube_link']
  print(url)
  ydl_opts = {
        'format': 'bestvideo[filesize<80m][ext=mp4]+bestaudio[ext=m4a]/best[filesize<80m][ext=mp4]',
        'outtmpl': f'{opt_path}%(id)s.mp4',
                'external_downloader': aria2c,
         'external-downloader-args': '-j 16 -x 16 -s 16 -k 1M'
    }

  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
  if 'entries' in result:
            # 播放清单
            video = result['entries'][0]
  else:
     # 单个视频
            video = result           
  id = video['id']
  requested_formats = video['requested_formats'][0]['format_note']
  fps = video['requested_formats'][0]['fps']
  file = f'{opt_path}{id}.mp4'
  print(file)
  mv = '[CQ:video,file=file:'+ str(file) + ']'
  del temp["key"]
  del temp["youtube_link"]
  msg = '本次下载视频格式为'+ str(requested_formats)+ str(fps) +'fps'
  await bot.send(ev, msg) 
  await bot.send(ev, mv)

@sv.on_prefix(('网页下载'))
async def web_download(bot, ev):
 global temp
 print(temp)
 if "key" not in temp:
  await bot.send(ev, '请先发送"偷视频"搜索需要下载的视频哦！')
 else:
  await spend_gold(bot, ev)
  await bot.send(ev, '请稍等片刻~,视频正在下载中')
  url = temp['youtube_link']
  print(url)
  ydl_opts = {
        'format': 'bestvideo+bestaudio',
        'outtmpl': f'{opt_path}%(id)s',
        'external_downloader': aria2c,
         'external-downloader-args': '-j 16 -x 16 -s 16 -k 1M'
    }

  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
  if 'entries' in result:
            # 播放清单
            video = result['entries'][0]
  else:
     # 单个视频
            video = result  
            print(video)         
  id = video['id']
  requested_formats = video['requested_formats'][0]['format_note']
  fps = video['requested_formats'][0]['fps']
  msg = f'视频格式为{requested_formats}{fps}fps\n下载链接为：{your_url}{id}.mkv'
  del temp["key"]
  del temp["youtube_link"]
  await bot.send(ev, msg)
  
@sv.on_prefix(('音乐下载'))
async def qq_download(bot, ev):
 global temp
 key = f'{ev.group_id}-{ev.user_id}'
 if "key" not in temp:
  await bot.send(ev, '请先发送"偷视频"搜索需要下载的视频哦！')
 else:
  await spend_gold(bot, ev)
  await bot.send(ev, '请稍等片刻~,音乐正在下载中')
  url = temp['youtube_link']
  print(url)
  ydl_opts = {
    'format': 'bestaudio/best',
    'external_downloader': aria2c,
    'external-downloader-args': '-j 16 -x 16 -s 16 -k 8M',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '256',
    }],
    'outtmpl': f'{opt_path}%(id)s'
}

  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
  if 'entries' in result:
            # 播放清单
            video = result['entries'][0]
  else:
     # 单个视频
            video = result           
  id = video['id']
  msg = f'音乐下载链接为：{your_url}{id}.mp3'
  del temp["key"]
  del temp["youtube_link"]
  await bot.send(ev, msg)
