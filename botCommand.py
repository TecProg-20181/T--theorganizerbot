from abc import ABC, abstractmethod

class BotCommand(ABC):
	"""
	Abstract class to implement diferent bot commands
	"""

	@abstractmethod
	def execute_commnd():
		"""
		Execte a specific command
		"""
		
		pass