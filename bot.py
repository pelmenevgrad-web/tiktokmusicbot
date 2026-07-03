import telebot
import requests
import yt_dlp
import os
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN") 
CHANNEL_ID = os.environ.get("CHANNEL_ID")

bot = telebot.TeleBot(BOT_TOKEN)

# Указываем стандартный путь для Linux серверов (на Render ffmpeg установится сюда)
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': '%(title)s.%(ext)s',
    'quiet': True,
    'nocheckcertificate': True,
    'ffmpeg_location': '/usr/bin/ffmpeg' 
}

def get_trends(region='ua'):
    url = f"https://itunes.apple.com/search?term=top&country={region}&media=music&limit=3"
    response = requests.get(url).json()
    tracks = []
    for item in response.get('results', []):
        artist = item.get('artistName')
        track = item.get('trackName')
        tracks.append(f"{artist} - {track}")
    return tracks

def download_music(query):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query} Audio", download=True)
            filename = ydl.prepare_filename(info)
            mp3_filename = filename.rsplit('.', 1)[0] + '.mp3'
            return mp3_filename
    except Exception as e:
        print(f"Ошибка при скачивании {query}: {e}")
        return None

def post_to_channel(track_name, file_path):
    try:
        with open(file_path, 'rb') as audio:
            caption = f"🎵 **{track_name}**\n\n🔥 Тренд из TikTok / Apple Music\n🎧 Полная версия!"
            bot.send_audio(
                chat_id=CHANNEL_ID, 
                audio=audio, 
                caption=caption, 
                parse_mode='Markdown'
            )
        print(f"✅ Успешно отправлен ПОЛНЫЙ ТРЕК: {track_name}")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

def main():
    print("🚀 Бот запущен на Render! Ищем полные треки...")
    ua_tracks = get_trends('ua')
    us_tracks = get_trends('us')
    all_tracks = ua_tracks + us_tracks

    for track in all_tracks:
        print(f"⏳ Обрабатываем: {track}")
        file_path = download_music(track)
        
        if file_path and os.path.exists(file_path):
            post_to_channel(track, file_path)
            os.remove(file_path)
            time.sleep(5)
        else:
            print(f"⏭ Пропускаем {track}.")

    print("🎉 Готово!")

if __name__ == '__main__':
    main()
