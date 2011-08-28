#!/usr/bin/python
Token = None
ClientId='1141f78aa9854d91be6afbdcb338e76f'

import os
appdir_ = os.path.join(os.environ['HOME'], '.fuse-yandex-fotki')
tokenfile_ = os.path.join(appdir_, 'token') 

try:
    Token = open(tokenfile_, 'r').read() 
except:
    import browser
    print 'your clietn not configured properly'
    print 'now browser window will be appeare, please authorise photo client to access on your album'
    Token = browser.getToken(ClientId)
    if not os.path.isfile(appdir_):
        os.mkdir(appdir_, 0700)
    open(tokenfile_, 'w').write(Token)
