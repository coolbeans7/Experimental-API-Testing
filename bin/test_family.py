# -*- coding: utf-8 -*-
from qa_testsetup import *
from andrews_utils import *
import requests
import json
import unittest
import time
import sys
import inspect # for method name reflection

class FamiliesAPI(object):

    def __init__(self):
        self.testThis = SetupMethodForTesting('families', env='prod')
        self.familyID = ''

    def GetFamily(self, testParam=200):
        if testParam == 200:
            headers = {'x-csv-token': str(self.testThis.loginToCSVas()["text"]["access-token"])}
            response = requests.get(url=self.testThis.url, headers=headers)

        if testParam == 405:
            headers = {'x-csv-token': 'DoesntMatter'}
            response = requests.delete(url=self.testThis.url, headers=headers)    

        if response.status_code == 200:
            familyList = json.loads(response.text)["families"]
            for family in familyList:
                self.familyID = family["id"]

        if response.status_code != 200:
            print self.testThis.url
            print response.text
            print headers

        if response.status_code == 200:
            self.testThis.updateTestuff(inspect.stack()[0][3], 'passed')
        else:
            self.testThis.updateTestuff(inspect.stack()[0][3], 'failed')

        return {'text': json.loads(response.text), 'status': response.status_code}

    def AddFamily(self, testParam=200):
        #print 'AddFamily'
        
        headers = {'x-csv-token': str(self.testThis.loginToCSVas()["text"]["access-token"])}
        family_name = 'Andrews_QA_Family'

        payload = {
            'family_name': family_name
        }

        if testParam == 405:
            response = requests.delete(url=self.testThis.url, data=payload, headers=headers)

        if testParam == 200:
            response = requests.post(url=self.testThis.url, data=payload, headers=headers)

        #if response.status_code == 500:
        #    self.GetMyFamily()
        #    print 'A family has already been added: ' + self.familyID
        #    print 'Attempting to delete family and rerun...'
        #    self.DeleteMyFamily()
        #    self.AddFamily()

        if response.status_code == 200:
            #print json.loads(response.text)
            self.familyID = json.loads(response.text)["family"]["id"]

        return {'text': json.loads(response.text), 'status': response.status_code}

    def UnicodeFamilyPOST(self):
        #test if the most common Unicode values are acceptable

        unicodeString = u"UnicodeTest: ♠♤ ♦♢ ♣♧ ♥♡ ❤ ツ ♻ ⚠"

        payload = {
            "token": str(self.testThis.loginToCSVas()["text"]["access-token"]),
            'family_name': unicodeString
        }

        response = requests.post(url=self.testThis.url, data=payload)

        print response.text      

    def DeleteMyFamily(self, _familyID=''):
        #these imports are here because they are already destroy by this time
        import time
        import requests

        if _familyID == '':
            _familyID = self.familyID

        isDeleted = True

        #print 'DeleteMyFamily'

        session = requests.Session()
        url = 'http://test15.plaxo.com/csadmin-web/login'
        payload = { 'username':'admin', 'password':'pw' }
        loginPage = session.post(url=url, data=payload)

        #print 'Login Page'
        if "You are logged in" in loginPage.content:
            #print 'Logged in to site...'
            time.sleep(1)
        else:
            isDeleted = False

        payload = { 'group_id': _familyID }
        groupPage = session.post(url='http://test15.plaxo.com/csadmin-web/groups', data=payload)

        #print 'Group Page'
        if "This group has the following members" in groupPage.content:
            #print 'Found the family...'
            time.sleep(1)
        else:
            isDeleted = False            

        deletePage = session.post(url='http://test15.plaxo.com/csadmin-web/groups/delete', data=payload)

        if "Group deleted" in deletePage.content:
            #print 'Family deleted...'
            time.sleep(1)
        else:
            isDeleted = False

        if isDeleted == False:
            print 'Manually delete family: ' + self.familyID

        return isDeleted

        #logoutPage = session.get(url='http://test15.plaxo.com/csadmin-web/logout')

        #if "username" in logoutPage.content:
        #   print 'Logged out successfully.'
        #else:
        #   print logoutPage.content
      
#The code below is for unittest only
class Test_Families(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.API = FamiliesAPI()

    def test_GetFamilyMethod(self):
        #test if get family is working correctly
        self.assertEqual(self.API.GetFamily(200)["status"], 200)
        #test wrong method
        #self.assertEqual(self.API.GetMyFamily(405)["status"], 405)
    @unittest.skip("cause add family is automatic now")        
    def test_AddFamilyMethod(self):
        # add family; !do this: verify it has been added
        self.assertEqual(self.API.GetMyFamily(200)["status"], 200)
        # !do this: if family member is child, attempt to add a family
        self.assertEqual(self.API.AddFamily(405)["status"], 405)
        # Test csv admin site to the family we just added
        self.assertTrue(self.API.DeleteMyFamily)

if __name__ == '__main__':
    unittest.main()
    #New = FamiliesAPI()
    #New.AddFamily()
    #New.GetMyFamily()
    #print New.familyID
    #if New.familyID != '':
    #x    New.DeleteMyFamily()
