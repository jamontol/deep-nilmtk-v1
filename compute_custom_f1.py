from argparse import ArgumentParser
import pickle
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from nilmtk.losses import *
from deep_nilmtk.utils.templates.baseline_templates.redd_template import redd_acts_from_paper, redd_acts_from_repo
from deep_nilmtk.utils.templates.baseline_templates.ukdale_template import uk_dale_acts_from_paper, uk_dale_acts_from_repo

parser = ArgumentParser(add_help=False)
parser.add_argument('--pred_file', type=str)
parser.add_argument('--appliance', type=str)
parser.add_argument('--ds', type=str)
parser.add_argument('--params_type', type=str)
args = parser.parse_args()


with open(args.pred_file, 'rb') as f:
    pred_dict = pickle.load(f)

metrics = {}

# parse existing error metrics
for error_key, error in zip(pred_dict['error_keys'], pred_dict['errors']):
    metrics[error_key] = error.loc[args.appliance].values[0]

gt = pred_dict['gt'][args.appliance].values
predictions = list(pred_dict['predictions'].values())[0][args.appliance].values
timestamps = list(pred_dict['predictions'].values())[0].index

print(f'Size of test set: {len(gt)}')

# re-compute existing metrics for comparsion
metrics_recomputed = {}
test_setting = None
for m_long in metrics.keys():
    m_parts = m_long.split('_')
    test_setting = '_'.join(m_parts[:2])
    m = m_parts[2:]
    if len(m) == 1:
        m = m[0]
    else:
        m = '_'.join(m)
    metric_fn = globals()[m]
    metrics_recomputed[m_long] = metric_fn(gt, predictions)

def get_activation_params(appliance, params_type, ds):
    if params_type == 'paper':
        if ds == 'redd':
            d = redd_acts_from_paper
        elif ds == 'uk_dale':
            d = uk_dale_acts_from_paper
    elif params_type == 'repo':
        if ds == 'redd':
            d = redd_acts_from_repo
        elif ds == 'uk_dale':
            d = uk_dale_acts_from_repo
    d = d['app_activation_params']
    return d['threshold'][appliance], d['min_off'][appliance], d['min_on'][appliance]
    
def compute_pred_status(pred, appliance, params_type, ds):
    pred = np.array(pred)
    threshold, _, _ = get_activation_params(appliance, params_type, ds)
    status = (pred >= threshold) * 1
    return status

def compute_gt_status(gt, appliance, params_type, ds):
    gt = np.array(gt)
    threshold, min_off, min_on = get_activation_params(appliance, params_type, ds)
    initial_status = gt >= threshold
    status_diff = np.diff(initial_status)
    events_idx = status_diff.nonzero()

    events_idx = np.array(events_idx).squeeze()
    events_idx += 1

    if initial_status[0]:
        events_idx = np.insert(events_idx, 0, 0)

    if initial_status[-1]:
        events_idx = np.insert(
            events_idx, events_idx.size, initial_status.size)

    events_idx = events_idx.reshape((-1, 2))
    on_events = events_idx[:, 0].copy()
    off_events = events_idx[:, 1].copy()
    assert len(on_events) == len(off_events)

    if len(on_events) > 0:
        off_duration = on_events[1:] - off_events[:-1]
        off_duration = np.insert(off_duration, 0, 1000)
        on_events = on_events[off_duration > min_off]
        off_events = off_events[np.roll(
            off_duration, -1) > min_off]

        on_duration = off_events - on_events
        on_events = on_events[on_duration >= min_on]
        off_events = off_events[on_duration >= min_on]
        assert len(on_events) == len(off_events)

    status = gt.copy()
    status[:] = 0
    for on, off in zip(on_events, off_events):
        status[on: off] = 1

    return status

status_gt = compute_gt_status(gt, args.appliance, args.params_type, args.ds)
status_predictions = compute_pred_status(predictions, args.appliance, args.params_type, args.ds)

naive_status_gt = np.where(np.array(gt) < 10, 0, 1)
naive_status_predictions = np.where(np.array(predictions) < 10, 0, 1)
precision_naive = precision_score(naive_status_gt, naive_status_predictions)
recall_naive = recall_score(naive_status_gt, naive_status_predictions)

f1_with_custom_status = f1_score(status_gt, status_predictions)
precision_with_custom_status = precision_score(status_gt, status_predictions)
recall_with_custom_status = recall_score(status_gt, status_predictions)

print('ORIGINAL')
print(f'f1: {metrics[test_setting + "_f1score"]}')
print(f'precision: {precision_naive} (how many detected activations were correct)')
print(f'recall: {recall_naive} (how many activations were detected')

print('-------\nCUSTOM')
print(f'f1: {f1_with_custom_status}')
print(f'precision: {precision_with_custom_status} (how many detected activations were correct)')
print(f'recall: {recall_with_custom_status} (how many activations were detected')


plt.plot(timestamps, status_gt, label='status_gt')
plt.plot(timestamps, -1 * status_predictions, label='status_predictions')
plt.legend()
plt.show()

plt.plot(timestamps, naive_status_gt, label='naive_status_gt')
plt.plot(timestamps, -1 * naive_status_predictions, label='naive_status_predictions')
plt.legend()
plt.show()

plt.plot(timestamps, gt, label='gt')
plt.plot(timestamps, -1 * predictions, label='predictions')
plt.legend()
plt.show()

# rest, no needed for now
"""
train_mains_list = pred_dict['train_mains']
print(f'train_mains is list of dataframes:')
for df in train_mains_list:
    print(len(df))
    
test_mains_list = pred_dict['test_mains']
print(f'test_mains is df of length:')
for df in test_mains_list:
    print(len(df))
    
train_submeters_list = pred_dict['train_submeters'][0][1] # access dataframe of first submeter tuple
print(f'train_submeters is list of dataframes:')
for df in train_submeters_list:
    print(len(df))

test_submeters = pred_dict['test_submeters'][0][1][0] # access dataframe in list of first submeter tuple
print(f'test_submeters is df of length: {len(test_submeters)}')
"""