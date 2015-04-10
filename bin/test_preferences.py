from qa_testsetup import *
import requests
import json, sys
import random
import unittest
import inspect # for reflection

class PreferencesAPI(object):
#Get all the values for the family        
#Set them all to something they are not (should be default)
#Verify they were set to whatever was chosen
#Delete all the values after setting them
#Verify they are set to defaults

#??? Get values for all user settings or user settings of specified type
#??? Get values for [all family settings] or [family settings of specified type]    
    def __init__(self):
        #
        # initial blank setup to access GetFamily method
        #
        self.qa_test = SetupMethodForTesting(env='dev')
        self.familyid = self.qa_test.GetCurrentOrReturnNewFamily()
        
        #
        # resetup method with family id (this usage indicated 
        # GetCurrentOrReturnNewFamily can be exposed outside the setup class)
        #
        self.qa_test = SetupMethodForTesting('families/%s/preferences' % self.familyid, env='dev')
        self.headers = {'x-csv-token':self.qa_test.loginToCSVas()['text']['access-token']}

        self.currentPrefs = {}
        self.newPrefs = {}
        self.pref_list = ['fc.cal-reminder', 
                            'fc.cal-update', 
                            'fc.stream-update']

        self.defaultPrefs = {"fc.cal-reminder": "Always",
                            "fc.cal-update": "On",
                            "fc.stream-update": "On",
                            "fc.tv-alert-location":"Off", 
                            "fc.tv-alert-cal":"Off"}

        self.cal_reminder_possible_values = ['Always','Own','None']  

    def GetAllFamilySettings(self):
        #
        #Get values for all family settings
        #

        response = requests.get(url=self.qa_test.url, headers=self.headers, timeout=5)

        if response.status_code == 200:
            self.currentPrefs = json.loads(response.text)["preferences"]
            #print 'GetAllFamilySettings says currentPrefs = ' + json.dumps(self.currentPrefs, sort_keys=True, indent=4, separators=(',', ': '))
            self.qa_test.updateTestuff(inspect.stack()[0][3], 'passed')
        else:
            self.qa_test.updateTestuff(inspect.stack()[0][3], 'failed')
            print 'Unsuccessful GetAllFamilySettings' + self.qa_test.url
            raise Exception()

        return True

    def FlipSwitchesOnAllFamilySettings(self):
        #
        # Setup needs for common settings
        #
        self.newPrefs.clear()
        
        # I'll eventually need a variable to trigger a method to submit a git issue
        # testPassed = True

        #
        # for each pref, flip those settings!
        #
        for pref in self.currentPrefs:            
            #
            # pref cal-reminder is special since it has 3 values
            #
            # print 'The pref being switched is: ' + pref
            # print 'From: ' + str(self.currentPrefs[pref])
            url = '%s/%s' % (self.qa_test.url, pref)

            if pref == 'fc.cal-reminder':
                i = 0
                while (self.currentPrefs[pref] == self.cal_reminder_possible_values[i]):
                    i = random.randint(0,2)
                
                payload = {'value':self.cal_reminder_possible_values[i]}
                self.newPrefs[pref] = self.cal_reminder_possible_values[i]
                # print 'To: ' + cal_reminder_possible_values[i]
            else:
                if self.currentPrefs[pref] == 'On':
                    payload = {'value':'Off'}
                if self.currentPrefs[pref] == 'Off':
                    payload = {'value':'Off'}
                
                self.newPrefs[pref] = payload["value"]
                # print 'To: ' + str(payload["value"])

            response = requests.put(url=url, headers=self.headers, timeout=5, data=payload)

            if response.status_code != 200:
                self.qa_test.updateTestuff(inspect.stack()[0][3], 'failed')
                raise Exception('''
                    Unsuccessful perf switch
                    Url: %(url)%
                    Pref attempted: %(pref)%
                    Tried to switch it from: %(switchedFrom)%
                    Tried to switch to: %(switchedTo)%
                    Response: %(response)%
                    ''' % { 'url' : url,
                            'pref' : perf,
                            'switchedFrom' : self.currentPrefs[pref],
                            'switchedTo' : payload,
                            'response' : response.text 
                            } )

        self.qa_test.updateTestuff(inspect.stack()[0][3], 'passed')
        return True

    def VerifySettingsWereFlipped(self):
        #
        # Get the current settings
        #
        self.GetAllFamilySettings()
        
        #
        # Compare them to the old settings
        #
        if set(self.currentPrefs.items()) == set(self.newPrefs.items()):
            return True
        else:
            return False

    def ReturnFamilySettingsToDefaultByDelete(self):

        for pref in self.pref_list:
            url = '%s/%s' % (self.qa_test.url, pref)
            response = requests.delete(url=url, headers=self.headers, timeout=5)

            if response.status_code != 200:
                self.qa_test.updateTestuff(inspect.stack()[0][3], 'failed')
                raise Exception('''
                    Unsuccessful attempt to return pref to default
                    Url: %(url)%
                    Pref attempted: %(pref)%
                    Response: %(response)%
                    ''' % { 'url' : url,
                            'pref' : perf,
                            'response' : response.text 
                            } )

            self.qa_test.updateTestuff(inspect.stack()[0][3], 'passed')
            return True

    def VerifySettingsAreDefault(self):
        #print  'newPrefs: ' + json.dumps(self.newPrefs, sort_keys=True, indent=4, separators=(',', ': '))
        if set(self.currentPrefs.items()) == set(self.defaultPrefs.items()):
            return True
        else:
            print 'currentPrefs: ' + str(self.currentPrefs.items())
            print 'defaultPrefs: ' + str(self.defaultPrefs.items())
            return False

    def GetSpecificFamilySetting(self):
        #
        #
        #

        for pref in self.pref_list:
            url = '%s/%s' % (self.qa_test.url, pref)
            response = requests.get(url=url, headers=self.headers, timeout=5)
            
            if response.status_code != 200:
                self.qa_test.updateTestuff(inspect.stack()[0][3], 'failed')
                raise Exception('''
                    Unsuccessful attempt to return pref to default
                    Url: %(url)%
                    Pref attempted: %(pref)%
                    Response: %(response)%
                    ''' % { 'url' : url,
                            'pref' : perf,
                            'response' : response.text 
                            } )

        self.qa_test.updateTestuff(inspect.stack()[0][3], 'passed')
        return True

    def GetAllUserSettings(self):
        #
        #
        #
        url = '%s/preferences' % self.qa_test.endpoint

        response = requests.get(url=url, headers=self.headers, timeout=5)

        if response.status_code == 200:
            self.currentPrefs = json.loads(response.text)["preferences"]
            self.qa_test.updateTestuff(inspect.stack()[0][3], 'passed')
        else:
            self.qa_test.updateTestuff(inspect.stack()[0][3], 'failed')
            raise Exception('GetAllFamilySettings failed because...%s' % response.text)

        return True

    def GetSpecificUserSetting(self, user=None):
        #
        # eventually make this take in a user
        #

        self.newPrefs.clear()

        for pref in self.pref_list:        
            url = '%s/%s' % (self.qa_test.url, pref)
            
            response = requests.get(url=url, headers=self.headers, timeout=5)
            
            if response.status_code != 200:
                self.qa_test.updateTestuff(inspect.stack()[0][3], 'failed')
                raise Exception('''
                    Unsuccessful attempt to return get user pref
                    Url: %(url)%
                    Pref attempted: %(pref)%
                    Response: %(response)%
                    ''' % { 'url' : url,
                            'pref' : perf,
                            'response' : response.text 
                            } )

        self.qa_test.updateTestuff(inspect.stack()[0][3], 'passed')
        return True

    def FlipSwitchesOnAllUserSettings(self, user=None):
        #
        # eventually make this take in a user
        #

        self.newPrefs.clear()

        for pref in self.currentPrefs:         
            #set pref cal-reminder to something other than what it is
            #print 'The pref being switched is: ' + pref
            #print 'From: ' + str(self.currentPrefs[pref])
            url = '%s/%s' % (self.qa_test.url, pref)

            if pref == 'fc.cal-reminder':
                i = 0
                while (self.currentPrefs[pref] == self.cal_reminder_possible_values[i]):
                    i = random.randint(0,2)
                
                payload = {'value':self.cal_reminder_possible_values[i]}
                self.newPrefs[pref] = self.cal_reminder_possible_values[i]
                #print 'To: ' + cal_reminder_possible_values[i]
            else:
                if self.currentPrefs[pref] == 'On':
                    payload = {'value':'Off'}
                if self.currentPrefs[pref] == 'Off':
                    payload = {'value':'Off'}
                
                self.newPrefs[pref] = payload["value"]
                #print 'To: ' + str(payload["value"])

            response = requests.put(url=url, headers=self.headers, timeout=5, data=payload)

            if response.status_code != 200:
                self.qa_test.updateTestuff(inspect.stack()[0][3], 'failed')
                raise Exception('''
                    Unsuccessful perf switch
                    Url: %(url)%
                    Pref attempted: %(pref)%
                    Tried to switch it from: %(switchedFrom)%
                    Tried to switch to: %(switchedTo)%
                    Response: %(response)%
                    ''' % { 'url' : url,
                            'pref' : perf,
                            'switchedFrom' : self.currentPrefs[pref],
                            'switchedTo' : payload,
                            'response' : response.text 
                            } )

        self.qa_test.updateTestuff(inspect.stack()[0][3], 'failed')
        return True

    def ReturnUserSettingsToDefaultByDelete(self, _user=None):
        #
        #
        #

        for pref in self.pref_list:
            url = '%s/%s' % (self.qa_test.url, pref)
            response = requests.delete(url=url, headers=self.headers, timeout=5)
            if response.status_code != 200:
                self.qa_test.updateTestuff(inspect.stack()[0][3], 'failed')
                raise Exception('''
                    Unsuccessful attempt to return pref to default
                    Url: %(url)%
                    Pref attempted: %(pref)%
                    Response: %(response)%
                    ''' % { 'url' : url,
                            'pref' : perf,
                            'response' : response.text 
                            } )

        self.qa_test.updateTestuff(inspect.stack()[0][3], 'passed')
        return True

    def SetForChildByParent(self):
        #
        #
        #

        member = qa_test.loginToCSVas('admin_family_child1')['text']['account_uuid']

        for pref in self.pref_list:
            url = 'http://test15.plaxo.com/family/families/%s/members/%s/preferences/%s' % (familyid, member, pref)

            if pref == 'fc.cal-reminder':
                i = 0
                while (self.currentPrefs[pref] == self.cal_reminder_possible_values[i]):
                    i = random.randint(0,2)
                
                payload = {'value': self.cal_reminder_possible_values[i]}
                self.newPrefs[pref] = self.cal_reminder_possible_values[i]
                #print 'To: ' + self.cal_reminder_possible_values[i]
            else:
                if self.currentPrefs[pref] == 'On':
                    payload = {'value': 'Off'}
                if self.currentPrefs[pref] == 'Off':
                    payload = {'value': 'Off'}
                
                self.newPrefs[pref] = payload["value"]
                print 'To: ' + str(payload["value"])

            response = requests.put(url=url, headers=self.headers, timeout=5, data=payload)

            if response.status_code != 200:
                self.qa_test.updateTestuff(inspect.stack()[0][3], 'failed')
                raise Exception('''
                    Unsuccessful perf switch
                    Member: %(member)%
                    Admin: %(admin)%
                    Url: %(url)%
                    Pref attempted: %(pref)%
                    Tried to switch it from: %(switchedFrom)%
                    Tried to switch to: %(switchedTo)%
                    Response: %(response)%
                    ''' % { 'member' : url,
                            'headers' : url,
                            'url' : url,
                            'pref' : perf,
                            'switchedFrom' : self.currentPrefs[pref],
                            'switchedTo' : payload,
                            'response' : response.text 
                            } )

        self.qa_test.updateTestuff(inspect.stack()[0][3], 'passed')
        return True

    def DeleteValueForChildByParent(self):
        #
        #
        #

        member = qa_test.loginToCSVas()['text']['account_uuid']

        for pref in self.pref_list:
            url = 'http://test15.plaxo.com/family/families/%s/members/%s/preferences/%s' % (familyid, member, pref)

            if pref == 'fc.cal-reminder':
                i = 0
                while (self.currentPrefs[pref] == self.cal_reminder_possible_values[i]):
                    i = random.randint(0,2)
                
                payload = {'value': self.cal_reminder_possible_values[i]}
                self.newPrefs[pref] = self.cal_reminder_possible_values[i]
            else:
                if self.currentPrefs[pref] == 'On':
                    payload = {'value': 'Off'}
                if self.currentPrefs[pref] == 'Off':
                    payload = {'value': 'Off'}

            response = requests.put(url=url, headers=self.headers, timeout=5, data=payload)

            if response.status_code != 200:
                self.qa_test.updateTestuff(inspect.stack()[0][3], 'failed')
                raise Exception('''
                    Unsuccessful perf switch
                    Member: %(member)%
                    Admin: %(admin)%
                    Url: %(url)%
                    Pref attempted: %(pref)%
                    Tried to switch it from: %(switchedFrom)%
                    Tried to switch to: %(switchedTo)%
                    Response: %(response)%
                    ''' % { 'member' : url,
                            'headers' : url,
                            'url' : url,
                            'pref' : perf,
                            'switchedFrom' : self.currentPrefs[pref],
                            'switchedTo' : payload,
                            'response' : response.text 
                            } )            

        self.qa_test.updateTestuff(inspect.stack()[0][3], 'passed')
        return True

