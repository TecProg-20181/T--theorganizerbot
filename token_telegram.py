def getToken():
		file = open("TOKEN.txt", 'r')

		# line: string
		myToken = file.read(45)

		return myToken
