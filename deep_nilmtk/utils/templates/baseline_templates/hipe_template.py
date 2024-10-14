hipe_aggregated_15min = {
    'power': {'mains': ['apparent'], 'appliance': ['active']},
    'sample_rate': 900,
    'appliances': [],
    'artificial_aggregate': False,
    'DROP_ALL_NANS': True,
    'methods': {

    },
    'train': {
        'datasets': {
            'hipe': {
                'path': "hipe_15min.h5",
                'buildings': {
                    1: {
                        'start_time': '2017-10-01',
                        'end_time': '2017-11-30'
                    }
                }
            }
        }
    },
    'test': {
        'datasets': {
            'hipe': {
                'path': "hipe_15min.h5",
                'buildings': {
                    1: {
                        'start_time': '2017-12-01',
                        'end_time': '2017-12-31'
                    },
                }
            },

        },
        'metrics': ['mae', 'nde', 'rmse', 'relative_error', 'f1score'],
    },
    'app_activation_params': {'threshold': {('motor',1): 50,
                                            ('motor',2): 50,
                                            ('motor',3): 50,
                                            'oven': 10,
                                            'printer': 300,
                                            'washing machine': 10},
                              'cutoff': {('motor',1): 25000,
                                         ('motor',2): 25000,
                                         ('motor',3): 25000,
                                         'oven': 8000,
                                         'printer': 350,
                                         'washing machine': 6000},
                              'min_on': {('motor',1): 7200,
                                         ('motor',2): 7200,
                                         ('motor',3): 7200,
                                          'oven': 3600,
                                          'printer': 18000,
                                          'washing machine': 900},
                              'min_off': {('motor',1): 900,
                                          ('motor',2): 900,
                                          ('motor',3): 900,
                                          'oven': 900,
                                          'printer': 900,
                                          'washing machine': 900},
                              'c0': {('motor',1): 1,
                                     ('motor',2): 1,
                                     ('motor',3): 1,
                                     'oven': 1,
                                     'printer': 1,
                                     'washing machine': 1}
    },
    'aggregate_cutoff': 50000,
    'experiment_settings': {'kfolds': 1, 'use_optuna': False}
}
