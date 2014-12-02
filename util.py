class SettingsDictionary(dict):
	""" Adds listener support to a dictionary, in order to track changes """
	def __init__(self):
		dict.__init__(self)
		self.listeners = []

	def __setitem__(self, key, value):
		dict.__setitem__(self, key, value)
		for listener in self.listeners: listener(key, value)

class SettingDefinition:
	""" Converts setting values from string to their respective data types """
	def __init__(self, definition):
		self.title, self.name, self.datatype, self.default = definition

	def transformToString(self, value):
		if self.datatype == int:
			return '%d' % value
		if self.datatype == float:
			return '%f' % value
		if self.datatype == str:
			return value.strip()
		if self.datatype == bool:
			if value: return "True"
			else: return "False"

	def transformToValue(self, string):
		if string is None: string = self.default
		else: string = string.strip()

		if self.datatype == int:
			return int(string)
		if self.datatype == float:
			return float(string)
		if self.datatype == str:
			return string
		if self.datatype == bool:
			string = string.lower()
			if string == "true": return True
			if string == "false": return False
			return bool(int(string))

class SettingsResolver:
	""" Manages the setup of settings """
	def __init__(self, definitions):
		self.definitions = dict()
		self.settings = SettingsDictionary()

		for definition in definitions:
			definition = SettingDefinition(definition)
			self.definitions[definition.name] = definition

	def resolve(self, settings, reset = False):
		for name in self.definitions:
			string = None

			if name in settings:
				string = settings[name]

			if reset or string is not None or not name in self.settings:
				self.settings[name] = self.definitions[name].transformToValue(string)
