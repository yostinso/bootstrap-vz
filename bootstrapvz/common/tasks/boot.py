from bootstrapvz.base import Task
from .. import phases
import os.path


class BlackListModules(Task):
	description = 'Blacklisting kernel modules'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		blacklist_path = os.path.join(info.root, 'etc/modprobe.d/blacklist.conf')
		with open(blacklist_path, 'a') as blacklist:
			blacklist.write(('# disable pc speaker\n'
			                 'blacklist pcspkr'))


class DisableGetTTYs(Task):
	description = 'Disabling getty processes'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from ..tools import sed_i
		inittab_path = os.path.join(info.root, 'etc/inittab')
		tty1 = '1:2345:respawn:/sbin/getty 38400 tty1'
		sed_i(inittab_path, '^' + tty1, '#' + tty1)
		ttyx = ':23:respawn:/sbin/getty 38400 tty'
		for i in range(2, 7):
			i = str(i)
			sed_i(inittab_path, '^' + i + ttyx + i, '#' + i + ttyx + i)
