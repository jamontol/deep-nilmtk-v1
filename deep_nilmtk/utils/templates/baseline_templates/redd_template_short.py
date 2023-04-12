redd_acts_from_paper = {
    'power': {'mains': ['apparent'], 'appliance': ['active']},
    'sample_rate': 6,
    'appliances': [],
    'artificial_aggregate': False,
    'DROP_ALL_NANS': True,
    'methods': {

    },
    'train': {
        'datasets': {
            'redd': {
                'path': "redd.h5",
                'buildings': {
                    3: {
                        'start_time': '2011-04-18',
                        'end_time': '2011-04-20'
                    }
                }
            }
        }
    },
    'test': {
        'datasets': {
            'redd': {
                'path': "redd.h5",
                'buildings': {
                    3: {
                        'start_time': '2011-04-25',
                        'end_time': '2011-04-26'
                    },
                }
            },

        },
        'metrics': ['mae', 'nde', 'rmse', 'relative_error', 'f1score'],
    },
    'app_activation_params': {'threshold': {'fridge': 50,
                                            'washing machine': 20,
                                            'microwave': 200,
                                            ' dish washer': 10},
                              'cutoff': {'fridge': 400,
                                          'washing machine': 500,
                                          'microwave': 1800,
                                          'dish washer': 1200},
                              'min_on': {'fridge': 60,
                                         'washing machine': 1800,
                                         'microwave': 12,
                                         'dish washer': 1800},
                              'min_off': {'fridge': 12,
                                          'washing machine': 160,
                                          'microwave': 30,
                                          'dish washer': 1800},
                              'c0': {'fridge': 0.000001,
                                     'washing machine': 0.001,
                                     'microwave': 1,
                                     'dish washer': 1}
    },
    'experiment_settings': {'kfolds': 1}
}

redd_acts_from_repo = {
    'power': {'mains': ['apparent'], 'appliance': ['active']},
    'sample_rate': 6,
    'appliances': [],
    'artificial_aggregate': False,
    'DROP_ALL_NANS': True,
    'methods': {

    },
    'train': {
        'datasets': {
            'redd': {
                'path': "redd.h5",
                'buildings': {
                    3: {
                        'start_time': '2011-04-18',
                        'end_time': '2011-04-20'
                    }
                }
            }
        }
    },
    'test': {
        'datasets': {
            'redd': {
                'path': "redd.h5",
                'buildings': {
                    3: {
                        'start_time': '2011-04-25',
                        'end_time': '2011-04-26'
                    },
                }
            },

        },
        'metrics': ['mae', 'nde', 'rmse', 'relative_error', 'f1score'],
    },
    'app_activation_params': {'threshold': {'fridge': 50,
                                            'washing machine': 20,
                                            'microwave': 200,
                                            ' dish washer': 10},
                              'cutoff': {'fridge': 300,
                                        'washing_machine': 3500,
                                        'microwave': 3000,
                                        'dishwasher': 2500},
                              'min_on': {'fridge': 10,
                                         'washing machine': 300,
                                         'microwave': 2,
                                         'dish washer': 10},
                              'min_off': {'fridge': 2,
                                          'washing machine': 26,
                                          'microwave': 5,
                                          'dish washer': 300},
                              'c0': {'kettle': 1,
                                     'fridge': 1e-6,
                                     'washing machine': 0.001,
                                     'microwave': 1,
                                     'dish washer': 1}
    },
    'experiment_settings': {'kfolds': 1}
}

redd_acts_from_paper_kfold3 = {
    'power': {'mains': ['apparent'], 'appliance': ['active']},
    'sample_rate': 6,
    'appliances': [],
    'artificial_aggregate': False,
    'DROP_ALL_NANS': True,
    'methods': {

    },
    'train': {
        'datasets': {
            'redd': {
                'path': "redd.h5",
                'buildings': {
                    3: {
                        'start_time': '2011-04-18',
                        'end_time': '2011-04-20'
                    }
                }
            }
        }
    },
    'test': {
        'datasets': {
            'redd': {
                'path': "redd.h5",
                'buildings': {
                    3: {
                        'start_time': '2011-04-25',
                        'end_time': '2011-04-26'
                    },
                }
            },

        },
        'metrics': ['mae', 'nde', 'rmse', 'relative_error', 'f1score'],
    },
    'app_activation_params': {'threshold': {'fridge': 50,
                                            'washing machine': 20,
                                            'microwave': 200,
                                            ' dish washer': 10},
                              'cutoff': {'fridge': 300,
                                        'washing_machine': 3500,
                                        'microwave': 3000,
                                        'dishwasher': 2500},
                              'min_on': {'fridge': 10,
                                         'washing machine': 300,
                                         'microwave': 2,
                                         'dish washer': 10},
                              'min_off': {'fridge': 2,
                                          'washing machine': 26,
                                          'microwave': 5,
                                          'dish washer': 300},
                              'c0': {'kettle': 1,
                                     'fridge': 1e-6,
                                     'washing machine': 0.001,
                                     'microwave': 1,
                                     'dish washer': 1}
    },
    'experiment_settings': {'kfolds': 3}
}
