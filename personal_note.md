rm -f cache/index.json outputs/narration/*.wav
python3 main.py audio
python3 main.py assemble
rm -f cache/index.json

python3 main.py validate        # storyboard schema
python3 main.py validate-media  # files exist (needs keyframe + clip + narration per shot)
python3 main.py assemble
python3 main.py final-check
<!-- when audio not working -->

problems 
- zooming problem
- pausing of images
- final sync
- end card problem
- timing of tts and our contract