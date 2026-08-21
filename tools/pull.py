#!/usr/bin/env python3
"""Pull a file from OneDrive by path, via Microsoft Graph.

Why this exists: Debian's rclone 1.60.1 cannot DOWNLOAD from personal OneDrive
(`unauthenticated`), though listing works fine. So rclone owns auth and we own transfer.

Auth: rclone's OneDrive app is a *confidential* client with a baked-in secret, so we cannot
refresh the token ourselves (AADSTS70002). Instead we let rclone refresh by making it do a
trivial listing, then read the refreshed access token out of rclone.conf. Serialised behind
an flock so concurrent callers don't stampede.
"""
import json, sys, os, time, fcntl, subprocess, urllib.request, urllib.parse, configparser

CONF = os.path.expanduser('~/.config/rclone/rclone.conf')
LOCK = os.path.expanduser('~/.config/rclone/.token.lock')
REMOTE = 'onedrive'
ROOT = 'Games/Tabletop'
SKEW = 300  # refresh if it expires within 5 minutes


def _read_token():
    cp = configparser.ConfigParser(); cp.read(CONF)
    return json.loads(cp[REMOTE]['token'])


def _expiring(tok):
    exp = tok.get('expiry', '')
    if not exp:
        return True
    t = time.strptime(exp[:19], '%Y-%m-%dT%H:%M:%S')
    return t <= time.gmtime(time.time() + SKEW)


def access_token():
    with open(LOCK, 'w') as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        tok = _read_token()
        if _expiring(tok):
            # Make rclone do the refresh; it holds the client secret we don't.
            subprocess.run(['rclone', 'lsf', f'{REMOTE}:{ROOT}', '--max-depth', '1',
                            '--contimeout', '20s', '--timeout', '40s'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            tok = _read_token()
        return tok['access_token']


def pull(relpath, dest):
    at = access_token()
    enc = urllib.parse.quote(f'{ROOT}/{relpath}')
    req = urllib.request.Request(
        f'https://graph.microsoft.com/v1.0/me/drive/root:/{enc}',
        headers={'Authorization': f'Bearer {at}'})
    meta = json.load(urllib.request.urlopen(req, timeout=90))
    url = meta.get('@microsoft.graph.downloadUrl') or meta['@content.downloadUrl']
    tmp = dest + '.part'
    with urllib.request.urlopen(url, timeout=1800) as r, open(tmp, 'wb') as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    os.replace(tmp, dest)
    return meta['size'], os.path.getsize(dest)


if __name__ == '__main__':
    rel = sys.argv[1]
    dest = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(rel)
    want, got = pull(rel, dest)
    print(f'{dest}: {got:,} bytes' + ('' if want == got else f' (MISMATCH, expected {want:,})'))
