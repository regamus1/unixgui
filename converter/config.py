import os
home = os.getenv("HOME")
videos = os.getcwd() + "/videos"
output = os.getcwd() + "/output"

default_ffmpeg_cmd = ''
video_formats = [
        '3g2', '3gp', 'aac', 'ac3', 'avi', 'dv', 'flac', 'flv', 'm4a', 'm4v',
        'mka', 'mkv', 'mov', 'mp3', 'mp4', 'mpg', 'ogg', 'vob', 'wav', 'webm',
        'wma', 'wmv'
        ]