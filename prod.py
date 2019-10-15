from unv.app.settings import ComponentSettings

SETTINGS = ComponentSettings.create({
    'deploy': {
        'tasks': [
            'tasks:OrangePiOnePlusTasks',
        ],
        'hosts': {
            'opi': {
                'public_ip': '192.168.1.46',
                'components': ['opi'],
                'settings': {
                    'opi': {'mac': 'aa:00:aa:00:aa:08'}
                }
            }
        }
    }
})
