import unittest
import taskbot
from token_telegram import *

class URLTest(unittest.TestCase):
	"""docstring for URLTest"""
	def test_get_url(self):
		TOKEN = getToken()
		URL = "https://api.telegram.org/bot{}/".format(TOKEN)

		expected = "{\"ok\":false,\"error_code\":404,\"description\":\"Not Found: method not found\"}"
		result = taskbot.get_url(URL)

		self.assertEqual(expected, result)

if __name__ == "__main__":
	unittest.main()
