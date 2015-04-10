# -*- coding: utf-8 -*-
import qa_testsetup
import requests
import json
import unittest
import inspect # for method name reflection

class MembersAPI(object):
    
    def __init__(self):
        self.testThis = qa_testsetup.SetupMethodForTesting('families', env='dev')

        self.headers = {'x-csv-token': str(self.testThis.loginToCSVas()['text']['access-token'])}

        self._familyID = self.testThis.GetCurrentOrReturnNewFamily()

    def GetMembers(self, testParam=200):

        url = '%s/%s/members' % (self.testThis.url, self._familyID)

        response = requests.get(url=url, headers=self.headers)

        if response.status_code != 200:
            print url
            raise Exception('Get Member Failed:' + response.text)
        elif response.status_code == 200:
            self.testThis.updateTestuff(inspect.stack()[0][3], 'passed')
        else:
            self.testThis.updateTestuff(inspect.stack()[0][3], 'failed')            

        return True

    def DeleteMember(self, testParam=200, _familymember=None):

        if not self._familyID or not _familymember:
            raise Exception('Missing required parameters')

        url = '%s/%s/members/%s' % (self.testThis.url, self._familyID, _familymember)

        headers = {'x-csv-token': str(self.testThis.loginToCSVas()['text']['access-token'])}
        response = requests.delete(url=url, headers=self.headers)

        if response.status_code != 200:
            print 'Debug: \n Url: %s \n Secondary ID: %s \n Delete Member Results: %s \n' % (url, _familymember, response.text)
            
        return {'text': json.loads(response.text), 'status': response.status_code} 

#The code below is for unittest only
class Test_Members(unittest.TestCase):

    #use setupClass, do it just once damnit
    @classmethod
    def setUpClass(cls):
        cls.API = MembersAPI()

    def test_GetMembersMethod(self):
        self.assertTrue(self.API.GetMembers())

    def test_DeleteMemberMethod(self):
        #assert self.testThis.DeleteMember(200, self.familyID, self.invitations.familymemberSK)["status"] == 200
        #assert self.myfamily.DeleteMyFamily(self.familyID) == True
        pass

if __name__ == '__main__':
    unittest.main()
    #New = MembersAPI()
    #print New.GetMembers()['text']
