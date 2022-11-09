import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from youtube_dl import YoutubeDL




bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

bot.remove_command('help')
load_dotenv()
token = os.getenv('TOKEN')

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
is_playing = False
is_paused = False
music_queue = []
vc = None

def search_yt(item):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            get_info = ydl.extract_info("ytsearch:%s"% item ,download=False)['entries'][0]
        except Exception:
            return False
    return {'source': get_info['formats'][0]['url'], 'title': get_info['title']}

def play_next(ctx):
    global vc
    global music_queue
    global is_playing
    global is_paused
    if len(music_queue) > 0:
        is_playing = True

        m_url = music_queue[0][0]['source']
        music_queue.pop(0)

        vc.play(discord.FFmpegPCMAudio(m_url, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
    else:
        is_playing = False

async def play_music(ctx):
    global vc
    global music_queue
    global is_playing
    global is_paused
    
    if len(music_queue) > 0:
        is_playing = True
        m_url = music_queue[0][0]['source']

        if vc == None or not vc.is_connected():
            vc = await music_queue[0][1].connect()

            if vc == None:
                await ctx.send("kanala giremiyom pic duzelt sunu")
                return
        else:
            await vc.move_to(music_queue[0][1])

        music_queue.pop(0)
        vc.play(discord.FFmpegPCMAudio(m_url, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
    else:
        is_playing = False



@bot.command(name='play',aliases=["p"], help="muzik cal")
async def play(ctx, *args):
    query = " ".join(args)
    voice_channel = ctx.message.author.voice.channel
    global vc
    global music_queue
    global is_playing
    global is_paused
    
    song = search_yt(query)
    if type(song) == type(True):
        await ctx.send("bulamadim")
        return
    await ctx.send("muzik caliniyor: %s"% song['title'])
    music_queue.append([song, voice_channel])

    if is_playing == True:
        music_queue.append([song, voice_channel])
    elif is_playing == False:
        await play_music(ctx)


@bot.command(name='skip', aliases=["s"])
async def skip(ctx, *args):
    global vc
    global music_queue
    if vc != None and vc:
        vc.stop()
        await ctx.send("diger muzige geciom")
        await ctx.send("caliniyor: %s"% music_queue[0][0]['title'])
        await play_music(ctx)

@bot.command(name='pause', aliases=["pa"])
async def pause(ctx, *args):
    global vc
    global music_queue
    global is_paused
    if vc != None and vc:
        if is_paused == False:
            vc.pause()
            is_paused = True
        elif is_paused == True:
            vc.resume()
            is_paused = False

@bot.command(name='resume', aliases=["r"])
async def resume(ctx, *args):
    global vc
    global music_queue
    global is_paused
    if vc != None and vc:
        if is_paused == True:
            vc.resume()
            is_paused = False

bot.run(token)

