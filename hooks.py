import os
import sys
from datetime import datetime

SKIPS = ['no-meta', 'upsert-meta']
BUILD_META = 'build_meta'
ADD_COMMIT_META = 'add_commit_meta'


def build_meta(commit_message: str) -> int:
    briefings = [b.replace('.md', '') for b in os.listdir('briefings') if b.endswith('.md')]
    briefings_meta = [bm.replace('.meta', '') for bm in os.listdir('briefings/.meta') if bm.endswith('.meta')]
    print(f"briefings: {briefings}")
    print(f"briefings_meta: {briefings_meta}")

    for bm in briefings_meta:
        if bm not in briefings:
            os.remove(f'briefings/.meta/{bm}.meta')
            print(f"Removed meta file for {bm}")

    with open(commit_message, 'r') as f: commit_message = f.read().strip()
    if any(skip in commit_message for skip in SKIPS): return 0
    try:
        category, visible = commit_message.split(',')
        visible = int(visible)
    except ValueError:
        print("Invalid commit message. Expected format: 'category,visible' or 'no-meta' "
              "if unrelated to new article")
        return 1

    for b in briefings:
        if b not in briefings_meta:
            with open(f'briefings/.meta/{b}.meta', 'w') as f:
                f.write(f"{category}\n{int(bool(visible))}\n{datetime.utcnow().isoformat()}")
            print(f"Created meta file for {b}")

    print(f"category: {category}, visible: {visible}")

    return 0


def add_commit():
    os.system('git add briefings/')
    os.system('mv .git/hooks/post-commit .git/hooks/post-commit.disabled')
    os.system('git commit -m "upsert-meta" --no-verify')
    os.system('mv .git/hooks/post-commit-disabled .git/hooks/post-commit')
    return 0


HOOK_DISPATCHER = {
    BUILD_META: build_meta,
    ADD_COMMIT_META: add_commit,
}


def prepare_commit_msg_hook():
    hook = f"""#!/bin/sh\npython3 hooks.py {BUILD_META} $1\n"""
    with open('.git/hooks/prepare-commit-msg', 'w') as f:
        f.write(hook)
    os.system('chmod +x .git/hooks/prepare-commit-msg')


def post_commit_hook():
    hook = f"""#!/bin/sh\npython3 hooks.py {ADD_COMMIT_META}\n"""
    with open('.git/hooks/post-commit', 'w') as f:
        f.write(hook)
    os.system('chmod +x .git/hooks/post-commit')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'install':
        prepare_commit_msg_hook()
        post_commit_hook()
    else:
        if len(sys.argv) < 2: sys.exit(1)
        sys.exit(HOOK_DISPATCHER[sys.argv[1]](*sys.argv[2:]))
