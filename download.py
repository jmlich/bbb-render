#!/usr/bin/python3

import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


class Downloader:

    def __init__(self, url, outdir):
        m = re.match(r'^.*/playback/presentation/2\.0/playback.html\?meetingId=(\S+)$', url)
        if m is None:
            raise ValueError(f"Does not look like a BBB playback URL: {url}")

        id = m.group(1)
        self.base_url = urllib.parse.urljoin(url, f"/presentation/{id}/")
        self.outdir = outdir

    def _get(self, path):
        url = urllib.parse.urljoin(self.base_url, path)
        outpath = os.path.join(self.outdir, path)
        os.makedirs(os.path.dirname(outpath), exist_ok=True)

        print(f"Downloading {url}...")
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'bbb-video-downloader/1.0')
        with urllib.request.urlopen(req) as resp, open(outpath, 'wb') as fp:
            buf = bytearray(64 * 1024)
            n = resp.readinto(buf)
            while n > 0:
                fp.write(buf[:n])
                n = resp.readinto(buf)
        return outpath

    def download(self):
        self._get('metadata.xml')
        shapes = self._get('shapes.svg')
        doc = ET.parse(shapes)
        for imgurl in {img.get('{http://www.w3.org/1999/xlink}href')
                       for img in doc.iterfind('.//{http://www.w3.org/2000/svg}image')}:
            self._get(imgurl)

        self._get('panzooms.xml')
        self._get('cursor.xml')
        self._get('deskshare.xml')
        self._get('presentation_text.json')
        self._get('captions.json')
        self._get('slides_new.xml')

        self._get('video/webcams.webm')
        self._get('deskshare/deskshare.webm')


def main(argv):
    if len(argv) != 3:
        sys.stderr.write('usage: {} PRESENTATION-URL OUTPUT-DIR\n'.format(argv[0]))
        return 1
    d = Downloader(argv[1], argv[2])
    d.download()


if __name__ == '__main__':
    sys.exit(main(sys.argv))