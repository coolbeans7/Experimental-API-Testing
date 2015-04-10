from qa_testsetup import SetupMethodForTesting
from fake_email_generator import *
import requests, unittest, random
import json, time, sys
import urlparse, mechanize, re

class InvitationAPI(object):
    
    def __init__(self):
        self.testThis = SetupMethodForTesting('invitations', env='dev')

        self.familyID = self.testThis.GetCurrentOrReturnNewFamily()
        
        self.invitations = None
        self.invitationToken = None
        self.familymemberSK = None

        self.CreateSendInvitations()

    def CreateSendInvitations(self, testParam=200):

        if testParam == 200:
            headers = {'x-csv-token': self.testThis.loginToCSVas()['text']['access-token']}

        if testParam == 404:
            headers = {'x-csv-token': 'badToken'}

        payload = {
            "family-id" : self.familyID,    
            "invitees" : [
                {
                    "name" : {
                        "first":'MyKid',
                        "last":'Syd'
                    },
                    "email": fake_addresses()
                }
            ],
            "children" : [
                {
                   "name" : {
                        "first": "NoPhoneBetsy",
                        "last": "Brown"
                   }
                },
            ]
        }

        response = requests.post(url=self.testThis.url, 
                                data=json.dumps(payload), 
                                headers=headers)

        if 'badly formed hexadecimal' in response.text:
            raise Exception('''
                Bad Hex in CreateSendInvitations
                Transaction id: %(id)s
                ''' % {'id' : json.loads(response.text)["response"]["id"]} )

        if response.status_code != 200:
            raise Exception('''
                CreateSendInvitations failed:
                Url attempted: %(url)s
                Headers: %(headers)s
                Response Code: %(responseCode)s
                Response Text: %(responseText)s
                ''' % { 'url' : self.testThis.url + 'families',
                    'headers' : headers,
                    'responseCode' : str(response.status_code),
                    'responseText' : response.text
                    } )
        else: #200
            pythonDict = json.loads(response.text)
            self.invitations = pythonDict
            for invitation in self.invitations["invitations"]:
                self.invitationToken = invitation['token']
                #print 'invitation token: ' + invitation['token']
            
        return True

    def GetAllInvitations(self, testParam=200):

        if testParam == 200:
            method = '/families/' + self.familyID + '/invitations'
            url = self.testThis.endpoint + method
            response = requests.get(url=url)
        if testParam == 400:
            method = '/families/badGroupID/invitations'
            url = self.testThis.endpoint + method
            response = requests.get(url=url)

        if 'badly formed hexadecimal' in response.text:
            raise Exception('''
                Bad Hex in GetAllInvitations
                Transaction id: %(id)s
                ''' % {'id' : json.loads(response.text)["response"]["id"]} )

        if response.status_code != 200:
            raise Exception('''
                GetAllInvitations failed:
                Url attempted: %(url)s
                Headers: %(headers)s
                Response Code: %(responseCode)s
                Response Text: %(responseText)s
                ''' % { 'url' : url,
                    'headers' : headers,
                    'responseCode' : str(response.status_code),
                    'responseText' : response.text
                    } )
        
        return True

    def GetInvitationByToken(self, testParam=200):

        if testParam == 200:
            url = self.testThis.url + '/' + self.invitationToken

        response = requests.get(url=url)
        pythonDict = json.loads(response.text)

        if 'badly formed hexadecimal' in response.text:
            raise Exception('''
                Bad Hex in GetAllInvitations
                Transaction id: %(id)s
                ''' % {'id' : json.loads(response.text)["response"]["id"]} )

        if response.status_code != 200:
            raise Exception('''
                GetAllInvitations failed:
                Url attempted: %(url)s
                Response Code: %(responseCode)s
                Response Text: %(responseText)s
                ''' % { 'url' : url,
                    'responseCode' : str(response.status_code),
                    'responseText' : response.text
                    } )
        
        print response.text

        return True

    def AcceptInvitation(self, testParam=200):
        pass
    # this method can't be used because I would need to access SIG
    # in order to get the subscriber-guid
    # so it was replaced with the method below

    def AcceptViaWebFlow(self):

        #
        # Get auth data
        #

        headers = {'x-csv-token': self.testThis.loginToCSVas()['text']['access-token']}

        #
        # By now the constuctor has:
        # 1. Found the existing family or created a new one
        # 2. Created and sent invitatinos
        #

        #
        # Now attempt to accept that invitation
        # 

        url = ('http://test.familyapp.comcast.net/xf/api/invite/%s' % self.invitationToken)

        print url

        sys.exit()

        br = mechanize.Browser()
        br.set_handle_robots(False)
        response = br.open(url)

        # form id = "mainForm"
        try:
            didTheRightPageLoad = False
            formcount=0
            for frm in br.forms():  
                if str(frm.attrs["id"])=="mainForm":
                    didTheRightPageLoad = True
                    break
                formcount=formcount+1
            br.select_form(nr=formcount)
        except:
            raise Exception('''
                Something failed or changed in the front end secondary user creation flow.
                Attempted: %s
                ''' % url )

        if didTheRightPageLoad == False:
            raise Exception('The accept invitation and create account page did not load correctly')

        br.form['firstName'] = gen_name(randint(7, 20))
        br.form['lastName'] = gen_name(randint(7, 20))
        br.form['userName'] = 'FC_Tester_%i' % random.randint(1,20)
        br.form['password'] = 'Tester123'
        br.form['passwordRetype'] = 'Tester123'

        # submit the form
        response1 = br.submit()

        if "Your account has been created." in response1.read():
            return True
        else:
            raise Exception('Something went wrong in the front-end invitation flow')

#The code below is for unittest only
class Test_Invitations(unittest.TestCase):
    #use setupClass, do it just once damnit
    @classmethod
    def setUpClass(cls):
        cls.API = InvitationAPI()

    # !Create new tests to verify error code
    def test_CreateSendInvitationsMethod(self):
        self.assertTrue(self.API.CreateSendInvitations())
        #Unable to write any tests other than 200 as status codes are all wrong
    def test_GetAllInvitations(self):
        self.assertTrue(self.API.GetAllInvitations())
        #unable to test 400 as when I send 400 I get 500
    def test_GetInvitationByToken(self):
        self.assertTrue(self.API.GetInvitationByToken())
        #assert self.testThis.GetInvitationByToken(404) == 404
    def CreateAndSendInvitations_ThenAcceptViaWebFlow(self, _sendAsAccount):
        self.assertTrue(self.API.AcceptViaWebFlow())
        pass


if __name__ == '__main__':
    unittest.main()
