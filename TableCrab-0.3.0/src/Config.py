"""client configuration
"""
import sys, os, logging, operator
from logging import handlers
import ConfigParser

#***************************************************************************************************
__application_name__ = 'TableCrab'
__author__ = 'juergen urner'
__email__ = 'jUrner@arcor.de'
__version__ = '0.3.0'
__release_name__ = '%s-%s' % (__application_name__, __version__)

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

class TypeFloat(ConfigValue):
	def __init__(self, default=None):
		self.default = default
	def fromConfig(self, value):
		value = value.strip()
		try:
			value =float(value)
		except ValueError:
			raise ConfigError('invalid floating point number')
		return value
	@classmethod
	def toConfig(klass, value):
		return str(value)

class TypeInt(ConfigValue):
	def __init__(self, default=None):
		self.default = default
	def fromConfig(self, value):
		value = value.strip()
		try:
			value =int(value)
		except ValueError:
			raise ConfigError('invalid integer')
		return value
	@classmethod
	def toConfig(klass, value):
		return str(value)

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
			raise ConfigError('invalid bool')
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

class TypeChoice(ConfigValue):
	def __init__(self, default=None, choices=None):
		self.default = default
		self.choices = () if choices is None else choices
	def fromConfig(self, value):
		myValue = value.strip().lower()
		if value not in self.choices:
			raise ConfigError('invalid choice')
		return value
	@classmethod
	def toConfig(klass, value):
		return value	
	
