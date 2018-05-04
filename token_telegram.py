TOLKEN_NUMBER_CHARACTERS = 45

def getToken():
		file = open("TOKEN.txt", 'r')

		# line: string
		myToken = file.read(TOLKEN_NUMBER_CHARACTERS)

		return myToken
