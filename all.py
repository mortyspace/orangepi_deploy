from unv.app.settings import ComponentSettings

HOSTS = {
    f'opi.{num}': {
        'public_ip': f'192.168.1.8{num}',
        'components': ['opi'],
        'settings': {
            'opi': {'mac': 'aa:00:aa:00:aa:05'}
        }
    }
    for num in range(1, 9)
}

SETTINGS = ComponentSettings.create({
    'deploy': {
        'tasks': [
            'tasks:OrangePiOnePlusTasks',
        ],
        'hosts': HOSTS
    }
})
