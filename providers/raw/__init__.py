from manifest import Manifest
from tasks import packages
from tasks import host
from tasks import filesystem
from common.tasks import filesystem as common_filesystem
from common.tasks import bootstrap
from common.tasks import locale
from common.tasks import apt
from tasks import boot
from common.tasks import boot as common_boot
from common.tasks import security
from common.tasks import network
from common.tasks import initd
from common.tasks import cleanup


def initialize():
	pass


def tasks(tasklist, manifest):
	tasklist.add(packages.HostPackages(),
	             packages.ImagePackages(),
	             host.CheckPackages())
	tasklist.add(filesystem.FormatVolume())
	if manifest.volume['filesystem'].lower() == 'xfs':
		tasklist.add(common_filesystem.AddXFSProgs())
	if manifest.volume['filesystem'].lower() in ['ext2', 'ext3', 'ext4']:
		tasklist.add(filesystem.TuneVolumeFS())
	tasklist.add(common_filesystem.CreateMountDir(),
	             filesystem.MountVolume())
	if manifest.bootstrapper['tarball']:
		tasklist.add(bootstrap.MakeTarball())
	tasklist.add(bootstrap.Bootstrap(),
	             common_filesystem.MountSpecials(),
	             locale.GenerateLocale(),
	             locale.SetTimezone(),
	             apt.DisableDaemonAutostart(),
	             apt.AptSources(),
	             #No network for the moment, skip
	             #apt.AptUpgrade(),
	             boot.ConfigureGrub(),
	             filesystem.ModifyFstab(),
	             common_boot.BlackListModules(),
	             common_boot.DisableGetTTYs(),
	             security.EnableShadowConfig(),
	             security.SetRootPassword(),
	             security.DisableSSHPasswordAuthentication(),
	             security.DisableSSHDNSLookup(),
	             network.RemoveDNSInfo(),
	             network.ConfigureNetworkIF(),
	             network.ConfigureDHCP(),
	             initd.ResolveInitScripts(),
	             initd.InstallInitScripts(),
	             cleanup.ClearMOTD(),
	             cleanup.ShredHostkeys(),
	             cleanup.CleanTMP(),
	             apt.PurgeUnusedPackages(),
	             apt.AptClean(),
	             apt.EnableDaemonAutostart(),
	             common_filesystem.UnmountSpecials(),
	             filesystem.UnmountVolume(),
	             common_filesystem.DeleteMountDir())


def rollback_tasks(tasklist, tasks_completed, manifest):
	completed = [type(task) for task in tasks_completed]

	def counter_task(task, counter):
		if task in completed and counter not in completed:
			tasklist.add(counter())

	counter_task(common_filesystem.CreateMountDir, common_filesystem.DeleteMountDir)
	counter_task(filesystem.MountVolume, filesystem.UnmountVolume)
	counter_task(common_filesystem.MountSpecials, common_filesystem.UnmountSpecials)