# -*- coding: utf-8 -*-

import urllib.request
import json
import sys
import os

URL = 'https://tinypng.com/web/shrink'

MAX_SIZE = 5 * 1024 *1024

fail_files = []

def tinypng(path):
    f = open(path, 'rb')
    data = f.read()
    f.close()
    if len(data) > MAX_SIZE:
        print('file too big')
        raise IOError('file too big')
    headers = {
        'Content-Length': str(len(data)),
        'Content-Type': 'image/png',
        'Host': 'tinypng.com',
        'Origin': 'https://tinypng.com',
        'Referer': 'https://tinypng.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36'
    }
    req = urllib.request.Request(URL, data = data, headers = headers)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read().decode('utf-8'))


def format_size(size):
    if size < 1024:
        return str(size) + 'B'
    elif size < (1024 * 1024):
        return str(round(size/1024, 1)) + 'KB'
    else:
        return str(round(size/1024/1024, 1)) + 'MB'

def save_file(url, path):
    urllib.request.urlretrieve(url, path)

def main():
    if len(sys.argv) < 3:
        print('Usage: python3 tinypng [source] [target]')
        sys.exit(0)
    srcpath = sys.argv[1]
    descpath = sys.argv[2]
	
    if not os.path.exists(descpath):
        os.makedirs(descpath)


    statistics = {
        'totalfile': 0,
        'totalfilesize': 0,
        'totalcompresssize': 0
    }
    print('file\tbefore\tafter\tratio')
    for basedir, dirs, files in os.walk(srcpath):
        for file in files:
            filename = os.path.basename(file)
            fullname = os.path.join(basedir, file)
            relpath = os.path.relpath(basedir, srcpath)
            fulldescdir = descpath
            if relpath != '.':
                fulldescdir = os.path.join(descpath, relpath)
                if not os.path.exists(fulldescdir):
                    os.makedirs(fulldescdir)

            if os.path.splitext(file)[1].upper() == '.PNG':
                try:
                    result = tinypng(fullname)
                    if 'input' in result and 'output' in result:
                        save_file(result['output']['url'], os.path.join(fulldescdir, filename))
                        inputsize = result['input']['size']
                        outputsize = result['output']['size']
                        ratio = result['output']['ratio']
                        statistics['totalfile'] += 1
                        statistics['totalfilesize'] += inputsize
                        statistics['totalcompresssize'] += outputsize
                        print('{0}\t{1}\t{2}\t-{3}%'.format(filename, format_size(inputsize), format_size(outputsize), 100 - round(ratio * 100)))
                    else:
                        print(json.dumps(result))
                except Exception as ex:
                    fail_files.append(fullname)
                    print('error during compress: ' + filename)
    print('total file: ' + str(statistics['totalfile']))
    print('total size: ' + format_size(statistics['totalfilesize']))
    print('after compress: ' + format_size(statistics['totalcompresssize']))
    print('compressed: ' + format_size(statistics['totalfilesize'] - statistics['totalcompresssize']))
    print('total ratio: ' + str(100-round(statistics['totalcompresssize']/statistics['totalfilesize']*100)) + '%')
    if len(fail_files) > 0:
        print('fails: ' + str(len(fail_files)))
        for fail in fail_files:
            print(fail)    


if __name__ == '__main__':
    main()