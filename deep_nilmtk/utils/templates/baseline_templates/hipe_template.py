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
                                            ('motor',3): 10,
                                            ('motor',4): 50,
                                            ('motor',5): 10,
                                            ('oven', 1): 10,
                                            ('oven', 2): 100,
                                            ('oven', 3): 10,
                                            'printer': 10,
                                            'washing machine': 100},
                              'cutoff': {('motor',1): 25500,
                                         ('motor',2): 650,
                                         ('motor',3): 350,
                                         ('motor',4): 1000,
                                         ('motor',5): 900,
                                         
                                         ('oven', 1): 8000,
                                         ('oven', 2): 6000,
                                         ('oven', 3): 900,
                                         
                                         'printer': 350,

                                         'washing machine': 6000},
                              'min_on': {('motor',1): 1800,
                                         ('motor',2): 1800,
                                         ('motor',3): 3600,
                                         ('motor',4): 3600,
                                         ('motor',5): 3600,

                                          ('oven', 1): 3600,
                                          ('oven', 2): 3600,
                                          ('oven', 3): 1800,

                                          'printer': 1800,
                                          
                                          'washing machine': 900},
                              'min_off': {('motor',1): 900,
                                          ('motor',2): 900,
                                          ('motor',3): 900,

                                          ('motor',4): 900,
                                          ('motor',5): 900,

                                          ('oven', 1): 900,
                                          ('oven', 2): 900,
                                          ('oven', 3): 900,
                                          
                                          'printer': 900,
                                          
                                          'washing machine': 900},
                              'c0': {('motor',1): 1,
                                     ('motor',2): 1,
                                     ('motor',3): 1,
                                     ('motor',4): 1,
                                     ('motor',5): 1,
                                     ('oven', 1): 1,
                                     ('oven', 2): 1,
                                     ('oven', 3): 1,
                                     'printer': 1,
                                     'washing machine': 1}
    },
    'aggregate_cutoff': 45000,
    'experiment_settings': {'kfolds': 1, 'use_optuna': True}
}
