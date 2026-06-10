import base64, sys
data = base64.b64decode(sys.argv[1]).decode("utf-8")
open("interactive_podcast_studio.py","w",encoding="utf-8").write(data)
print("written", len(data))
