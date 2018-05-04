from abc import ABCMeta, abstractmethod

"""
Abstract class to implement diferent bot commands
"""
class BotCommand:
	__metaclass__ = ABCMeta

	"""
	Execte a specific command
	"""
	@abstractmethod
	def execute_command(self):
		print("Im your father")
		# raise NotImplementedError
		pass
