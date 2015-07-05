import base64
import ConfigParser
from Crypto.Cipher import DES3
import json
from os.path import expanduser

home = expanduser("~")

class EqualsSpaceRemover:
    output_file = None
    def __init__( self, new_output_file ):
        self.output_file = new_output_file

    def write( self, what ):
        self.output_file.write( what.replace( " = ", "=" ) )

remmina_pref = ConfigParser.RawConfigParser(allow_no_value=True)
with open (home + '/.remmina/remmina.pref') as f:
    remmina_pref.readfp(f)
secret = remmina_pref.get('remmina_pref', 'secret')
secret = base64.decodestring(secret)

def encrypt_DES3(msg):
    # pending msg to be a multiple of 8 in length
    toAdd = 8 - len(msg) % 8
    msg += '\0'*toAdd
    encrypt_msg = base64.encodestring(DES3.new(secret[:24], DES3.MODE_CBC, secret[24:]).encrypt(msg))
    # remove extra trailing newline
    return encrypt_msg[:-1]

config = ConfigParser.RawConfigParser(allow_no_value=True)

with open('serverlist.json') as f:    
    serverlist = json.load(f)['serverlist']

for i in serverlist:
    with open ('remmina.temp') as f:
        config.readfp(f)
    with open (home + '/.remmina/' + i['name'] + '.remmina', 'w') as output:
        config.set('remmina', 'name', i['name'])
        config.set('remmina', 'group', i['group'])
        config.set('remmina', 'server', i['server'])
        config.set('remmina', 'username', i['username'])
        config.set('remmina', 'password', encrypt_DES3(i['password']))
        config.write(EqualsSpaceRemover(output))
