import sys
import os
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import zipfile

if len(sys.argv) < 2:
    print('Usage: python download_and_extract_repo.py <repo_https_url>')
    sys.exit(1)

repo_url = sys.argv[1].rstrip('/')
# Construct archive URL for main branch
archive_url = repo_url + '/archive/refs/heads/main.zip'
print('Downloading', archive_url)

out_zip = 'repo_archive.zip'
try:
    with urlopen(archive_url) as resp, open(out_zip, 'wb') as out:
        out.write(resp.read())
except HTTPError as e:
    print('HTTP Error:', e)
    sys.exit(2)
except URLError as e:
    print('URL Error:', e)
    sys.exit(2)

print('Extracting', out_zip)
with zipfile.ZipFile(out_zip, 'r') as zf:
    zf.extractall('.')

# Move extracted folder to a predictable name
extracted_dirs = [n for n in os.listdir('.') if n.startswith('fiber-fault-detector-') and os.path.isdir(n)]
if extracted_dirs:
    src = extracted_dirs[0]
    dst = 'fiber-fault-detector'
    if os.path.exists(dst):
        print('Removing existing', dst)
        import shutil
        shutil.rmtree(dst)
    os.rename(src, dst)
    print('Repository extracted to', dst)
else:
    print('Extraction failed: expected folder not found')

# cleanup
os.remove(out_zip)
print('Done')
