"""TableCrab implementation

creating custom window handlers
-------------------------------


windows running on the os are handled in following way: WindowHandlers.Registry.WindowHandlerRegistry
is a dict containing all registered window handlers. each time w new window is detected each window handler
in the registry is queried by calling its its handleWindowCreated() method. if it wants to handle the window
it should return a instance that will handle the window at runtime.

to add custom window handlers, derrive a handler from Registry.WindowHandlerBase. doing so will automatically
register it as handler.

sample code::
	
	from WindowHandlers import Registry
	
	class MyHandler(Registry.WindowHandlerBase):
		Type = Registry.WindowHandlerType
		Site = 'MySitesName'
		Window = 'MyWindowName'
		#TODO: implement handler
	
	# manipulate Reistry.WindowHandlerRegistry if necessary
			
	# run client with custom window handler
	import Cli, Config
	cfg = Config.Config()
	cli = Cli(config=config)
	cli.start()
	
it is also possible to create window handlers without registering them, to create a meta window handler for example:

sample code::

	from WindowHandlers import Registry
	
	# create a handler
	class MyHandler(object):
		Type = Registry.WindowHandlerType
		Site = 'MySitesName'
		Window = 'MyWindowName'
		#TODO: implement handler
		
	# create type name for the handler
	MyHandler.Type = Registry.reateTypeName(MyHandler)
	
	# create a meta handler and register it as handler
	class MyMetaHandler(Registry.WindowHandlerBase):
		Type = Registry.WindowHandlerType
		Site = 'MySitesName'
		Window = 'MyMetaWindow'
	
		@classmethod
		def handleWindowCreated(klass, cli, hWindow):
			return MyHandler()
	
	# run client with custom meta window handler
	import Cli, Config
	cfg = Config.Config()
	cli = Cli(config=config)
	cli.start()
		
		
for details see Registry.WindowHandlerBase


"""
