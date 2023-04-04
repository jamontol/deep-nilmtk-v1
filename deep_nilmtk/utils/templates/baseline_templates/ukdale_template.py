uk_dale_acts_from_paper = {
    'power': {'mains': ['active'], 'appliance': ['active']},
    'sample_rate': 6,
    'appliances': [],
    'artificial_aggregate': False,
    'DROP_ALL_NANS': True,
    'methods': {

    },
    'train': {
        'datasets': {
            'ukdale': {
                'path': "ukdale.h5",
                'buildings': {
                    1: {
                        'start_time': '2015-01-04',
                        'end_time': '2015-01-06'
                    }
                }
            }
        }
    },
    'test': {
        'datasets': {
            'ukdale': {
                'path': "ukdale.h5",
                'buildings': {
                    1: {
                        'start_time': '2015-04-16',
                        'end_time': '2015-04-17'
                    },
                }
            },

        },
        'metrics': ['mae', 'nde', 'rmse', 'f1score'],
    },
    'app_activation_params': {'threshold': {'kettle': 2000,
                                            'fridge': 50,
                                            'washing machine': 20,
                                            'microwave': 200,
                                            ' dish washer': 10},
                              'cutoff': {'kettle': 3100,
                                          'fridge': 300,
                                          'washing machine': 2500,
                                          'microwave': 3000,
                                          'dish washer': 2500},
                              'min_on': {'kettle': 12,
                                         'fridge': 60,
                                         'washing machine': 1800,
                                         'microwave': 12,
                                         'dish washer': 1800},
                              'min_off': {'kettle': 0,
                                          'fridge': 12,
                                          'washing machine': 160,
                                          'microwave': 30,
                                          'dish washer': 1800},
                              'c0': {'kettle': 1,
                                     'fridge': 0.000001,
                                     'washing machine': 0.01,
                                     'microwave': 1,
                                     'dish washer': 1}
    },
    'experiment_settings': {'kfolds': 1}
}

uk_dale_acts_from_repo = {
    'power': {'mains': ['active'], 'appliance': ['active']},
    'sample_rate': 6,
    'appliances': [],
    'artificial_aggregate': False,
    'DROP_ALL_NANS': True,
    'methods': {

    },
    'train': {
        'datasets': {
            'ukdale': {
                'path': "ukdale.h5",
                'buildings': {
                    1: {
                        'start_time': '2015-01-04',
                        'end_time': '2015-01-06'
                    }
                }
            }
        }
    },
    'test': {
        'datasets': {
            'ukdale': {
                'path': "ukdale.h5",
                'buildings': {
                    1: {
                        'start_time': '2015-04-16',
                        'end_time': '2015-04-17'
                    },
                }
            },

        },
        'metrics': ['mae', 'nde', 'rmse', 'f1score'],
    },
    'app_activation_params': {'threshold': {'kettle': 2000,
                                            'fridge': 50,
                                            'washing machine': 20,
                                            'microwave': 200,
                                            ' dish washer': 10},
                              'cutoff': {'kettle': 3100,
                                        'fridge': 300,
                                        'washing_machine': 2500,
                                        'microwave': 3000,
                                        'dishwasher': 2500},
                              'min_on': {'kettle': 2,
                                         'fridge': 10,
                                         'washing machine': 300,
                                         'mircowave': 2,
                                         'dish washer': 300},
                              'min_off': {'kettle': 0,
                                          'fridge': 2,
                                          'washing machine': 26,
                                          'microwave': 5,
                                          'dish washer': 300},
                              'c0': {'kettle': 1,
                                     'fridge': 1e-6,
                                     'washing machine': 0.01,
                                     'microwave': 1,
                                     'dish washer': 1}
    },
    'experiment_settings': {'kfolds': 1}
}

uk_dale_acts_from_paper_kfold3 = {
    'power': {'mains': ['active'], 'appliance': ['active']},
    'sample_rate': 6,
    'appliances': [],
    'artificial_aggregate': False,
    'DROP_ALL_NANS': True,
    'methods': {

    },
    'train': {
        'datasets': {
            'ukdale': {
                'path': "ukdale.h5",
                'buildings': {
                    1: {
                        'start_time': '2015-01-04',
                        'end_time': '2015-01-06'
                    }
                }
            }
        }
    },
    'test': {
        'datasets': {
            'ukdale': {
                'path': "ukdale.h5",
                'buildings': {
                    1: {
                        'start_time': '2015-04-16',
                        'end_time': '2015-04-17'
                    },
                }
            },

        },
        'metrics': ['mae', 'nde', 'rmse', 'f1score'],
    },
    'app_activation_params': {'threshold': {'kettle': 2000,
                                            'fridge': 50,
                                            'washing machine': 20,
                                            'microwave': 200,
                                            ' dish washer': 10},
                              'cutoff': {'kettle': 3100,
                                          'fridge': 300,
                                          'washing machine': 2500,
                                          'microwave': 3000,
                                          'dish washer': 2500},
                              'min_on': {'kettle': 12,
                                         'fridge': 60,
                                         'washing machine': 1800,
                                         'microwave': 12,
                                         'dish washer': 1800},
                              'min_off': {'kettle': 0,
                                          'fridge': 12,
                                          'washing machine': 160,
                                          'microwave': 30,
                                          'dish washer': 1800},
                              'c0': {'kettle': 1,
                                     'fridge': 0.000001,
                                     'washing machine': 0.01,
                                     'microwave': 1,
                                     'dish washer': 1}
    },
    'experiment_settings': {'kfolds': 3}
}


