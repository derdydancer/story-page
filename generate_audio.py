import sys
import edge_tts
import os

VOICE = "en-US-AvaMultilingualNeural"


def main(text, dir, output_file) -> None:
    """Main function"""
     
    communicate = edge_tts.Communicate(text, VOICE)
    communicate.save_sync(dir + '\\' + output_file)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            text = f.read()
    else:
        print("Missing the file name")
        exit
  
    dir = os.path.dirname(sys.argv[1])

    output_file = os.path.basename(sys.argv[1]).split('.')[0] + '.mp3'

    main(text, dir, output_file)