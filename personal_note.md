rm -f cache/index.json outputs/narration/*.wav
python3 main.py audio
python3 main.py assemble
<!-- when audio not working -->