
rm *.h264
rm *.mp3
rm *.mpg
sleep 2; arecord -D plughw:0,0 -d 10 -r 8000 -f s16_le -c 1 | lame - audio.mp3 &
raspivid -o video.h264 -t 10000 -w 320 -h 240 -fps 30 -vf 


#arecord -q -d 10 -r 8000 -c1 | lame -S -x -h -b 64 - audio.mp3 &

ffmpeg -i audio.mp3 -i video.h264 video_audio.mpg
