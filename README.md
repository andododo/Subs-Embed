# Subs Embed
I use this hand-in-hand with [anipy-cli](https://github.com/sdaqo/anipy-cli). Sometimes downloaded videos does not come with hardcoded subs, and just downloads a separate .vtt file. So I just merge them using this. 

Important to note: this is embedding the subs ONLY, I have a separate script for hardcoding the .vtt file. Check out [Subs-Hardcode-FFmpeg](https://github.com/andododo/Subs-Hardcode-FFmpeg).


## How to use
1. Just place the `.py` file inside the folder where the video and `.vtt` file is located.
2. Run the `.py` file.
3. The output will overwrite the source video, replacing with the merged video with embedded subs.