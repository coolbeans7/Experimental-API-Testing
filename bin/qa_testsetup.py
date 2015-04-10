import mechanize
import requests
import re
import json
import sys
import urlparse
import logging

class SetupMethodForTesting(object):
    def __init__(self, method=None, env=None, debug=None):
        #
        # The constructor here allows multiple methods to get added onto the 
        # back of a single specified url. Eventually this url will be set
        # from the command line. It also allows you to specify multiple
        # environments.
        #
        self.debug = debug #info, verbose
        if debug == 'info':
            self.logger = logging.getLogger("").setLevel(logging.INFO)

        self.env = env #dev, prod
        
        if env == 'dev':
            self.endpoint = 'http://test15.plaxo.com/family/'
            logging.info('Using dev: %s' % self.endpoint)

        if env == 'prod':
            self.endpoint = 'http://familyapp.comcast.net/family/'
            logging.info('Using prod: %s' % self.endpoint)

        if env == None:
            self.endpoint = 'http://test15.plaxo.com/family/'
            logging.info('Using dev: %s' % self.endpoint)

        self.method = method
        
        # Note with a add'l option enabled
        # x-csv-dummy-user: account uuid 
        # will pass as login credentials

        if method != None:
            self.url = self.endpoint + method
        else:
            self.url = self.endpoint

    def getAccountInfo(self, _account):
        #
        # Primary accounts:mcdv_5624_uid_05, mcdv_5624_uid_06, mcdv_5624_uid_07
        # as either the admin or the child.
        # 

        if _account == 'prod':
            username = 'prod'
            password = 'Tester123'
        
        if _account == 'dev':
            username = 'dev'
            password = 'Tester123'

        if _account == 'badaccount':
            username = 'badaccount'
            password = 'badaccount'    
        
        return {'username':username,
                'password':password}

    def loginToCSVas(self, _membertype=None, _cima=None):

        #
        # If no account is specified, use the account specified for the env variable
        # Yeah baby!
        #
        if _membertype == None:
            _membertype = self.env

        #
        # TODO: abstract return ouside of IF,
        # wrap a try, except around the IF and
        # catch URLError so you can raise a 
        # "CIMA is down" error
        #

        #
        # Use mechanize to act as a browser to login an account to CIMA
        #
        br = mechanize.Browser()
        br.set_handle_robots(False)

        try:
            if self.env == 'prod':
                logging.info('Using CIMA PROD')
                response = br.open("https://login.comcast.net/oauth/authorize?scope=sig.subscriber.full_profile&state=android&redirect_uri=https%3A%2F%2Ffamilyapp.comcast.net%2Foauthfinal&response_type=code&client_id=family-connect-app")

                if 'token' not in response.read():
                    br.select_form(name="signin")
                    br.form["user"]=self.getAccountInfo(_membertype)['username']
                    br.form['passwd']=self.getAccountInfo(_membertype)['password']
                    response = br.submit()

                response = json.loads(response.read())

                if 'token' not in str(response):
                    raise Exception(response)

                return {
                        'text': response, 
                        'status': 200,
                        }

            elif self.env == 'dev':
                logging.info('Using middleware CIMA QA')
                response = br.open("https://login-qa4.comcast.net/oauth/authorize?scope=sig.subscriber.full_profile&state=android&redirect_uri=https%3A%2F%2Ftest.familyapp.comcast.net%2Foauthfinal&response_type=code&client_id=family-connect-app")

                if 'token' not in response.read():
                    br.select_form(name="signin")
                    br.form["user"]=self.getAccountInfo(_membertype)['username']
                    br.form['passwd']=self.getAccountInfo(_membertype)['password']
                    response = br.submit()

                response = json.loads(response.read())

                if 'token' not in str(response):
                    raise Exception(response)

                return {
                        'text': response, 
                        'status': 200,
                        }

            elif _cima == 'backend':
                #
                # What should I do here?
                # I could use /auth so that I could get
                # a 500 response and trap that as a CIMA
                # test for up/down? Sometimes a 500 using
                # requests doens't return at all but fails
                # with a timeout
                # maybe turn this into a failsafe?
                pass

            elif self.dev == 'oldschool':
                logging.info('Using Old School, Complicated CIMA QA')
                br.open("https://login-qa4.comcast.net/oauth/authorize?client_id=sig_test&response_type=token&redirect_uri=https://xdn-qa4.xfinity.com/sig/v1/$metadata&scope=sig.subscriber.full_profile")
                #br.open("https://login.comcast.net/oauth/authorize?client_id=sig_test&response_type=token&redirect_uri=https://xdn.xfinity.com/sig/v1/$metadata&scope=sig.subscriber.full_profile")
                
                br.select_form(name="signin")
                br.form["user"]=self.getAccountInfo(_membertype)['username']
                br.form['passwd']=self.getAccountInfo(_membertype)['password']

                # Print out the selected form on the page
                #print br.form

                response1 = br.submit()

                # After submitting the username print out the html webpage in response
                # print 'CIMA responsed'
                # print response1.read()

                #
                # If the account as not "allowed" the app permissions before, go
                # ahead and accept them
                #

                htmlOfPage = response1.read()

                if "THIS APP REQUESTS PERMISSION" in htmlOfPage:
                    formcount=0
                    for frm in br.forms():  
                        if str(frm.attrs["id"])=="confirmationForm":
                            break
                        formcount=formcount+1
                    br.select_form(nr=formcount)
                    response1 = br.submit()

                #try and use regex to match and parse like in ruby
                url = response1.geturl()
                s = response1.geturl().find('access_token=')
                _dictionary = urlparse.parse_qs(url[s:])

                try:
                    cima_access_token = _dictionary['access_token'][0]
                    #print cima_access_token
                except:
                    raise KeyError('Getting a token from CIMA did not succeed')

                #
                # Use that cima token to auth with test15
                #

                payload = {
                    'cima_access_token': cima_access_token,
                    'cima_refresh_token': 'whatever',
                    "device_info": '''{"app-id":"fc",
                                    "os-type":"ios",
                                    "device_id":"myDeviceID1"}'''
                }

                url = '%s/%s' % (self.endpoint, 'oauth')
                response = requests.post(url=url, data=payload)

                if response.status_code != 200:
                    raise Exception (response.text)

                return {
                        'text': response.json(), 
                        'status': response.status_code,
                        }
        except:
            print 'CIMA or SIG is down'


    def updateTestuff(self, _testChoice, _status):
        if self.env == 'dev':
            URL = 'http://sdev61.plaxo.com:8080'
            TESTUFF = '/testuff'
            EMAIL = '/email'

            logging.info("Testuff: " + _testChoice)

            testDict = {'AddFamily':'15a02e068632f0121f14ca78f06f8939',
                        'LoginToProd':'1eba5b3a1b5fcdbc2e88b716c710daf4',
                        'GetFamily':'b73c9acb13dac5649780e546e3863dd7',
                        'CreateAndSendInvitations':'20ed44ecaa9bb7b262a40f7949340fa8',
                        'GetAllInvitations':'b2154c9742a9ad07834fe395ecdeda4a',
                        'GetInvitationByToken':'1f6d302109c4b76577d570fc939dd0ce',
                        'Auth':'a2e60c36ff52351d6eff20a889f2118a',
                        'RefreshAuth':'cbfcf58fb3bb58f9b9c0e9e8258060e3',
                        'DeleteToken':'9c71ea530052cedf0d08e6e98e5c02af',
                        'GetMembers':'2169ccebdd51419fa25289e8892f05c9',
                        'GetAllFamilySettings':'dd80afd0c6aa3a74bb07e975ea175ccf',
                        'FlipSwitchesOnAllFamilySettings':'b67d2876646c9a05264b406b28949701',
                        'ReturnFamilySettingsToDefaultByDelete':'5a1b4bfcbf79eadcbc3371873dcde304',
                        'GetSpecificFamilySetting':'a7140565d4382f8cc2ae46f69b248f77',
                        'GetAllUserSettings':'e216fae8624dd411a5ec0bbfcf986800',
                        'GetSpecificUserSetting':'b9f09404cbc2e973fdaaf303001e55fa',
                        'FlipSwitchesOnAllUserSettings':'6a3c93084603943dd4ddea5482f76b8c',
                        'ReturnUserSettingsToDefaultByDelete':'8179cceb60ec0b2fb95b88d10636c2aa',
                        'SetForChildByParent':'df9d0b3cce2833a04f6d6dc06fd430cb',
                        'DeleteValueForChildByParent':'f1d6a56a72c645d65aca6d6a74f32418'}

            _id = testDict[_testChoice]
            status = _status
            username = ''
            password = ''
            service = '6'

            data = {
                'test_id':_id,
                'status':status,
                'username':username,
                'password':password,
                'service':service,
            }

            curURL = '%s%s' % (URL, TESTUFF)
            response = requests.post(curURL, data)
            logging.info(response.text)                

    def GetCurrentOrReturnNewFamily(self, _membertype=None, _token=None):
        if _membertype == None:
            _membertype = self.env        

        #
        # Check if a family exists first, if not: create family!
        #

        if _token:
            headers = {'x-csv-token': _token}
            print 'Getting family with token...'
        else:
            headers = {'x-csv-token': str(self.loginToCSVas(_membertype)['text']['access-token'])}

        response = requests.get(url=self.endpoint+'families', headers=headers)

        if response.status_code == 200:
            familyList = json.loads(response.text)["families"]
            for family in familyList:
                print '\n' + 'Family Found: ' + family["id"]
                return family["id"]
                break
            
            if len(familyList) == 0:
                #
                # No family found, add a familky
                # http://ci.plaxo.com:8080/view/csv/job/csv-documentation/doxygen/families.html#post_families
                #

                response = requests.post(url=self.endpoint+'families', headers=headers)

                #
                # Analyze the response
                #

                if response.status_code == 200:
                    print 'Family Created:'
                    print json.dumps(response.json(), sort_keys=True, indent=4, separators=(',', ': '))
                    return response.json()["family"]["id"]
                else:
                    raise Exception('''
                AddFamily failed:
                Url attempted: %(url)s
                Headers: %(headers)s
                Response: %(response)s
                ''' % { 'url' : self.endpoint + 'families',
                        'headers' : headers,
                        'response' : response.text
                        } )
        else:
            print response.text
