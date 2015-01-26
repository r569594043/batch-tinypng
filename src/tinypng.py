# -*- coding: utf-8 -*-

import urllib.request
import json
import sys
import os
import socket
from optparse import OptionParser
import sys

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
    if opener:
        resp = opener.open(req)
    else:
        resp = urllib.request.urlopen(req)
    return json.loads(resp.read().decode('utf-8'))


def format_size(size):
    if size < 1024:
        return str(size) + 'B'
    elif size < (1024 * 1024):
        return str(round(size/1024, 1)) + 'KB'
    else:
        return str(round(size/1024/1024, 1)) + 'MB'

def retrieve(url, path):
    resp = opener.open(url)
    f = open(path, "wb")
    f.write(resp.read())
    f.close()

def save_file(url, path):
    if opener:
        retrieve(url, path)
    else:
        urllib.request.urlretrieve(url, path)

def tinydir(srcpath, descpath):
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
def tinyfile(srcfile, descfile):
    filename = os.path.basename(srcfile)
    result = tinypng(srcfile)
    if 'input' in result and 'output' in result:
        save_file(result['output']['url'], descfile)
        inputsize = result['input']['size']
        outputsize = result['output']['size']
        ratio = result['output']['ratio']
        print('{0}\t{1}\t{2}\t-{3}%'.format(filename, format_size(inputsize), format_size(outputsize), 100 - round(ratio * 100)))

def main():
    usage = "usage: %prog [options] INPUT OUTPUT"

    parser = OptionParser(usage)
    parser.add_option("-p", "--proxy", dest="proxy", metavar="PROXY", default=None,
                      help="proxy")
    (options, args) = parser.parse_args()
    input = None
    output = None
    proxy = None

    if not input and len(args) > 0:
        input = args[0]
        if not output and len(args) > 1:
            output = args[1]

    if options.proxy:
        proxy = options.proxy

    if not input or not output:
        print("Error: input and output can't be empty!")
        parser.print_help()
        sys.exit()
    global opener
    opener = None
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({'https': proxy})
        opener = urllib.request.build_opener(urllib.request.HTTPHandler, proxy_handler)
        
    socket.setdefaulttimeout(60)
    
    if os.path.exists(input):
        if os.path.isdir(input):
            tinydir(input, output)
        elif os.path.isfile(input):
            tinyfile(input, output)
    else:
        print('Source file or folder does not exists!')


if __name__ == '__main__':
    main()