
import sys, os, logging
from logging import handlers
import ConfigParser

#***************************************************************************************************
__application_name__ = 'TableCrab'
__author__ = 'juergen urner'
__emainl__ = 'jUrner@arcor.de'
__version__ = '0.1.0'

#***************************************************************************************************
DirApplication = os.path.dirname(os.path.abspath(__file__))
DirUser = os.path.join(DirApplication, 'User')
FilePathDefaultCfg = os.path.join(DirUser, 'default.cfg')
FilePathErrorLog = os.path.join(DirUser, 'errlog.txt')

logger = logging.getLogger(__application_name__)
excHandler = handlers.RotatingFileHandler(
		FilePathErrorLog,
		mode='a',
		maxBytes=32000,
		backupCount=0,
		)
excHandler.setLevel(logging.CRITICAL)
logger.addHandler(excHandler)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")

#****************************************************************************************************
class ConfigError(Exception): pass

class ConfigValue(object): pass

class TypeString(ConfigValue):
	def __init__(self, default=None):
		self.default = default
	def fromConfig(self, key, value):
		return value
	def toConfig(self, key, value):
		return value

class TypeBool(ConfigValue):
	def __init__(self, default=None):
		self.default = default
	def fromConfig(self, key, value):
		value = value.lower().strip()
		if value == 'true':
			value = True
		elif value == 'false':
			value = False
		else:
			raise ConfigError('invalid bool, key: %s=%s' % (key, value) )
		return value
	def toConfig(self, key, value):
		return str(value).lower()

class TypeKey(ConfigValue):
	def __init__(self, default=None):
		self.default = default
	def fromConfig(self, key, value):
		myValue = value.strip()
		return myValue
	def toConfig(self, key, value):
		return value

class TypePoint(ConfigValue):
	def __init__(self, default=None):
		self.default = default
	def fromConfig(self, key, value):
		myValue = [i.strip() for i in value.split(',')]
		if len(myValue) != 2:
			raise ConfigError('invalid point, key: %s=%s' % (key, value) )
		try:
			myValue = [int(i) for i in myValue]
		except ValueError:
			raise ConfigError('invalid point, key: %s=%s' % (key, value) )
		return tuple(myValue)
	@classmethod
	def toConfig(self, key, value):
		return '%s, %s' % value

class TypeSize(TypePoint): pass

#*************************************************************************************************
class Config(object):
	Defaults = {
				
			'cli': {
				'key-pause-keyboard':  TypeKey(None),
				'key-report-keyboard': TypeKey(None),
				'key-report-windows': TypeKey(None),
				'key-info-window': TypeKey(None),
				'key-info-window-under-mouse': TypeKey(None),
				},
				
			'tables': {
				'bool-move-mouse-to-active-table': TypeBool(False),
				},
			
			'table': {
				'key-fold': TypeKey(None),
				'key-check': TypeKey(None),
				'key-raise': TypeKey(None),
				'key-hilight-bet-amount': TypeKey(None),
				'key-replayer': TypeKey(None),
				'key-add-one-bb': TypeKey(None),
				'key-subtract-one-bb': TypeKey(None),
				'key-add-one-sb': TypeKey(None),
				'key-subtract-one-sb': TypeKey(None),
				},
			
			'pokerstars': {
					'bool-close-popup-news': TypeBool(False),
					},
			'pokerstars-tables': [],		#
		}
			
	DefaultsPokerStarsTable = {
			'key': TypeKey(None), 
			'name': TypeString(''),
			'size': TypeSize(None),
			'point-button-check': TypePoint(None),
			'point-button-fold': TypePoint(None),
			'point-button-raise': TypePoint(None),
			'point-checkbox-fold': TypePoint(None),
			'point-button-replayer-1': TypePoint(None),
			'point-button-replayer-2': TypePoint(None),
			}
		
		
		
	def __init__(self, filePathCfg=FilePathDefaultCfg):
		self._settings = {}
			
		parser = None
		if filePathCfg is not None:
			parser = ConfigParser.ConfigParser()
			parser.read(filePathCfg)
			
		for section, values in self.Defaults.items():
			if section == 'global':
				self._settings[section] = values
			
			elif section == 'pokerstars-tables':
				tables = []
				self._settings[section] = tables
				# try to get value from cfg
				if parser is not None:
						parserSections = [i.lower() for i in parser.sections()]
						for section in parserSections:
							if section.startswith('pokerstars-table-'):
								table = {}
								tables.append(table)
								parserSection = parser.sections()[parserSections.index(section)]
								for option, typeOption in self.DefaultsPokerStarsTable.items():
									if parser.has_option(parserSection, option):
										value = parser.get(parserSection, option)
										value = typeOption.fromConfig('[%s]%s' % (parserSection, option), value)
										table[option] = value
										continue
									
									# default
									table[option] = typeOption.default
						
			else:
				self._settings[section] = {}
				for option, typeOption in values.items():
					if isinstance(typeOption, ConfigValue):
						
						# try to get value from cfg
						if parser is not None:
							#NOTE: ConfigParser sections are case-sensitive, handle case-insensitive here
							parserSections = [i.lower() for i in parser.sections()]
							if section in parserSections:
								parserSection = parser.sections()[parserSections.index(section)]
								if parser.has_option(parserSection, option):
									value = parser.get(parserSection, option)
									value = typeOption.fromConfig('[%s]%s' % (parserSection, option), value)
									self._settings[section][option] = value
									continue
						
						# default
						self._settings[section][option] = typeOption.default
	
		
	def __getitem__(self, key):
		return self._settings[key]
	def __setitem__(self, key, value):
		self._settings[key] = value

#**************************************************************************************************
if __name__ == '__main__':
	
	# shallow test if we our parsing of default.cfg is correct
	c = Config()
	for section, value in c._settings.items():
		
		if section == 'pokerstars-tables':
			for table in value:
				print '[%s-XX]' % 'pokerstars-table'
				for option, value in table.items():
					print '%s=%s' % (option, value)
				print
		else:
			print '[%s]' % section
			for option, value in value.items():
				print '%s=%s' % (option, value)
		print
		
	
	