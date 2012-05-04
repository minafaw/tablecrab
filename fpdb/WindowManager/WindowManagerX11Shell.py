# -*- coding: utf-8 -*-

##raise NotImplementedError('this module is currently not functional')

"""window manager implementation via shell

@dependences: xwininfo, xdotool
"""
#************************************************************************************
#LICENCE: AGPL
#
# Copyright 2012 Jürgen Urner (jUrner<at>arcor.de)
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>. In the "official"
# distribution you can find the license in agpl-3.0.txt.
#************************************************************************************

import re, subprocess
import WindowManagerBase

__all__ = ['WindowManager', ]

# check if X is running
#TODO: check if test if ok
out, err = subprocess.Popen(
		'ps -e | grep X', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
		).communicate()
if not ' Xorg' in out:
	raise OSError('no X server running!')

#************************************************************************************
# window manager implementation
#
#NOTES:
# - windows are not guaranteed to be alive when we handle them
# - we can not guarantee the identity of a window. another window may have been
#   created with the same handle from the same application at any time.
#
# so i found best approach is to retrieve all data for a window on every hop and let
# the user deal with eventual troubles.
#************************************************************************************
class Window(WindowManagerBase.Window):
	def set_size(self, w, h):
		out, err = subprocess.Popen(
			'xdotool WINDOWSIZE %s %s %s' % (self.handle, w, h), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
			).communicate()

class WindowManager(WindowManagerBase.WindowManagerBase):
	def window_list(self):
		return window_list()

#************************************************************************************
# helpers
#************************************************************************************
PatRootWindow = re.compile('''
		xwininfo\:\s
		window\sid\:\s
		(?P<handle>0x[\dabcdef]+)\s+
		\(the\sroot\swindow\)\s\(has\sno\sname\)
		''',
		re.X|re.I)

PatXWinInfo = re.compile('''
		(?P<indent>\s*)
		(?P<handle>0x[\dabcdef]+)\s+
		\"(?P<title>.+)\"\:\s+
		\(
			\"(?P<application>.+?)\".*?
		\)\s+
		(?P<w>\d+)x
		(?P<h>\d+)+
		.+?\s
		\+(?P<x>\-?\d+)
		\+(?P<y>\-?\d+)
		''',
		re.X|re.I)

def get_window_is_visible(handle):
	isVisible = False
	out, err = subprocess.Popen(
		'xwininfo -id %s' % handle, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
		).communicate()
	if not err:
		for line in out.split('\n'):
			if 'Map State:' in line:
				isVisible = '\x20IsViewable' in line
				break
	return isVisible

def get_root_window():
	out, err = subprocess.Popen(
		'xwininfo -root', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
		).communicate()
	if not err:

		window = Window(
			None,
			0,
			'RootWindow',
			'',
			WindowManagerBase.Rectangle(),
			False
			)
		for line in out.split('\n'):
			if not window.handle:
				match = PatRootWindow.match(line)
				if match is not None:
					window.handle = int(match.group('handle'), 16)
			else:
				if 'Absolute upper-left X:' in line:
					x = line.rsplit('\x20', 1)[1]
					window.geometry.x = int(x)
				elif 'Absolute upper-left Y:' in line:
					y = line.rsplit('\x20', 1)[1]
					window.geometry.y = int(y)
				elif 'Width:' in line:
					w = line.rsplit('\x20', 1)[1]
					window.geometry.w = int(w)
				elif 'Height:' in line:
					h = line.rsplit('\x20', 1)[1]
					window.geometry.h = int(h)
				elif 'Map State:' in line:
					window.isVisible = '\x20IsViewable' in line
	return window

#NOTE: currently we ignore windows with no name here
#
def window_list():
	"""returns a list of all windows currently open
	@note: list should always start at the root window (the desktop)
	@note: the list should be sorted in stacking oder. root first, topmost window last
	"""
	windows = []
	window = get_root_window()
	if not window.handle:
		raise ValueError('could not retrieve root window')

	out, err = subprocess.Popen(
		'xwininfo -root -tree', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
		).communicate()
	if err:
		raise ValueError(err)

	parents = [window, ]
	for line in out.split('\n'):
		if ' (has no name): ' in line:
			continue
		match = PatXWinInfo.match(line)
		if match:
			d = match.groupdict()
			# determine window parent. xwininfo has 3 space chars per level,
			# prefixed by 2 space chars for root
			level = ((d['indent'].count('\x20') -2) / 3)
			parents = parents[:level]

			handle = int(d['handle'], 16)
			x = int(d['x'])
			y = int(d['y'])
			w = int(d['w'])
			h = int(d['h'])
			isVisible = get_window_is_visible(handle)
			window = Window(
					parents[-1],
					handle,
					unicode(d['title'].decode('utf-8')),
					d['application'],
					WindowManagerBase.Rectangle(x, y, w, h),
					isVisible,
					)
			windows.append(window)
			parents.append(window)

	return windows

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	# sample code + run WindowManager (CAUTION: will run unconditionally until keyboard interrupt!!)
	import time
	wm = WindowManager()
	for events in wm:
		for event, param in events:
			if isinstance(param, WindowManagerBase.Window):
				window = param
				print '%s: 0x%x "%s" ("%s") %s visible=%s' % (
						event,
						window.handle,
						window.title,
						window.application,
						window.geometry.to_tuple(),
						window.isVisible,
						)
		time.sleep(0.5)

