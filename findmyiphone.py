import sys
import getpass
import json
import re
import urllib
import datetime

import httplib2


    

class FindMyIPhone:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.http = httplib2.Http()
    def auth(self):
        debug(self.username)
        debug(self.password)
        auth_response, auth_content = self.http.request('https://auth.me.com/authenticate', 
            'POST', 
            body=urllib.urlencode({
                'service': 'mail', ###### should i change it to find my iphone?
                'ssoNamespace': 'appleid', 
                'returnURL': 'https://me.com/find', 
                #'lang':'en', 
                'anchor': 'findmyiphone', 
                'formID': 'loginForm', 
                'username': self.username, 
                'password': self.password}
            ), 
            headers={
                'Content-Type': 'application/x-www-form-urlencoded', 
                'Referer':'https://auth.me.com/authenticate?service=findmyiphone'
            }
        )
        debug(auth_response)
        debug(auth_content)
        if 'set-cookie' not in auth_response:
            print >> sys.stderr, 'Incorrect member name or password.'
            sys.exit(1)
        auth_cookie = auth_response['set-cookie']
        self.auth_cookie = auth_cookie
    def get(self):
        init_response, init_content = self.http.request('https://p03-fmipweb.me.com/fmipservice/client/initClient', 
            'POST', 
            body='{"clientContext":{"appName":"MobileMe Find (Web)","appVersion":"1.0"}}', 
            headers={
                'Cookie': self.auth_cookie, 
                'X-Mobileme-Version': '1.0', 
                'X-Requested-With': 'XMLHttpRequest', 
                'Content-Type': 'application/json; charset=UTF-8',
                'Keep-Alive': '115'
            }
        )
        debug(init_response)
        debug(init_content)
        if 'set-cookie' not in init_response:
            print >> sys.stderr, 'Incorrect member name or password.'
            sys.exit(1)
        init_cookie = init_response['set-cookie']
        self.cookie = init_cookie
        if json.loads(init_content)['statusCode'] == 0:
            print >> sys.stderr, 'Find My iPhone is unavailable.'
            sys.exit(1)
        lon = json.loads(init_content)['content'][0]['location']['longitude']
        lat = json.loads(init_content)['content'][0]['location']['latitude']
        self.lat = lat
        self.lon = lon
        debug(str(lon)+", "+str(lat))
        timestamp = json.loads(init_content)['content'][0]['location']['timeStamp']
        self.timestamp = timestamp
        debug(timestamp)
        devicemodule = json.loads(init_content)['content'][0]['deviceModel'].encode('utf-8')
        devicename = json.loads(init_content)['content'][0]['name'].encode('utf-8')
        self.devicename = devicename
        self.devicemodule = devicemodule
        debug(devicemodule)
        debug(devicename)
        servercontext = json.loads(init_content)['serverContext']
        self.servercontext = servercontext
        mobileid = json.loads(init_content)['serverContext']['prsId']
        self.mobileid = mobileid
        debug(mobileid)
        lsc, = re.search('isc-me\\.com=(.*?);', init_response['set-cookie']).groups()
        self.lsc = lsc
        debug(lsc)
    def refresh(self):
        #httpbody = '{"serverContext":'+json.dumps(self.servercontext)+', "clientContext":{"appName":"MobileMe Find (Web)","appVersion":"1.0"}}';
        httpbody = '{"clientContext":{"appName":"MobileMe Find (Web)","appVersion":"1.0"}}'
        response, content = self.http.request('https://p03-fmipweb.me.com/fmipservice/client/refreshClient', 
            'POST', 
            body=httpbody,
            headers={
                'Cookie': self.cookie, 
                'X-Requested-With': 'XMLHttpRequest', 
                'Content-Type': 'application/json; charset=UTF-8',
                'X-Mobileme-Isc': self.lsc, 
                'X-SproutCore-Version': '1.0', 
                'X-Mobileme-User': json.dumps(self.mobileid), 
                'Connection': 'keep-alive',
                'Referer': 'https://p03-fmipweb.me.com/find/resources/frame.html',
                'Keep-Alive': '115'
            }
        )
        debug(response)
        debug(content)
        
        
    
def cmd():
    if len(sys.argv) == 1:
        username = raw_input('Username: ')
        password = getpass.getpass()
    elif len(sys.argv) == 2:
        username = sys.argv[1]
        password = getpass.getpass()
    elif len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
        return username, password
    else:
        print >> sys.stderr, 'Usage: findmyiphone.py [username] [password]'
        sys.exit(1)


isdebug = False
def debug(text):
    if isdebug == True:
        print "==DEBUG==:"+str(text)    
    


if __name__ == "__main__":
    username, password = cmd()
    fmi = FindMyIPhone(username, password)
    print "lat, lng, timestamp, device model, devic name"
    while True:
        fmi.auth()
        fmi.get()
        print ""+str(fmi.lat)+", "+str(fmi.lon)+", "+str(fmi.timestamp)+", "+fmi.devicemodule+", "+fmi.devicename
    #fmi.refresh()
    