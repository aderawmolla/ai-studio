rm -f cache/index.json outputs/narration/*.wav
python3 main.py audio
python3 main.py assemble
rm -f cache/index.json
<!-- when audio not working -->

problems 
- zooming problem
- pausing of images
- final sync
- end card problem
- timing of tts and our contract