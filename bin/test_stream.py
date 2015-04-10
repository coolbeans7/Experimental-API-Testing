from qa_testsetup import *
import requests
import json
import sys, os
import unittest
import random
from multiprocessing import Process, Lock
import time
from datetime import datetime

class print_out():

    def __init__ (self, _user, _threadname, l):
        self.l = l
        self.teststream(_user, _threadname)

    #
    # Recursivly compare
    #
    def working(self, msg, streamMsg):
      for k, v in msg.iteritems():
        if isinstance(v, dict):
          self.working(v, streamMsg)
        else:
          #print str(json.dumps({k:v})).replace('{', '').replace('}', '')
          stringWithoutBraces = str(json.dumps({k:v})).replace('{', '').replace('}', '')
          if stringWithoutBraces in str(json.dumps(streamMsg)):
            # print 'found ' + stringWithoutBraces #+ '\n' + json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': '))
            pass
        # exceptions to the rule
          elif k == 'caption':
            print 'skipped caption'
          else:
            print 'Message content {0} not found'.format(stringWithoutBraces)
            print 'Here is the msg id: %s' % msg['id']
            raise Exception('Unable to find message content')   

    def notWorking(self, msg, streamMsg):
        for k, v in msg.iteritems():
            if isinstance(v, dict):
                self.notWorking(v, streamMsg)
        else:
            #print str(json.dumps({k:v})).replace('{', '').replace('}', '')
            stringWithoutBraces = str(json.dumps({k:v})).replace('{', '').replace('}', '')
            if stringWithoutBraces in str(json.dumps(streamMsg)):
                #print 'found ' + stringWithoutBraces #+ '\n' + json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': '))
                pass
            else:
                print 'missing ' + stringWithoutBraces

    def teststream(self, _user, _threadname):
        #create objects and login user
        testThis = SetupMethodForTesting('streams/', env='dev')
        #invitations will add a family to the user, create and send an invitation,
        #and then accept that invitation to add a user to the family.

        #send message
        _userdata = testThis.loginToCSVas(_user)['text']

        headers = {'x-csv-token': _userdata['access-token']}

        #print data
        #print url
        i = 0
        audioPayloadTotal = 0
        while True:
            url = testThis.url+testThis.GetCurrentOrReturnNewFamily(_user, _userdata['access-token'])+'/messages'

            # GET optional params
            #newerThan=<message_uuid>
            #olderThan=<message_uuid>

            #
            # Create text payload
            #

            textPayload = {
                'type':'text',
                'data.sender-id': _userdata['account-uuid'],
                'data.text':'''U.S. intelligence agents have been hacking computer networks
                            around the world for years, apparently targeting fat data
                            pipes that push immense amounts of data around the Internet,
                            NSA leaker Edward Snowden t'''
            }

            #
            # Create audio payload
            #

            randbytes = random.randint(1,480)
            audioPayloadTotal += randbytes
            audioFile = {'data.audio': os.urandom(randbytes)}

            if audioPayloadTotal > 1024:
                print 'No Errors Caught in: %s bytes of data' % audioPayloadTotal
                sys.exit(0)

            audioPayload = {
                'type':'audio',
                'data.sender-id': _userdata['account-uuid'],
                'data.object-props.format':'wav',
                'data.object-props.duration':str(random.randint(1,60)),
                'data.object-props.bitrate':320,
                'data.object-props.transcript':'Fake transcript goes here'
            }

            #
            # Create image payload
            #

            imageFile = {'data.image': open('cat.jpg', 'rb')}

            imagePayload = {
                'type':'image',
                'data.sender-id': _userdata['account-uuid'],
                'data.object-props.format':'jpg',
                'data.object-props.caption':'Test caption goes here'
            }

            #
            # Post created data to the stream
            # use locks to make sure the writes
            # to the console don't hit a race
            # condition

            # Create a list to store the
            # message id's for use later on
            messages = []

            #
            # Attempt to post audio
            #
            self.l.acquire()
            print 'attempting to post audio to stream...'
            self.l.release()
            response = requests.post(url=url, headers=headers, data=audioPayload, files=audioFile)

            if response.status_code != 200:
                raise Exception (response.text)
            else:
                print response.text
                sys.exit()
                messages.append(json.loads(response.text)["message"])

            #
            # Attempt to post text
            #
            self.l.acquire()
            print 'attempting to post text to stream...'
            self.l.release()
            response = requests.post(url=url, headers=headers, data=textPayload)

            if response.status_code != 200:
                raise Exception (response.text)
            else:
                messages.append(json.loads(response.text)["message"])

            #
            # Attempt to post image
            #
            self.l.acquire()
            print 'attempting to post image to stream...'
            self.l.release()
            response = requests.post(url=url, headers=headers, data=imagePayload, files=imageFile)

            if response.status_code != 200:
                raise Exception (response.text)
            else:
                messages.append(json.loads(response.text)["message"])
                #   print json.dumps(response.text, sort_keys=True, indent=4, separators=(',', ': '))
            #print len(messages)

            #
            # Attempt to GET stream
            #
            self.l.acquire()
            print 'attempting to get stream...'  
            self.l.release()
            response = requests.get(url=url, headers=headers)

            if response.status_code != 200:
                raise Exception (response.text)
            else:
                stream = json.loads(response.text)

            #
            # Verify the message is in the stream
            # and verify the contents of stream
            # from posted messages
            #

            for msg in messages:
                #
                # Verify message is in the stream by id
                #                
                if str(msg["id"]) not in str(stream):
                    raise Exception ("missing " + str(msg["id"]))
                #
                # Then verify each message contents in the stream
                #
                for streamMsg in stream["messages"]:
                    if streamMsg['id'] == msg['id']:
                        #print 'matching msg snd streamMsg'
                        self.working(msg, streamMsg)

            #
            # Verify newerThan=<message_id>
            #
            timestamp = None
            for streamMsg in stream["messages"]:
                if streamMsg['id'] == messages[1]['id']:
                    timestamp = streamMsg['data']['timestamp']

            params = { 'newerThan':messages[1]['id'],
                        'resetbadgecounter':'True' }            

            response = requests.get(url=url, headers=headers, params=params)

            if response.status_code != 200:
                raise Exception (response.text)

            stream = json.loads(response.text)

            # timestamp: 2013-01-25T00:00:02Z
            msgDate = re.search( r'^[^_]+(?=T)', timestamp, re.M|re.I).group()
            msgTime = re.search( r'(?<=T)[^_]+(?=Z)', timestamp, re.M|re.I).group()
            # 2013-09-16 18:12:12 %Y-%m-%d %H:%M:%S
            timestamp = '%s %s' % (msgDate, msgTime)
            earilestDate = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

            #
            # Verify each message in the returned stream
            # subset is newerThan the message selected
            #

            for msg in stream['messages']:
                timestamp = msg['data']['timestamp']
                msgDate = re.search(r'^[^_]+(?=T)', timestamp, re.M|re.I).group()
                msgTime = re.search(r'(?<=T)[^_]+(?=Z)', timestamp, re.M|re.I).group()
                # 2013-09-16 18:12:12 %Y-%m-%d %H:%M:%S
                timestamp = '%s %s' % (msgDate, msgTime)
                date_object = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

                if date_object < earilestDate:
                    raise Exception('date check test failed: %s is not greater than %s', (str(date_object), str(earilestDate)))


            #
            # Verify olderThan=<message_id>
            #

            #
            # Attempt to GET stream
            #
            response = requests.get(url=url, headers=headers)

            if response.status_code != 200:
                raise Exception (response.text)
            else:
                stream = json.loads(response.text)

            #
            # Begin to verify
            #
            timestamp = None
            for streamMsg in stream["messages"]:
                if streamMsg['id'] == messages[0]['id']:
                    timestamp = streamMsg['data']['timestamp']

            params = { 'olderThan':messages[0]['id'],
                        'resetbadgecounter':'True' }            

            response = requests.get(url=url, headers=headers, params=params)

            if response.status_code != 200:
                raise Exception (response.text)

            stream = json.loads(response.text)

            #print response.text

            # timestamp: 2013-01-25T00:00:02Z
            msgDate = re.search(r'^[^_]+(?=T)', timestamp, re.M|re.I).group()
            msgTime = re.search(r'(?<=T)[^_]+(?=Z)', timestamp, re.M|re.I).group()
            # 2013-09-16 18:12:12 %Y-%m-%d %H:%M:%S
            timestamp = '%s %s' % (msgDate, msgTime)
            oldestDate = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

            #print oldestDate

            #
            # Verify each message in the returned stream
            # subset is olderThan the message selected
            #

            for msg in stream['messages']:
                timestamp = msg['data']['timestamp']
                msgDate = re.search( r'^[^_]+(?=T)', timestamp, re.M|re.I).group()
                msgTime = re.search( r'(?<=T)[^_]+(?=Z)', timestamp, re.M|re.I).group()
                # 2013-09-16 18:12:12 %Y-%m-%d %H:%M:%S
                timestamp = '%s %s' % (msgDate, msgTime)
                date_object = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

                if date_object > oldestDate:
                    raise Exception('date check test failed: %s is not less than %s', (str(date_object), str(earilestDate)))

            #
            # TODO: Cause system stream messages:
            # add, delete member
            # add, update, del calender
            # Verify they exist
            # Verify their contents
            #

            #
            # Get only x number of messages
            #
            randlimit = random.randint(1,9)
            
            self.l.acquire()
            print 'attempting to get %i messages from stream...' % randlimit 
            self.l.release()
            
            params = { 'limit':randlimit,
                        'resetbadgecounter':'True' }

            response = requests.get(url=url, headers=headers, params=params)

            if response.status_code != 200:
                raise Exception (response.text)
            else:
                stream = json.loads(response.text)["messages"]

            if len(stream) != randlimit:
                print 'I asked for %i and I got %i' % (randlimit, len(stream))
                raise Exception('Yo, the limit feature of the stream API is possibly broke')

            #
            # Print which loop the thread is on
            #

            print '%s loop: %i' % (_threadname, i)
            i += 1

if __name__=="__main__":

    # Create threads as follows
    # Verify post was a success
    # users = ('dev')

    lock = Lock()
    i = 0
    threadname = 'Thread-%i' % i
    Process(target=print_out, args=('dev', threadname, lock)).start()


#The code below is for unittest only
class Test_Stream(unittest.TestCase):
    #use setupClass, do it just once damnit
    @classmethod
    def setUpClass(cls):
        cls.API = Test_Stream()

    # !Create new tests to verify error code
    def test_GetStream(self):
        pass
    def test_AddToStream(self):
        pass
    def test_DeleteStream(self):
        pass
