import discord
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
import asyncio
from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


client = commands.Bot(command_prefix='!')

status = ['음악재생', '코딩', '채널관리']

@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='일반')
    await channel.send(f'어서옵쇼! {member.mention}!  [ **!help** ]를 입력하여 명령어를 확인하세요!')

@client.command(name='핑', help='이 명령어는 레이턴시를 반환합니다.')
async def ping(ctx):
    await ctx.send(f'{round(client.latency * 1000)}ms')

@client.command(name='재생', help='명령어를 입력한 유저의 음성채널에서 음악을 재생합니다. !재생 [유튜브 주소]')
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("현재 채널에 연결되어있지 않습니다.")
        return
    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**재생 중:** {}'.format(player.title))

@client.command(name='중지', help='현재 참여중인 음성채널을 떠납니다.')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@client.command(name='공지사항', help = '공지사항을 확인합니다.')
async def notice(ctx):
    noticeFile = open("notice.txt", 'r',encoding="utf-8")
    notice = []
    while True:
        line = noticeFile.readline()
        notice.append(line)
        if not line: break
    
    noticeTitle = notice[0]
    del notice[0]
    embed = discord.Embed(title=str(noticeTitle), description=str('\n'.join(notice)), color=0xff0000)
    await ctx.send(embed = embed)
    noticeFile.close()

@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))

client.run('ODU2MjQxNTIyMjgyMjAxMTQ5.YM-LDw.c8T9odbK5S-bpbHiC8yIbv-3DDQ')