#*************************************************************************************************
class Config(object):
	SectionCli = (
			'cli', (
				('host-single-app',  TypeString(None) ),
				('port-single-app',  TypeInt(None) ),
				('key-pause-keyboard',  TypeKey(None) ),
				('key-report-keyboard', TypeKey(None) ),
				('key-report-windows', TypeKey(None) ),
				('key-info-window', TypeKey(None) ),
				('key-info-window-under-mouse', TypeKey(None) ),
			)
		)
	SectionTables = (
			'tables', (
				('bool-move-mouse-to-active-table', TypeBool(False) ),
				('flag-move-mouse-to-active-table-edge', TypeChoice(default='top-left', choices=('top-left', 'top-right', 'bottom-left', 'bottom-right') ) ),
				('offset-move-mouse-to-active-table', TypeInt(0)),
			)
		)
	SectionTable = (
			'table', (
				('key-fold', TypeKey(None) ),
				('key-check', TypeKey(None) ),
				('key-raise', TypeKey(None) ),
				('key-hilight-bet-amount', TypeKey(None) ),
				('key-replayer', TypeKey(None) ),
				#('type-alter-bet-amount': []),	# filled in later [{'key': TypeKey, 'type': TypeChoice, 'factor': TypeInt), {'key-add-blind': params, ...}]
				#'type-alter-bet-amount-mouse-wheel-up', # filled in later {'type': TypeChoice, 'factor': TypeInt}
				#'type-alter-bet-amount-mouse-wheel-down', # filled in later {'type': TypeChoice, 'factor': TypeInt}
			)
		)
	SectionPokerstars = (
			'pokerstars', (
				('bool-close-popup-news', TypeBool(False)),
			)
		)
	SectionPokerStarsReplayer = (
			'pokerstars-replayer', (
			('key', TypeKey(None)),
			('size', TypeSize(None)),
			('point-button-first', TypePoint(None)),
			('key-button-first', TypeKey(None)),
			('point-button-last', TypePoint(None)),
			('key-button-last', TypeKey(None)),
			('point-button-start', TypePoint(None)),
			('key-button-start', TypeKey(None)),
			('point-button-stop', TypePoint(None)),
			('key-button-stop', TypeKey(None)),
			('point-button-prev', TypePoint(None)),
			('key-button-prev', TypeKey(None)),
			('point-button-next', TypePoint(None)),
			('key-button-next', TypeKey(None)),
			)
		)
	
	SectionPokerStarsTable = (
		('key', TypeKey(None) ), 
		#('name', TypeString('') ),		# filled in later
		('size', TypeSize(None)),
		('point-button-check', TypePoint(None) ),
		('point-button-fold', TypePoint(None) ),
		('point-button-raise', TypePoint(None) ),
		('point-checkbox-fold', TypePoint(None) ),
		('point-button-replayer-1', TypePoint(None) ),
		('point-button-replayer-2', TypePoint(None) ),
		)
		
	Sections = (
			SectionCli ,
			SectionTables,
			SectionTable,
			SectionPokerstars,
			#'pokerstars-tables': [SectionPokerStarsTable(0), ...SectionPokerStarsTable(N)],	# filled in later
			SectionPokerStarsReplayer,
			)
			
		
	def _cfgGetValue(self, userOptions, option, typeOption):
		"""private method to retrieve a value for an option"""
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
		return value
	
	def __init__(self, filePathCfg=FilePathDefaultCfg):
		
		self._settings = {}
		pokerStarsTables= []
		tableAlterBetAmounts = []
		
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
		for (section, options) in self.Sections:
			self._settings[section] = {}
			userOptions = userSettings.get(section, {})
			for (option, typeOption) in options:
				self._settings[section][option] = self._cfgGetValue(userOptions, option, typeOption)
			userSection = userSettings.get(section, None)
			if userSection is not None and not userSection:
				del userSettings[section]
				
		# special handling for alter-bet-amount-(N)
		for (section, userOptions) in userSettings.items():
			if section == 'table':
				alterBetAmounts = []
				for option, value in userOptions.items():
					
					if option in ('type-alter-bet-amount-mouse-wheel-up', 'type-alter-bet-amount-mouse-wheel-down'):
						baseValue = factor = None
						params = value.strip()
						if not params:
							pass
						else:
							params = [i.strip() for i in value.split(',')]
							if len(params) != 2:
								logger.debug('Config:invalid params: [%s]:%s' % (section, option) )
							else:
								try: baseValue = TypeChoice(choices=('big-blind', 'small-blind')).fromConfig(params[0])
								except ConfigError: logger.debug('Config:invalid params: [%s]:%s' % (section, option) )
								else:
									try: factor = TypeFloat().fromConfig(params[1])
									except ConfigError: logger.debug('Config:invalid params: [%s]:%s' % (section, option) )
						self._settings[section][option] = {'baseValue': baseValue, 'factor': factor}
						del userSettings[section][option]
					
					elif option.startswith('type-alter-bet-amount-'):
						factor = None
						try:
							n = int(option[len('type-alter-bet-amount-'): ])
						except ValueError:
							logger.debug('Config:invalid option name: [%s]:%s' % (section, option) )
						else:
							params = [i.strip() for i in value.split(',')]
							if len(params) != 3:
								logger.debug('Config:invalid params: [%s]:%s' % (section, option) )
							else:
								try: key = TypeKey().fromConfig(params[0])
								except ConfigError: logger.debug('Config:invalid params: [%s]:%s' % (section, option) )
								else:
									try: baseValue = TypeChoice(choices=('big-blind', 'small-blind')).fromConfig(params[1])
									except ConfigError: logger.debug('Config:invalid params: [%s]:%s' % (section, option) )
									else:
										try: factor = TypeFloat().fromConfig(params[2])
										except ConfigError: logger.debug('Config:invalid params: [%s]:%s' % (section, option) )
						del userSettings[section][option]
						if factor is not None:
							alterBetAmounts.append( (n, {'key': key, 'baseValue': baseValue, 'factor': factor}) )
					
				alterBetAmounts.sort(key=operator.itemgetter(0) )
				tableAlterBetAmounts = [i[1] for i in alterBetAmounts]
					
				
				
		# parse config for pokerStars tables
		for (section, userOptions) in userSettings.items():
			if section.startswith('pokerstars-table-'):
				table = {
						'name': section[len('pokerstars-table-'): ]
						}
				for (option, typeOption) in self.SectionPokerStarsTable:
					table[option] = self._cfgGetValue(userOptions, option, typeOption)
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
		self._settings['table']['alter-bet-amounts'] = tableAlterBetAmounts	
		
		
	def __getitem__(self, section):
		return self._settings[section]
	def __setitem__(self, key, section):
		self._settings[section] = value
		
	def toConfig(self):
		"""dumps settings to a string representing a cfg file
		@return: (str)
		"""
		result = []
		for (section, options) in self.Sections:
			result.append( ('[%s]' % section).upper() )
			for option, typeOption in options:
				value = self._settings[section][option]
				value = typeOption.toConfig(value)
				result.append( '%s=%s' % (option, value) )
			
			# special handling for alter-bet-amount-(N)
			if section == 'table':
				for n, alterBetAmount in enumerate(self._settings['table']['alter-bet-amounts']):
					option = 'alter-bet-amount-%s' % n
					value = '%(key)s, %(baseValue)s, %(factor)s' % alterBetAmount
					result.append('%s=%s' % (option, value))
				
				for option in ('type-alter-bet-amount-mouse-wheel-up', 'type-alter-bet-amount-mouse-wheel-down'):
					params = self._settings['table'][option]
					if params['baseValue'] is None:
						value = ''
					else:
						value = '%(baseValue)s, %(factor)s' % params
					result.append('%s=%s' % (option, value))
			
			result.append('')
				
			# add PS tables following [POKERSTARS] section
			if section == 'pokerstars':
				for table in self._settings['pokerstars-tables']:
					result.append( ('[pokerstars-table-%s]' % table['name']).upper() )
					for (option, typeOption) in self.SectionPokerStarsTable:
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
	print '-----------------------------------------------'
	print c.toConfig()
		
	
	