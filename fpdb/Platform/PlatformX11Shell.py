"""x11 specific methods via shell
"""

import subprocess
__all__ = ['toplevel_windows', ]
#************************************************************************************
# platform implementation
#************************************************************************************
class PlatformWindow(object):
	def __init__(self, handle):
		self.handle = handle

	def __eq__(self, other): return self.handle == other.handle
	def __ne__(self, other): return not self.__eq__(other)

	def get_title(self):
		out, err = subprocess.Popen(
			'xprop _NET_WM_NAME -id %s' % self.handle, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
			).communicate()
		if not '"' in out:
			return ''
		out = out.split('\"', 1)[1]
		out = out.rsplit('"', 1)[0]
		return out

	def get_geometry(self):
		out, err = subprocess.Popen(
			'xwininfo -id %s' % self.handle, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
			).communicate()
		x = y = w = h = None
		for line in out.split('\n'):
			line = line.strip()
			if x is None:
				if line.startswith('Absolute upper-left X:'):
					x = int(line.rsplit('\x20', 1)[1])
			elif y is None:
				if line.startswith('Absolute upper-left Y:'):
					y = int(line.rsplit('\x20', 1)[1])
			elif w is None:
				if line.startswith('Width:'):
					w = int(line.rsplit('\x20', 1)[1])
			elif h is None:
				if line.startswith('Height:'):
					h = int(line.rsplit('\x20', 1)[1])
					break
		return (x, y, w, h)


#NOTE: x11 has no real notion of toplevel so we have to go over the whole tree here.
# to keep things reasonable we filter out windows that have no name.
def toplevel_windows():
	windows = []
	out, err = subprocess.Popen(
		'xwininfo -root -tree', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
		).communicate()
	if err:
		raise ValueError(err)
	for line in out.split('\n'):
		if ' (has no name): ' in line:
			continue
		line = line.strip()
		if line.startswith('0x'):
			xid = line.split('\x20', 1)[0]
			xid = int(xid, 16)
			windows.append(PlatformWindow(xid))
	return windows

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	for window in toplevel_windows():
		print 'window: "%s" %s' % (window.get_title(), window.get_geometry())