#The code below is for unittest only
class Test_Preferences(unittest.TestCase):
    #use setupClass, do it just once damnit
    @classmethod
    def setUpClass(cls):
        cls.API = PreferencesAPI()

    # !Create new tests to verify error code
    def test_GetAll_Family_Settings(self):
        self.assertTrue(self.API.GetAllFamilySettings())
    def test_FlipSwitchesOnAll_Family_Settings(self):
        self.assertTrue(self.API.GetAllFamilySettings())
        self.assertTrue(self.API.FlipSwitchesOnAllFamilySettings())
        self.assertTrue(self.API.GetAllFamilySettings())
        self.assertTrue(self.API.VerifySettingsWereFlipped())
    def test_Return_Family_SettingsToDefaultByDelete(self):
        self.assertTrue(self.API.ReturnFamilySettingsToDefaultByDelete())
        self.assertTrue(self.API.GetAllFamilySettings())
        self.assertTrue(self.API.VerifySettingsAreDefault())
    def test_GetSpecific_Family_Setting(self):
        self.assertTrue(self.API.GetSpecificFamilySetting())
    def test_GetAll_User_Settings(self):
        self.assertTrue(self.API.GetAllFamilySettings())
    def test_GetSpecific_User_Setting(self):        
        self.assertTrue(self.API.GetSpecificUserSetting())
    def test_FlipSwitchesOnAll_User_Settings(self):
        self.assertTrue(self.API.FlipSwitchesOnAllUserSettings())
    def test_ReturnUserSettingsToDefaultByDelete(self):
        self.assertTrue(self.API.ReturnUserSettingsToDefaultByDelete())
    @unittest.skip("test account not setup correctly on CIMA side")
    def test_SetForChildByParent(self):
        self.assertTrue(self.API.SetForChildByParent())
    @unittest.skip("test account not setup correctly on CIMA side")
    def test_DeleteValueForChildByParent(self):
        self.assertTrue(self.API.DeleteValueForChildByParent())

if __name__ == '__main__':
    unittest.main()
