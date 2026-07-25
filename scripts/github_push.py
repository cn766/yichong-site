#!/usr/bin/env python3
"""Push local changes to GitHub via REST API - optimized version"""

import hashlib
import json
import os
import subprocess
import urllib.request

REPO_ROOT = r'c:\Users\cn\.trae-cn\work\6a16a760ff8af3f6424fba73\异宠网站\yichong-site'
OWNER = "cn766"
REPO = "yichong-site"
BASE_REF = "main"
TOKEN = os.environ.get('GITHUB_TOKEN', '')

def api_call(method, path, data=None):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("Content-Type", "application/json")
    if data is not None:
        req.data = json.dumps(data).encode('utf-8')
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode('utf-8'))

def git_blob_sha(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()
    header = f"blob {len(content)}\0".encode('utf-8')
    return hashlib.sha1(header + content).hexdigest()

def main():
    os.chdir(REPO_ROOT)
    print("Step 1: Getting GitHub base commit...")
    ref_data = api_call("GET", f"/git/refs/heads/{BASE_REF}")
    base_commit = ref_data['object']['sha']
    print(f"  GitHub base: {base_commit}")

    print("Step 2: Getting GitHub file list...")
    commit_info = api_call("GET", f"/git/commits/{base_commit}")
    tree_info = api_call("GET", f"/git/trees/{commit_info['tree']['sha']}?recursive=1")
    github_files = {e['path']: e['sha'] for e in tree_info.get('tree', []) if e['type'] == 'blob'}
    print(f"  GitHub files: {len(github_files)}")

    print("Step 3: Computing local diffs...")
    # Get tracked files from git
    tracked = subprocess.check_output(['git', 'ls-tree', '-r', 'HEAD', '--name-only'], text=True).strip().split('\n')
    tracked = [t for t in tracked if t]
    
    to_upload = []
    for relpath in tracked:
        if not os.path.exists(relpath):
            continue
        local_sha = git_blob_sha(relpath)
        if github_files.get(relpath) != local_sha:
            to_upload.append(relpath)
    
    # Find deleted
    local_set = set(tracked)
    to_delete = [p for p in github_files if p not in local_set]
    
    print(f"  Upload: {len(to_upload)}, Delete: {len(to_delete)}")

    if not to_upload and not to_delete:
        print("Already up to date!")
        return

    print("Step 4: Creating blobs...")
    tree_items = []
    for i, relpath in enumerate(to_upload, 1):
        fullpath = os.path.join(REPO_ROOT, relpath)
        with open(fullpath, 'rb') as f:
            content = f.read()
        is_binary = b'\x00' in content[:8000]
        if is_binary:
            import base64
            blob_data = {"content": base64.b64encode(content).decode('ascii'), "encoding": "base64"}
        else:
            blob_data = {"content": content.decode('utf-8'), "encoding": "utf-8"}
        try:
            blob = api_call("POST", "/git/blobs", blob_data)
            tree_items.append({"path": relpath, "mode": "100644", "type": "blob", "sha": blob['sha']})
            print(f"  [{i}/{len(to_upload)}] {relpath}")
        except Exception as e:
            print(f"  ERROR {relpath}: {e}")

    for relpath in to_delete:
        tree_items.append({"path": relpath, "mode": "100644", "type": "blob", "sha": None})
        print(f"  [DEL] {relpath}")

    print(f"Step 5: Creating tree ({len(tree_items)} items)...")
    tree_data = {"base_tree": commit_info['tree']['sha'], "tree": tree_items}
    new_tree = api_call("POST", "/git/trees", tree_data)
    print(f"  New tree: {new_tree['sha']}")

    print("Step 6: Creating commit...")
    commit_msg = subprocess.check_output(['git', 'log', '-1', '--format=%B'], text=True).strip()
    commit_data = {"message": commit_msg, "tree": new_tree['sha'], "parents": [base_commit]}
    new_commit = api_call("POST", "/git/commits", commit_data)
    print(f"  New commit: {new_commit['sha']}")

    print("Step 7: Updating ref...")
    api_call("PATCH", f"/git/refs/heads/{BASE_REF}", {"sha": new_commit['sha'], "force": False})
    print(f"SUCCESS: Pushed to {BASE_REF}")

if __name__ == '__main__':
    main()
