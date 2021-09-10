# youtube_dl_hoshino
Hoshinobot调用YouTube_dl来下载YouTube/Twitter/Tiktok视频

# 安装方法
安装youtube-dl和aria2c
```
apt/yum install youtube-dl

pip/pip3 install youtube-dl

wget -N git.io/aria2.sh && chmod +x aria2.sh

```

在 HoshinoBot\hoshino\modules 目录下使用以下命令拉取本项目
```
git clone https://github.com/haha114514/youtube_dl_hoshino.git
```

然后在 HoshinoBot\\hoshino\\config\\\__bot__.py 文件的 MODULES_ON 加入 youtube_dl_hoshino

修改youtubedown.py里面的 第 14-16行为你指定的参数.

重启 HoshinoBot

# 使用方法

群内发送 偷视频+视频链接（支持YouTube Tiktok Twitter 网易云MV）

等待bot返回视频信息之后，发送 QQ下载 或者 网页下载

QQ下载即通过QQ文件发送视频

网页下载即发送视频下载网页地址
