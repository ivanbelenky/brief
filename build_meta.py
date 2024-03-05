import os
from datetime import datetime


def build_meta(commit_message: str) -> int:
    if commit_message.startswith('no-meta'): return 0
    try: category, visible = commit_message.split(',')
    except ValueError:
        print("Invalid commit message. Expected format: 'category,visible' or 'no-meta'"
              " if unrelated to new article")
        return 1
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
    return 0

def install_hook():
    hook = """#!/bin/sh\npython3 build_meta.py "$1"
"""
    with open('.git/hooks/prepare-commit-msg', 'w') as f:
        f.write(hook)
    os.system('chmod +x .git/hooks/prepare-commit-msg')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'install': install_hook()
