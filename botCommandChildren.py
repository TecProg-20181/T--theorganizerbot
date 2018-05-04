from botCommand import BotCommand

"""Classes that define the bot commands"""

#Command /new
class BotCommandNew(BotCommand):
	def execute_command(self):
		super(BotCommandNew, self).execute_command()
		print ("Executing: '/new' command")
		pass

# Command /rename
class BotCommandRename(BotCommand):
	def execute_command(self):
		pass

#Command /duedate
class BotCommandDuedate(BotCommand):
	def execute_command(self):
		pass

#Command /duplicate
class BotCommandDuplicate(BotCommand):
	def execute_command(self):
		pass

#Command /delete
class BotCommandDelete(BotCommand):
	def execute_command(self):
		pass

#Command /todo
class BotCommandTodo(BotCommand):
	def execute_command(self):
		pass

#Command /done
class BotCommandDone(BotCommand):
	def execute_command(self):
		pass

#Command /list
class BotCommandList(BotCommand):
	def execute_command(self):
		pass

#Command /dependson
class BotCommandDependson(BotCommand):
	def execute_command(self):
		pass

#Command /priority
class BotCommandPriority(BotCommand):
	def execute_command(self):
		pass

#Command /start
class BotCommandStart(BotCommand):
	def execute_command(self):
		pass

#Command /help
class BotCommandHelp(BotCommand):
	def execute_command(self):
		pass

#Command Error
class BotCommandError(BotCommand):
	def execute_command(self):
		super(BotCommandNew, self).execute_command()
		print ("Executing: '/error' command")
		pass