import logging


building_info = {
    'redd': {'fridge': [1,2,3,5,6],
            'washing machine': [1,2,3,4,5,6],
            'dish washer': [1,2,3,4,5,6],
            'microwave': [1,2,3,5]},
    'ukdale':{'fridge': [1,2,4,5],
            'washing machine': [1,2,4,5],
            'dish washer': [1,2,5],
            'microwave': [1,2,5],
            'kettle': [1,2,3,4,5]},
    'hipe': {('motor',1) : [1],
             ('motor',2) : [1],
             ('motor',3) : [1],
             ('motor',4) : [1],
             ('motor',5) : [1],
             ('oven', 1): [1],
             ('oven', 2): [1],
             ('oven', 3): [1],
            'printer': [1],
            'washing machine': [1]}
    }


def check_ds(ds_name, ds, app):
    """
    Remove buildings from used dataset that have
    no recording for the given appliance
    """
    if ds_name in building_info:
        for b in list(ds['buildings'].keys()):
            if b not in building_info[ds_name][app]:
                del ds['buildings'][b]
                logging.warning(f'Removing building [{b}] from [{ds_name}] for this experiment because [{app}] not available.')
        return ds
                
    else:
        logging.warning(f'For dataset {ds_name}, availability of target appliance in buildings was not checked.')
        return ds
    

def check_data(datasets, ds_type, app):
    """
    For each dataset in train/test data, run search whether
    specified buildings have target appliance
    """
    total_buildings = 0
    for ds_name, ds in datasets.items():
        ds_checked = check_ds(ds_name, ds, app)
        datasets[ds_name] = ds_checked
        total_buildings += len(ds['buildings'])
    if total_buildings == 0:
        raise Exception(f'Given building(s) for [{ds_type}] do not have appliance [{app}], no {ds_type} data available.')
    return datasets


def buildings_available(experiment, app):
    """
    Update experiment parameters to only include
    buildings with target appliance
    """
    train_datasets = check_data(experiment['train']['datasets'], 'train', app)
    test_datasets = check_data(experiment['test']['datasets'], 'test', app)
    
    experiment['train']['datasets'] = train_datasets
    experiment['test']['datasets'] = test_datasets
    
    return experiment
    
