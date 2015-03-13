# Import zenpacklib from the current directory (zenpacklib.py).
from . import zenpacklib


# Create a ZenPackSpec and name it CFG.
CFG = zenpacklib.ZenPackSpec(
    name=__name__,

    zProperties={
        'DEFAULTS': {'category': 'DDN Exascaler Solution'},

        'zESMdsNodes': {
            'type': 'string',
        },

        'zESOssNodes': {
            'type': 'string',
        },
    },

    classes={
        'ExascalerDevice': {
            'base': zenpacklib.Device,
            'label': 'ExascalerDevice',

            'properties': {
                'deadtime': {
                    'label': 'deadtime',
                    'order': 4.0,
                },
                '"monitor_interval': {
                    'label': '"monitor_interval',
                    'order': 4.1,
                },
                'no_quorum_policy': {
                    'label': 'no_quorum_policy',
                    'order': 4.2,
                },
                'type': {
                    'label': 'type',
                    'order': 4.4,
                },
                'pingd': {
                    'label': 'pingd',
                    'order': 4.5,
                },
                'sfa_list': {
                    'label': 'sfa_list',
                    'order': 4.6,
                },
                'numFs': {
                    'label': 'numFs',
                    'order': 4.7,
                },
                'numHosts': {
                    'label': 'numHosts',
                    'order': 4.8,
                },
                'fs_list': {
                    'label': 'fs_list',
                    'order': 4.9,
                },
                'monitor_interval': {
                    'label': 'monitor_interval',
                    'order': 4.10,
                },

            }
        },

        'FsList': {
            'base': zenpacklib.Component,
            'label': 'FsList',
            'properties': {
                'mds_list': {
                    'label': 'Mds List',
                    'order': 4.0,
                },

                'mdt_opts': {
                    'label': 'Mdt Options',
                    'order': 4.1,
                },

                'mdt_parts': {
                    'label': 'Mdt Parts',
                    'order': 4.2,
                },

                'mdt_size': {
                    'label': 'Mdt Size',
                    'order': 4.3,
                },

                'mgs_internal': {
                    'label': 'Mgs Internal',
                    'order': 4.4,
                },

                'mgs_size': {
                    'label': 'Mgs Size',
                    'order': 4.5,
                },

                'mgs_standalone': {
                    'label': 'Mgs Standalone',
                    'order': 4.6,
                },
                'oss_list': {
                    'label': 'Oss List',
                    'order': 4.7,
                },
                'ost_device_path': {
                    'label': 'Ost device path',
                    'order': 4.8,
                },
                'ost_mke2fs_opts': {
                    'label': 'Ost mke2fs Options',
                    'order': 4.9,
                },
                'ost_opts': {
                    'label': 'Ost Options',
                    'order': 4.10,
                },
            }
        },

        'MetaDataServer': {
            'base': zenpacklib.Component,
            'label': 'MetaDataServer',
            'properties': {
                'eth0_gateway': {
                    'label': 'eth0_gateway',
                    'order': 4.0,
                },

                'eth0_ip': {
                    'label': 'eth0_ip',
                    'order': 4.1,
                },

                'eth0_netmask': {
                    'label': 'eth0_netmask',
                    'order': 4.2,
                },

                'eth1_ip': {
                    'label': 'eth1_ip',
                    'order': 4.3,
                },

                'eth1_netmask': {
                    'label': 'eth1_netmask',
                    'order': 4.4,
                },

                'ipmi_ip_base': {
                    'label': 'ipmi_ip_base',
                    'order': 4.5,
                },
                'ipmi_netmask': {
                    'label': 'ipmi_netmask',
                    'order': 4.6,
                },
                'lnets': {
                    'label': 'lnets',
                    'order': 4.7,
                },

                'nic_list': {
                    'label': 'nic_list',
                    'order': 4.8,
                },

                'nw_addr': {
                    'label': 'nw_addr',
                    'order': 4.8,
                },

                'stonith_pass': {
                    'label': 'stonith_pass',
                    'order': 4.10,
                },

                'stonith_primary_peers': {
                    'label': 'stonith_primary_peers',
                    'order': 4.11,
                },
                'stonith_type': {
                    'label': 'stonith_type',
                    'order': 4.12,
                },
                'stonith_user': {
                    'label': 'stonith_user',
                    'order': 4.13,
                },
                'management_address': {
                    'label': 'management_address',
                    'order': 4.14,
                },
                'status': {
                    'label': 'Status',
                    'order': 4.15,
                }
            }
        },

        'ObjectStorageServer': {
            'base': zenpacklib.Component,
            'label': 'ObjectStorageServer',
            'properties': {
                'eth0_gateway': {
                    'label': 'eth0_gateway',
                    'order': 4.0,
                },

                'eth0_ip': {
                    'label': 'eth0_ip',
                    'order': 4.1,
                },

                'eth0_netmask': {
                    'label': 'eth0_netmask',
                    'order': 4.2,
                },

                'eth1_ip': {
                    'label': 'eth1_ip',
                    'order': 4.3,
                },

                'eth1_netmask': {
                    'label': 'eth1_netmask',
                    'order': 4.4,
                },

                'ipmi_ip_base': {
                    'label': 'ipmi_ip_base',
                    'order': 4.5,
                },
                'ipmi_netmask': {
                    'label': 'ipmi_netmask',
                    'order': 4.6,
                },
                'lnets': {
                    'label': 'lnets',
                    'order': 4.7,
                },

                'nic_list': {
                    'label': 'nic_list',
                    'order': 4.8,
                },

                'nw_addr': {
                    'label': 'nw_addr',
                    'order': 4.8,
                },

                'stonith_pass': {
                    'label': 'stonith_pass',
                    'order': 4.10,
                },

                'stonith_primary_peers': {
                    'label': 'stonith_primary_peers',
                    'order': 4.11,
                },
                'stonith_type': {
                    'label': 'stonith_type',
                    'order': 4.12,
                },
                'stonith_user': {
                    'label': 'stonith_user',
                    'order': 4.13,
                },
                'devesfs_ost_count': {
                    'label': 'devesfs_ost_count',
                    'order': 4.14,
                },
                'management_address': {
                    'label': 'management_address',
                    'order': 4.15,
                },
                'status': {
                    'label': 'Status',
                    'order': 4.16,
                }
            }
        },
    },

    class_relationships=zenpacklib.relationships_from_yuml(
        """[ExascalerDevice]++-[FsList]
           [ExascalerDevice]++-[MetaDataServer]
           [ExascalerDevice]++-[ObjectStorageServer]"""
    )
)

# Create the specification.
CFG.create()
