from asyncio.windows_events import NULL
import discord
from discord import channel
from discord import VoiceClient
import youtube_dl
import asyncio

client = discord.Client()

token = "ODU2MjQxNTIyMjgyMjAxMTQ5.YM-LDw.c8T9odbK5S-bpbHiC8yIbv-3DDQ"

# notice = open("notice.txt", encoding="utf8")

# line = notice.readline()

# notice.close()

@client.event
async def on_ready():
    game = discord.Game("채널 관리")
    await client.change_presence(status = discord.Status.online, activity = game)

@client.event
async def on_message(message):
    # 명령어를 친 사용자가 있는 음성채널로 입장
    if message.content.startswith("@입장"):
        if message.author.voice.channel:
            print(message.author.voice.channel)
            channel = message.author.voice.channel
            voice = await channel.connect()
            await message.channel.send("입장합니다")

    # 음성채널에서 퇴장
    if message.content.startswith("@퇴장"):
        for vc in client.voice_clients:
            if vc.guild == message.guild:
                voice = vc

        await voice.disconnect()
        await message.channel.send("퇴장합니다.")

    if message.content.startswith("@재생"):
        for vc in client.voice_clients:
            if vc.guild == message.guild:
                voice = vc

        url = message.content.split(" ")[1]
        option = {'outmpl' : "file/" + url.split("=")[1] + ".mp3"}
        
        with youtube_dl.YoutubeDL(option) as ydl:
             ydl.download([url])
             info = ydl.extract_info(url, download=False)
             title = info["title"]

        voice.play(discord.FFmpegPCMAudio("file/" + url.split('=')[1] + ".mp3"))
        await message.channel.send("[" + title + "]을 재생합니다.")

    # 기본 메세지 보내기
    if message.content.startswith("@공지사항"):
        print("line")
        await message.channel.send("line")
    
    # 임베드
    if message.content.startswith("@임베드"):
        embed = discord.Embed(title="땡땡이", description = "학교종", color=0x00ff00)
        embed.add_field(name="종쳐라 제발좀", value="종쳐쫌", inline=False)
        embed.add_field(name="종쳐라 제발좀22222", value="종쳐쫌22222", inline=False)
        embed.set_footer(text="얼른얼른 보자고")
        await message.channel.send(embed = embed)

client.run(token)