import os
home = os.getenv("HOME")
default_ffmpeg_cmd = ''

video_codecs = [
        'copy', 'flv', 'h263', 'libvpx', 'libx264', 'libxvid', 'mpeg2video',
        'mpeg4', 'msmpeg4', 'wmv2'
        ]

audio_codecs = [
        'aac', 'ac3', 'copy', 'libfaac', 'libmp3lame', 'libvo_aacenc',
        'libvorbis', 'mp2', 'wmav2'
        ]

video_formats = [
        '3g2', '3gp', 'aac', 'ac3', 'avi', 'dv', 'flac', 'flv', 'm4a', 'm4v',
        'mka', 'mkv', 'mov', 'mp3', 'mp4', 'mpg', 'ogg', 'vob', 'wav', 'webm',
        'wma', 'wmv'
        ]

video_frequency_values = [
        '22050', '44100', '48000'
        ]

video_bitrate_values = [
        '32', '96', '112', '128', '160', '192', '256', '320'
        ]
