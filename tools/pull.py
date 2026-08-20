#!/usr/bin/env python3
"""Pull a file from OneDrive by path, via Graph. Refreshes the rclone token as needed."""
import json, re, sys, os, time, fcntl, urllib.request, urllib.parse, configparser

CONF = os.path.expanduser('~/.config/rclone/rclone.conf')
CLIENT_ID = 'b15665d9-eda6-4092-8539-0eec376afd59'
ROOT = 'Games/Tabletop'

def load_token():
    cp = configparser.ConfigParser(); cp.read(CONF)
    return json.loads(cp['onedrive']['token']), cp

def save_token(tok):
    cp = configparser.ConfigParser(); cp.read(CONF)
    cp['onedrive']['token'] = json.dumps(tok)
    with open(CONF, 'w') as f: cp.write(f)

LOCK = os.path.expanduser('~/.config/rclone/.token.lock')

def access_token():
    """Serialised across processes: refresh tokens are single-use, so a concurrent
    refresh invalidates its siblings. Hold an exclusive lock across check-and-refresh."""
    with open(LOCK, 'w') as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        return _access_token_locked()

def _access_token_locked():
    tok, _ = load_token()
    exp = tok.get('expiry', '')
    fresh = exp and time.strptime(exp[:19], '%Y-%m-%dT%H:%M:%S') > time.gmtime(time.time() + 120)
    if fresh:
        return tok['access_token']
    data = urllib.parse.urlencode({
        'client_id': CLIENT_ID, 'grant_type': 'refresh_token',
        'refresh_token': tok['refresh_token'],
    }).encode()
    r = urllib.request.urlopen(
        'https://login.microsoftonline.com/common/oauth2/v2.0/token', data, timeout=60)
    new = json.load(r)
    tok['access_token'] = new['access_token']
    tok['refresh_token'] = new.get('refresh_token', tok['refresh_token'])
    tok['expiry'] = time.strftime('%Y-%m-%dT%H:%M:%SZ',
                                  time.gmtime(time.time() + new.get('expires_in', 3600)))
    save_token(tok)
    return tok['access_token']

def pull(relpath, dest):
    at = access_token()
    enc = urllib.parse.quote(f'{ROOT}/{relpath}')
    req = urllib.request.Request(
        f'https://graph.microsoft.com/v1.0/me/drive/root:/{enc}',
        headers={'Authorization': f'Bearer {at}'})
    meta = json.load(urllib.request.urlopen(req, timeout=60))
    url = meta.get('@microsoft.graph.downloadUrl') or meta['@content.downloadUrl']
    with urllib.request.urlopen(url, timeout=600) as r, open(dest, 'wb') as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    return meta['size'], os.path.getsize(dest)

if __name__ == '__main__':
    rel = sys.argv[1]
    dest = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(rel)
    want, got = pull(rel, dest)
    print(f'{dest}: {got:,} bytes' + ('' if want == got else f' (MISMATCH, expected {want:,})'))
