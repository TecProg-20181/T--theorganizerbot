def getToken():
		file = open("TOKEN.txt", 'r')

		# line: string
		myToken = file.read()

		return myToken