NILM22_experiment = {
    'power': {'mains': ['active'], 'appliance': ['active']},
    'sample_rate': 8,
    'appliances': [],
    'artificial_aggregate': False,
    'DROP_ALL_NANS': True,
    'methods': {

    },
    'train': {
        'datasets': {
            'ukdale': {
                'path': "ukdale.h5",
                'buildings': {
                    1: {
                        'start_time': '2015-01-04',
                        'end_time': '2015-01-15'
                    }
                }
            }
        }
    },
    'test': {
        'datasets': {
            'ukdale': {
                'path': "ukdale.h5",
                'buildings': {
                    1: {
                        'start_time': '2015-04-16',
                        'end_time': '2015-04-30'
                    },
                }
            },

        },
        'metrics': ['mae', 'nde', 'rmse', 'f1score'],
    }

}

ukdale_0 = {'power': {'mains': ['active'], 'appliance': ['active']},
            'sample_rate': 8,
            'appliances': ['coffee maker'],
            'artificial_aggregate': False,
            'DROP_ALL_NANS': True,
            'methods': {},
            'train': {'datasets': {'ukdale': {'path': "ukdale.h5",
                                              'buildings': {
                                                  1: {'start_time': '2013-09-07', 'end_time': '2013-11-13'}}}}},
            'test': {'datasets': {'ukdale': {'path': "ukdale.h5",
                                             'buildings': {1: {'start_time': '2015-04-16',
                                                               'end_time': '2015-05-15'}}}},
                     'metrics': ['mae', 'nde', 'rmse', 'f1score']}}

# ukdale_1 = {'power': {'mains': ['active'], 'appliance': ['active']},
#             'sample_rate': 8,
#             'appliances': ['toaster'],
#             'artificial_aggregate': False,
#             'DROP_ALL_NANS': True,
#             'methods': {},
#             'train': {'datasets': {'ukdale': {'path': None,
#                                               'buildings': {1: {'start_time': '2013-11-13',
#                                                                 'end_time': '2014-02-03'}}}}},
#             'test': {'datasets': {'ukdale': {'path': None,
#                                              'buildings': {1: {'start_time': '2015-04-16',
#                                                                'end_time': '2015-05-15'}}}},
#                      'metrics': ['mae', 'nde', 'rmse', 'f1score']}}

# The dryer can also be integrated in the ukdale but rather here the problem
# is as follows two dryers are connected to the same meter and thus we do not have the
# recording for a single dryer but rather two dryers together.
# In the case of IADL this is not a problem since we are just interested in detecting if the
# the dryer is used or not as part of the laundry activity.
ukdale_1 = {'power': {'mains': ['active'], 'appliance': ['active']},
            'sample_rate': 8,
            'appliances': ['breadmaker',
                           'washing machine',
                           'microwave',
                           'washer dryer'],
            'artificial_aggregate': False,
            'DROP_ALL_NANS': True,
            'methods': {},
            'train': {'datasets': {'ukdale': {'path': "ukdale.h5",
                                              'buildings': {1: {'start_time': '2014-03-17',
                                                                'end_time': '2014-07-21'}}}}},
            'test': {'datasets': {'ukdale': {'path': "ukdale.h5",
                                             'buildings': {1: {'start_time': '2015-04-16',
                                                               'end_time': '2015-05-15'}}}},
                     'metrics': ['mae', 'nde', 'rmse', 'f1score']}}

ukdale_2 = {'power': {'mains': ['active'], 'appliance': ['active']},
            'sample_rate': 8,
            'appliances': ['kettle'],
            'artificial_aggregate': False,
            'DROP_ALL_NANS': True,
            'methods': {},
            'train': {'datasets': {'ukdale': {'path': "ukdale.h5",
                                              'buildings': {1: {'start_time': '2014-08-16',
                                                                'end_time': '2014-10-04'}}}}},
            'test': {'datasets': {'ukdale': {'path': "ukdale.h5",
                                             'buildings': {1: {'start_time': '2015-04-16',
                                                               'end_time': '2015-05-15'}}}},
                     'metrics': ['mae', 'nde', 'rmse', 'f1score']}}

### the boiler do not have recording for teh active power in the ukdale
### but rather contain different measures for the input and the target

ukdale_3 =  {'power': {'mains': ['apparent'], 'appliance': ['active']},
  'sample_rate': 8,
  'appliances': ['boiler'],
  'artificial_aggregate': False,
  'DROP_ALL_NANS': True,
  'methods': {},
  'train': {'datasets': {'ukdale': {'path': "ukdale.h5",
     'buildings': {1: {'start_time': '2015-01-09',
       'end_time': '2015-03-15'}}}}},
  'test': {'datasets': {'ukdale': {'path': "ukdale.h5",
     'buildings': {1: {'start_time': '2015-04-16',
       'end_time': '2015-05-15'}}}},
   'metrics': ['mae', 'nde', 'rmse', 'f1score']}}

ukdale_4 = {'power': {'mains': ['active'], 'appliance': ['active']},
            'sample_rate': 8,
            'appliances': ['computer',
                           'dish washer',
                           'television',
                           'audio amplifier',
                           'oven'],
            'artificial_aggregate': False,
            'DROP_ALL_NANS': True,
            'methods': {},
            'train': {'datasets': {'ukdale': {'path': "ukdale.h5",
                                              'buildings': {1: {'start_time': '2016-04-26',
                                                                'end_time': '2016-07-30'}}}}},
            'test': {'datasets': {'ukdale': {'path': "ukdale.h5",
                                             'buildings': {1: {'start_time': '2015-04-16',
                                                               'end_time': '2015-05-15'}}}},
                     'metrics': ['mae', 'nde', 'rmse', 'f1score']}}
