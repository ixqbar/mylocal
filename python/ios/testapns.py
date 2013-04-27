#!/usr/bin/python
#-*-coding:utf-8-*-

'''
http://developer.apple.com/library/mac/#documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/Chapters/LegacyFormat.html
'''

import socket
import ssl
import struct
import json
import binascii

certificate  = './hc_apns_cert_and_key_dev.pem';
device_token = binascii.unhexlify('4007cca50c4b4cde9631fdedd05029a1557381d81163f6d5b5db69fe4a22c018'.replace(' ', ''))

socket_handle = socket.socket()
connection_handle = ssl.wrap_socket(socket_handle, certfile = certificate, ssl_version=ssl.PROTOCOL_SSLv3)
connection_handle.connect(('gateway.sandbox.push.apple.com', 2195))


command = 0
token_length = len(device_token)
messages = [
    {"aps":{"alert":"Hello,Python,Ok"}}
]

payloads = []
for m in messages:
    m = json.dumps(m)
    payload_length = len(m)
    pack_format = "!BH" + str(token_length) + "sH" + str(payload_length) + "s"
    payloads.append(struct.pack(pack_format,
                                command,
                                token_length,
                                device_token,
                                payload_length,
                                m))


connection_handle.write("".join([struct.pack('%ds' % len(p), p) for p in payloads]))

'''
http://developer.apple.com/library/mac/#documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/Chapters/CommunicatingWIthAPS.html

If you send a notification that is accepted by APNs, nothing is returned.
If you send a notification that is malformed or otherwise unintelligible, APNs returns an error-response packet and closes the connection. Any notifications that you sent after the malformed notification using the same connection are discarded, and must be resent. Figure 5-2 shows the format of the error-response packet.
'''

#connection_handle.read(1024)
connection_handle.close()
socket_handle.close()