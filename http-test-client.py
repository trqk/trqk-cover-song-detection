# http-server.py: - minimal shell REPL to respond to HTTP commands
# -*- coding: utf-8 -*-

"""
    http-server.py: - shell client to respond to HTTP commands   
        Stephen Travis Pope - stephen@FASTLabInc.com - 2002
        
    //    Copyright (C) 2020 Stephen T. Pope & Trqk. All rights reserved.
    //    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE.
    //    The copyright notice above does not evidence any actual or intended publication
    //    of such source code.

To Run:
    py http-server.py
OR
    py http-server.py file_list.txt

If called with no arg, run REPL, else read a list of files and run them 1-by-1

Type command "exit" (or empty line) to exit program

Reads HTTP command like,

POST http://127.0.0.1:8000/songs/csd url=http://fastlabinc.com/SndsLike/WaitingInVain.wav
POST /songs/csd/ url:http://fastlabinc.com/SndsLike/WaitingInVain.wav
POST http://204.236.206.86:8000/csd url=http://fastlabinc.com/SndsLike/WaitingInVain.wav

POST http://204.236.206.86:8000/csd url=http://fastlabinc.com/SndsLike/WaitingInVain.wav  reference=http://fastlabinc.com/SndsLike/WaitingInVain.wav

As an alternative, you can use https://www.codepunker.com/tools/http-requests to create GET/POST requests

"""

import http.client, sys, json
                                    # http server ip & port
http_server = '127.0.0.1'           # test locally
server_port = 8000

# http_server = '204.236.206.86'     # or test in the cloud
# server_port = 80

def read_file(conn, fn):                  # read a file of S3 file names
    print(('Load file list', fn))
    print('Title,Artist,Tempo,Exp. Tempo,Key,Exp. Key,Genre,Exp. Genre,Mood,Instruments,Style')
    with open(fn, 'r') as inF:
        for lin in inF:
            if len(lin) < 8 or lin[0] == '#':      # skip empty lines and comments
                continue
            lin = lin.replace('\n', '')             # drop the CR
            pos = lin.find('\t')
            toks = ['', '', '']
            if pos < 1:
                pos = len(lin) - 1
            else:
                toks = lin[pos + 1 : ].split('\t')
            nam = lin[ : pos]                       # break line at tab
            nam2 = nam.replace(' ', '%20')
#            print nam2, '--', toks
            bas = 'http://204.236.206.86:80/analysis?filename='
            s3_home = 'https://trqk-desktop-dev.s3.amazonaws.com/public/0aadaddb-8208-442e-a1f3-89c7da568dd1/trqks/'
            fURL = bas + s3_home + nam2
#            print fURL
            conn.request('GET', fURL)
            handle_response(nam, toks[0], toks[1], toks[2])
        inF.close()

def get_str(dct, key):
    if key in dct and dct[key] is not None:
        return dct[key]
    else:
        return 'Undefined'


def handle_response(conn, nam, tpo = '', ky = '', gen = ''):          # print server response and data
    "handle_response"
    try:
        rsp = conn.getresponse()    # get response from server
        print((rsp.status, rsp.reason))
        data_received = rsp.read()
#    print(data_received)
        dct = json.loads(data_received)
        if nam.endswith('SYSTEM_TEST'):
            print(('Test results:', dct))
            return
        err = get_str(dct, "statusOK")              # check return status
        if not err:
    #        print 'Error:', get_str(dct, "errorMessage"), nam, data_received
            print(('%s,ERROR,,,,,%s' % (nam.encode('ISO-8859-1', 'ignore'), get_str(dct, "errorMessage"))))
        else:
            print(('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (get_str(dct, "name").replace(',', '_'), 
                                              get_str(dct, "artist").replace(',', '_'), 
                                              get_str(dct, "tempo"),  tpo,
                                              get_str(dct, "key"), ky,
                                              get_str(dct, "genre").replace(',', '_'), gen.replace(',', '_'),
                                              get_str(dct, "mood2").replace(',', '_'),
                                              get_str(dct, "instruments").replace(',', '_'),
                                              get_str(dct, "style").replace(',', '_'))))
    except Exception as inst:
        print('Client handle_response error')
        print(inst)


def server_loop(conn):              # REPL
    "Read-eval-print loop"
    while 1:                    # the loop
        inp = input('HTTP command: ')
#        print('Inp:', inp)
        if len(inp) > 0:
            cmd = inp.split()
        else:
            print('Empty input?')
            break
        if cmd is None: 
            break
        if cmd[0] == 'exit':    # type exit or blank line to end
            break
        print('Cmd:', cmd)
        if len(cmd) == 2:       #request command to server
            # hdr = { cmd[1] }
            # conn.request(cmd[0], headers=hdr)
            conn.request(cmd[0], cmd[1])
            handle_response(conn, cmd[1])
        else:
            conn.request(cmd[0], cmd[1], cmd[2])
            handle_response(conn, cmd[2])
    conn.close()                # when done, close connection
    print('Client exiting')


#### Main -------------------

def main_fcn():
    conn = http.client.HTTPConnection(http_server, server_port)
    if (len(sys.argv)) == 1:                    # if called with no arg, run REPL
        server_loop(conn)
    else:                                       # else load file list
        read_file(conn, sys.argv[1])

if __name__ == '__main__':
    main_fcn()
