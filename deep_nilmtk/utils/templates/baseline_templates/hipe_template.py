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
                        'start_time': '2011-04-18',
                        'end_time': '2011-04-20'
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
                        'start_time': '2011-04-25',
                        'end_time': '2011-04-26'
                    },
                }
            },

        },
        'metrics': ['mae', 'nde', 'rmse', 'relative_error', 'f1score'],
    },
    'app_activation_params': {'threshold': {'motor': 50,
                                            'oven': 10,
                                            'printer': 300,
                                            'washing machine': 10},
                              'cutoff': {'motor': 25000,
                                         'oven': 8000,
                                         'printer': 350,
                                         'washing machine': 6000},
                              'min_on': {'motor': 7200,
                                          'oven': 3600,
                                          'printer': 18000,
                                          'washing machine': 10800},
                              'min_off': {'motor': 900,
                                          'oven': 900,
                                          'printer': 900,
                                          'washing machine': 900},
                              'c0': {'motor': 1,
                                     'oven': 1,
                                     'printer': 1,
                                     'washing machine': 1}
    },
    'aggregate_cutoff': 50000,
    'experiment_settings': {'kfolds': 1}
}
