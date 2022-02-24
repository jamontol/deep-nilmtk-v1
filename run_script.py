from deep_nilmtk.disaggregator import NILMExperiment
import logging
# logging.root.setLevel(logging.NOTSET)

# The following line sets the root logger level as well.
# It's equivalent to both previous statements combined:
# logging.basicConfig(level=logging.NOTSET)

import sys
sys.path.append("..") # Adds higher directory to python modules path.

from deep_nilmtk.utils import setup
from deep_nilmtk.disaggregator import NILMExperiment

max_nb_epochs = 20
sequence_length = 121
nfolds = 1
data_path = 'C:\\Users\\Hafsa\\Documents\\data\\ukdale.h5'
train = True
plot_events = False

# STEP 00: Experiment definition
experiment = {
   'power': {'mains': ['active'],'appliance': ['active']},
   'sample_rate': 8,
   'threshold':{
     'kettle':500,
     'microwave':50,
     'fridge':50,
     'washing machine': 100
   },
   'appliances': [
         'washing machine',
         'kettle',
         'microwave',
         'television'
       ],
   'artificial_aggregate': False,
   'DROP_ALL_NANS': True,
   'methods': {
        'Seq2Pointbaseline':NILMExperiment({
                "model_name": 'Seq2Pointbaseline',
                'backend':'pytorch',
                'in_size': sequence_length,
                'custom_preprocess':None,
                'feature_type':'mains',
                'input_norm':'z-norm',
                'target_norm':'z-norm',
                'seq_type':'seq2point',
                'use_optuna':True,
                'n_trials':30,
                'point_position':'mid_position',
                'learning_rate':10e-5,
                'max_nb_epochs': max_nb_epochs
                }),
   },

   'train': {
     'datasets': {
      'refit': {
         'path': data_path,
         'buildings': {
               1: {
                  'start_time': '2015-01-04',
                  'end_time': '2015-03-30'
           }
         }
      }
     }
   },
     'test': {
     'datasets': {

       'refit': {
         'path': data_path,
         'buildings': {
               1: {
                   'start_time': '2015-04-16',
                   'end_time':  '2015-05-15'
               },
         }
       },

     },
        'metrics':['mae','nde', 'rmse','f1score', 'precision', 'recall'],
     }

}

api_res = setup(experiment,  experiment_name = 'baselines_anp_rnn_2',
                results_path='C:\\Users\\Hafsa\\Documents\\new_dnilm',
                mlflow_repo='file:\\\\\\C:\\Users\\Hafsa\\Documents\\new_dnilm/mlflow/mlruns')


# api_res = setup(experiment,  experiment_name = 'baselines_anp_rnn_2',
#                 results_path='C:\\Users\\Hafsa\\Documents\\new_dnilm',
#                 mlflow_repo='file:\\\\\\C:\\Users\\Hafsa\\Documents\\new_dnilm/mlflow/mlruns')
