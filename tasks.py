from unv.deploy.settings import DeployComponentSettings
from unv.deploy.tasks import DeployComponentTasks, register


class OrangePiOnePlusSettings(DeployComponentSettings):
    NAME = 'opi'
    DEFAULT = {
        'user': 'orangepi',
        'iface': 'eth0',
        'mac': 'aa:00:aa:00:aa:01'
    }
    SCHEMA = {
        'user': {'type': 'string', 'required': True},
        'mac': {'type': 'string', 'required': True},
        'iface': {'type': 'string', 'required': True}
    }

    @property
    def iface(self):
        return self._data['iface']

    @property
    def mac(self):
        return self._data['mac']



class OrangePiOnePlusTasks(DeployComponentTasks):
    SETTINGS = OrangePiOnePlusSettings()

    @register
    async def maxcpu(self):
        with self._prefix('DEBIAN_FRONTEND=noninteractive'):
            await self._sudo('rm -r /var/cache/apt/*')
            # await self._sudo('apt-get update --fix-missing')
            await self._sudo('apt-get install cpufrequtils -y -q')

        await self._sudo('cpufreq-set -g performance')
        for core in range(4):
            await self._sudo(f'echo 1 > /sys/devices/system/cpu/cpu{core}/online')

    @register
    async def upgrade(self):
        with self._prefix('DEBIAN_FRONTEND=noninteractive'):
            await self._sudo('apt-get upgrade -y -q')

    @register
    async def temps(self):
        result = await self._run(
            'cat /sys/devices/virtual/thermal/thermal_zone0/temp')
        print(self.public_ip, result)

    @register
    async def setup(self):
        # copy ssh keys
        await self._local(
            f'ssh-copy-id -i ~/.ssh/id_rsa {self.user}@{self.public_ip}'
            f' -p {self.port}'
        )
        await self._run(
            'sudo mkdir -p /root/.ssh', interactive=True)
        await self._run(
            'sudo cp ~/.ssh/authorized_keys /root/.ssh/', interactive=True)

        # remove ununsed packages
        with self._prefix('DEBIAN_FRONTEND=noninteractive'):
            try:
                await self._sudo('apt-get clean')
                await self._sudo('rm -rf /var/cache/apt/*')
                await self._sudo('rm -rf /var/lib/apt/lists/*')
                await self._sudo('rm /var/lib/dpkg/lock*')
            except:
                pass

            try:
                await self._sudo('apt-get update -y -q')
            except:
                pass

            await self._sudo(
                'apt purge evolution-data-server cups lightdm '
                'lightdm-gtk-greeter gnome-screensaver whoopsie '
                'indicator-sound indicator-bluetooth cpus-* network-manager '
                '*polkit* sudo -y -q'
            )
            await self._sudo('apt autoremove -y -q')
            await self._sudo('apt install macchanger cpufrequtils htop -y -q')

        # change mac address
        with self._set_user('root'):
            await self._upload_template(
                self.settings.local_root / 'macchanger.service',
                '/etc/systemd/system/macchanger.service',
                {'mac': self.settings.mac, 'iface': self.settings.iface}
            )
        await self._sudo('systemctl enable macchanger')
        
        # resize to whole sd card size
        await self._sudo('/usr/local/sbin/resize_rootfs.sh')
        
        await self._reboot(timeout=0)