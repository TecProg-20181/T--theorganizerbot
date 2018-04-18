def getToken ():
    file = openFile("token.txt", 'r')
    token = file.readLine()
    return token
