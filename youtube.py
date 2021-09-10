import datetime
import typing
import youtube_dl
from aiocqhttp.message import MessageSegment
from hoshino import Service
from hoshino.util.score import Score
from hoshino.util.database import (DataBaseException, NotEnoughScoreError,
                                   ScoreLimitExceededError, database,
                                   score_data, score_log, init)


cool_down = datetime.timedelta(minutes=1)  # 冷却时间
expire = datetime.timedelta(minutes=2)

temp = {}
last_check = {}

async def spend_gold(bot, ev):

	gold = Score(ev) 
    # 首先实例化类,可以传入CQEvent和CommandSession,对于定时任务,直接传入uid即可
	try:
		now_gold = gold.spend_score('5') # 花费积分,其他方法见源码
		await bot.send(ev, f'你花掉了5 积分，你现在有{now_gold} 积分')
	except NotEnoughScoreError as e: 
        # 积分不够花
        # 判断积分是否够用还可以使用`check_score`方法,这样就不用处理异常
		await bot.finish(
            ev, f'你只有{e.args[1]} 积分，不够用于消费')
        # 从异常信息中获取参数(args1:现有积分数,args2:需要花掉的积分数)
	except ScoreLimitExceededError as e: 
        # 积分花太多(没有启用花费上限可以不用处理)
		await bot.finish(ev, f'你今天已经花了{e.args[0]} 积分了，请明天再来吧')
	except DataBaseException as e: # 数据库操作失败
		await bot.finish(ev, f'花费积分失败(Error:{e})，请联系维护组')





sv = Service('下载youtube视频', help_='''
youtube下载+网页地址
'''.strip())

async def search_youtube(youtube_link):
  ydl_opts = {
        'format': 'mp4',
        'outtmpl': '/www/wwwroot/192.168.0.231/%(id)s.mp4'
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
           msg = '[CQ:image,file='+ str(thumbnail) +']\n标题：' + str(title) + '\n作者：' + str(uploader) +'\n请回复"QQ下载"或者"网页下载"'
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
           msg = '[CQ:image,file='+ str(thumbnail) +']\n歌名：' + str(title) + '\n作者：' + str(uploader) +'\n请回复"QQ下载"或者"网页下载"'
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
           msg = '[CQ:image,file='+ str(thumbnail) +']\n标题：' + str(title) + '\n作者：' + str(uploader) +'\n请回复"QQ下载"或者"网页下载"'
           key = f'{ev.group_id}-{ev.user_id}'
           temp["key"] = key
           temp["youtube_link"] =  youtube_link    
           await bot.send(ev, msg)
           
        elif video_info['extractor'] == 'youtube':
           await bot.send(ev, '获取油管视频信息中！')
          
           id = video_info['id']
           title = video_info['title']
           uploader = video_info['uploader']
           thumbnail = 'https://i.ytimg.com/vi/' + str(id) +'/hqdefault.jpg?sqp=-oaymwEZCNACELwBSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLBTdBfxLI18e8Vv5m2jf8ViQKlD2A'
           msg = '[CQ:image,file='+ str(thumbnail) +']\n标题：' + str(title) + '\n作者：' + str(uploader) +'\n请回复"QQ下载"或者"网页下载"'
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
  await bot.send(ev, '请先发送"油管下载"搜索需要下载的视频哦！')
 else:
  await spend_gold(bot, ev)
  await bot.send(ev, '请稍等片刻~,视频正在下载中')
  url = temp['youtube_link']
  print(url)
  ydl_opts = {
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '/www/wwwroot/192.168.0.231/%(id)s.mp4',
                'external_downloader': '/usr/local/bin/aria2c',
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
  file = '/www/wwwroot/192.168.0.231/' + str(id) +'.mp4'
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
  await bot.send(ev, '请先发送"油管下载"搜索需要下载的视频哦！')
 else:
  await spend_gold(bot, ev)
  await bot.send(ev, '请稍等片刻~,视频正在下载中')
  url = temp['youtube_link']
  print(url)
  ydl_opts = {
        'format': 'bestvideo[filesize<50M]+bestaudio[ext=m4a]/bestvideo+bestaudio',
        'outtmpl': '/www/wwwroot/192.168.0.231/%(id)s',
        'external_downloader': '/usr/local/bin/aria2c',
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
  msg = '视频格式为'+ str(requested_formats)+ str(fps) + 'fps\n下载链接为：https://ytdown.bili.moe/'+ str(id) + '.mkv'
  del temp["key"]
  del temp["youtube_link"]
  await bot.send(ev, msg)
