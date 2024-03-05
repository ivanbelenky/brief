import os
import sys


def build_meta(commit_message: str) -> int:
    with open(commit_message, 'r') as f: commit_message = f.read().strip()
    print(f"commit_message: {commit_message}")

    if commit_message.startswith('no-meta'):
        return 0
    try:
        category, visible = commit_message.split(',')
        visible = int(visible)
    except ValueError:
        print("Invalid commit message. Expected format: 'category,visible' or 'no-meta' "
              "if unrelated to new article")
        return 1

    print(f"category: {category}, visible: {visible}")

    briefings = [b.strip('.md') for b in os.listdir('briefings')]
    briefings_meta = [bm.strip('.meta') for bm in os.listdir('briefings/.meta')]
    for b in briefings:
        if b not in briefings_meta:
            with open(f'briefings/.meta/{b}.meta', 'w') as f:
                f.write(f"category: {category}\nvisible: {visible}\n")
            print(f"Created meta file for {b}")
    for bm in briefings_meta:
        if bm not in briefings:
            os.remove(f'briefings/.meta/{bm}.meta')
            print(f"Removed meta file for {bm}")
    os.system('git add briefings/')
    return 0

def install_hook():
    hook = """#!/bin/sh\npython3 build_meta.py $1\n"""
    with open('.git/hooks/prepare-commit-msg', 'w') as f:
        f.write(hook)
    os.system('chmod +x .git/hooks/prepare-commit-msg')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'install':
        install_hook()
    else:
        if len(sys.argv) < 2:
            print("Usage: python3 build_meta.py <commit_message>")
            sys.exit(1)
        sys.exit(build_meta(sys.argv[1]))
