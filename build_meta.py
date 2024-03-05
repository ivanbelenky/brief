import os
from datetime import datetime
import sys

def build_meta():
    commit_message = sys.argv[1]
    category, visible = commit_message.split(',')
    visible = int(visible)
    print(f"category: {category}, visible: {visible}")
    briefings = os.listdir('briefings')
    briefings_meta = os.listdir('briefings/.meta')
    for briefing in briefings:
        if briefing not in briefings_meta:
            with open(f'briefings/.meta/{briefing}.meta', 'w') as f:
                f.write(f"{category}\n{visible}\n{datetime.utcnow()}")
    for briefing_meta in briefings_meta:
        if briefing_meta not in briefings:
            os.remove(f'briefings/.meta/{briefing_meta}')


if __name__ == "__main__": build_meta()