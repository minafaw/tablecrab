
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

class ConfigValue(object):
	def __init__(self, default=None):
		self.default = default
	def fromConfig(self, value):
		return value
	@classmethod
	def toConfig(klass, value):
		return value

class TypeString(ConfigValue):
	def __init__(self, default=None):
		self.default = default
	def fromConfig(self, value):
		return value
	@classmethod
	def toConfig(klass, value):
		return value

class TypeBool(ConfigValue):
	def __init__(self, default=None):
		self.default = default
	def fromConfig(self, value):
		value = value.lower().strip()
		if value == 'true':
			value = True
		elif value == 'false':
			value = False
		else:
			raise ConfigError('invalid bool, key: %s=%s' % (key, value) )
		return value
	@classmethod
	def toConfig(klass, value):
		return str(value).lower()

class TypeKey(ConfigValue):
	def __init__(self, default=None):
		self.default = default
	def fromConfig(self, value):
		myValue = value.strip()
		return myValue
	@classmethod
	def toConfig(klass, value):
		return value

class TypePoint(ConfigValue):
	def __init__(self, default=None):
		self.default = default
	def fromConfig(self, value):
		myValue = [i.strip() for i in value.split(',')]
		if len(myValue) != 2:
			raise ConfigError('invalid point')
		try:
			myValue = [int(i) for i in myValue]
		except ValueError:
			raise ConfigError('invalid poin' )
		return tuple(myValue)
	@classmethod
	def toConfig(klass, value):
		return '%s, %s' % value

class TypeSize(TypePoint): pass

#*************************************************************************************************
class Config(object):
	Defaults = (
			(
				'cli', (
					('key-pause-keyboard',  TypeKey(None)),
					('key-report-keyboard', TypeKey(None)),
					('key-report-windows', TypeKey(None)),
					('key-info-window', TypeKey(None)),
					('key-info-window-under-mouse', TypeKey(None)),
				),
			),
			(
				'tables', (
					('bool-move-mouse-to-active-table', TypeBool(False)),
				),
			),
			(
				'table', (
					('key-fold', TypeKey(None)),
					('key-check', TypeKey(None)),
					('key-raise', TypeKey(None)),
					('key-hilight-bet-amount', TypeKey(None)),
					('key-replayer', TypeKey(None)),
					('key-add-one-bb', TypeKey(None)),
					('key-subtract-one-bb', TypeKey(None)),
					('key-add-one-sb', TypeKey(None)),
					('key-subtract-one-sb', TypeKey(None)),
				),
			),
			(
				'pokerstars', (
					('bool-close-popup-news', TypeBool(False)),
				),
			),
			#'pokerstars-tables': [],		# filled in later
		)
		
	DefaultsPokerStarsTable = (
			('key', TypeKey(None)), 
			#'name': TypeString(''),		# filled in later
			('size', TypeSize(None)),
			('point-button-check', TypePoint(None)),
			('point-button-fold', TypePoint(None)),
			('point-button-raise', TypePoint(None)),
			('point-checkbox-fold', TypePoint(None)),
			('point-button-replayer-1', TypePoint(None)),
			('point-button-replayer-2', TypePoint(None)),
			)
			
		
	def __init__(self, filePathCfg=FilePathDefaultCfg):
		
		self._settings = {}
		pokerStarsTables= []
		
		userSettings = {}
		if filePathCfg is not None:
			parser = ConfigParser.ConfigParser()
			logger.debug('Config:parsing config: %s' % filePathCfg)
			# NOTE: we do config is crucial. so not errorcheck here, we want the exception to be thrown
			#            ++ ConfigParser ignores non-existing files, we add a test for that here
			open(filePathCfg).close()
			parser.read(filePathCfg)
			userSettings = dict( [(section.lower(), dict(parser.items(section)) ) for section in parser.sections()] )
			
		# parse config
		for (section, options) in self.Defaults:
			self._settings[section] = {}
			userOptions = userSettings.get(section, {})
			for (option, typeOption) in options:
				userValue = userOptions.get(option, None)
				if userValue is None:
					value = typeOption.default
				else:
					del userOptions[option]
					try:
						value = typeOption.fromConfig(userValue)
					except ConfigError:
						value = typeOption.default
						logger.debug('Config:invalid value for option:[%s]:%s' % (section, option) )
				self._settings[section][option] = value
			userSection = userSettings.get(section, None)
			if userSection is not None and not userSection:
				del userSettings[section]
				
		# parse config for pokerStars tables
		for (section, userOptions) in userSettings.items():
			if section.startswith('pokerstars-table-'):
				table = {
						'name': section[len('pokerstars-table-'): ]
						}
				for (option, typeOption) in self.DefaultsPokerStarsTable:
					userValue = userOptions.get(option, None)
					if userValue is None:
						value = typeOption.default
					else:
						del userOptions[option]
						try:
							value = typeOption.fromConfig(userValue)
						except ConfigError:
							value = typeOption.default
							logger.debug('Config:invalid value for option:[%s]:%s' % (section, option) )
						table[option] = value
				userSection = userSettings.get(section, None)
				if userSection is not None and not userSection:
					del userSettings[section]
								
				pokerStarsTables.append(table)
				
		# errorcheck
		for (section, options) in userSettings.items():
			if section in self._settings or section.startswith('pokerstars-table-'):
				for option, value in options.items():
					logger.debug('Config:unknown option:[%s]:%s' % (section, option) )
			else:
				logger.debug('Config:unknown section:[%s]' % section)
		
		#
		self._settings['pokerstars-tables'] = pokerStarsTables	
		
		
	def __getitem__(self, key):
		return self._settings[key]
	def __setitem__(self, key, value):
		self._settings[key] = value
		
	def toConfig(self):
		result = []
		for (section, options) in self.Defaults:
			result.append( ('[%s]' % section).upper() )
			for option, typeOption in options:
				value = self._settings[section][option]
				value = typeOption.toConfig(value)
				result.append( '%s=%s' % (option, value) )
			result.append('')
				
			# add PS tables following [POKERSTARS] section
			if section == 'pokerstars':
				for table in self._settings['pokerstars-tables']:
					result.append( ('[pokerstars-table-%s]' % table['name']).upper() )
					for (option, typeOption) in self.DefaultsPokerStarsTable:
						value = table[option]
						value = typeOption.toConfig(value)
						result.append( '%s=%s' % (option, value) )
					result.append('')
		return '\n'.join(result)
		
	
#**************************************************************************************************
if __name__ == '__main__':
	
	# shallow test if we our parsing is correct
	c = Config()
	print c.toConfig()
		
	
	