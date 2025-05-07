import sys
import edge_tts
import os

VOICE = "en-US-AvaMultilingualNeural"
OUTPUT_FILE = "audio.mp3"


def main(text, dir) -> None:
    """Main function"""
     
    communicate = edge_tts.Communicate(text, VOICE)
    communicate.save_sync(dir + '\\' + OUTPUT_FILE)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            text = f.read()
    else:
        print("Missing the file name")
        exit
  

    dir = os.path.dirname(sys.argv[1])
    main(text, dir)