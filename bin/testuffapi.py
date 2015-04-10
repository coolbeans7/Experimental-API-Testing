import requests
from requests import session

class Testuff(object):
	def __init__(self):
		self.URL = 'http://sdev61.plaxo.com:8080'
		self.TESTUFF = '/testuff'
		self.EMAIL = '/email'
		self.testDict = {'AddFamily':'15a02e068632f0121f14ca78f06f8939',
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

	def update(self, _testChoice, _status):
		id = self.testDict[_testChoice]
		status = _status
		#status = 'passed'
		username = ''
		password = ''
		service = '6'

		data = {
			'test_id':id,
			'status':status,
			'username':username,
			'password':password,
			'service':service,
		}

		curURL = '%s%s' % (self.URL, self.TESTUFF)
		response = requests.post(curURL, data)
		
		if 'true' not in response.text:
			raise Exception("Fail posting data to Testuff")
