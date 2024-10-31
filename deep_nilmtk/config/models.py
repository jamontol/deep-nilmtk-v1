#import deep_nilmtk.models.tensorflow as KerasModels
import deep_nilmtk.models.pytorch as TorchModels

#import deep_nilmtk.data.loader.tensorflow as KerasLoader
import deep_nilmtk.data.loader.pytorch as TorchLoader

# currently not in use:
"""
    'tensorflow': {
        'Seq2Pointbaseline':{
            'model': KerasModels.Seq2Point,
            'loader':None
        }
    }
"""

__models__ = {
    'tensorflow': None,
    'pytorch':{
            # =============================================================================
            #     Baseline models from nilmtk-contrib in pytorch
            # =============================================================================
            'Seq2Pointbaseline': {
                'model': TorchModels.seq2point.Seq2Point,
                'loader': TorchLoader.GeneralDataLoader,
                'extra_params':{
                    'point_position': 'mid_point',
                    'sequence_type':'seq2point'
                }
            },
            'SAED_model':{
                'model': TorchModels.seq2point.SAED,
                'loader': TorchLoader.GeneralDataLoader,
                'extra_params': {
                    'point_position': 'mid_point',
                    'sequence_type': 'seq2point'
                }
            },
            'RNNbaseline': {
                'model': TorchModels.seq2point.RNN,
                'loader': TorchLoader.GeneralDataLoader,
                'extra_params':{'sequence_type': 'seq2point'}
            },

            'WindowGRUbaseline': {
                'model': TorchModels.seq2point.WindowGRU,
                'loader': TorchLoader.GeneralDataLoader,
                'extra_params':{'sequence_type': 'seq2point'}
            },

            'Seq2Seqbaseline':{
                'model': TorchModels.seq2seq.Seq2Seq,
                'loader': TorchLoader.GeneralDataLoader,
                'extra_params':{'sequence_type': 'seq2seq'}
            },

            'BERT4NILM': {
                'model': TorchModels.BERT4NILM,
                'loader': TorchLoader.BERTDataset,
                'extra_params': {'sequence_type': 'seq2point'}
            },

            'DAE':{
                'model': TorchModels.seq2seq.DAE,
                'loader': TorchLoader.GeneralDataLoader,
                'extra_params':{
                    'sequence_type': 'seq2point'}
            },
            'UNET': {
                'model': TorchModels.UNETNILM,
                 'loader': TorchLoader.GeneralDataLoader,
                'extra_params': {'sequence_type': 'seq2point'}
            },
            'UNET_quantile': {
                'model': TorchModels.UNETNILMSeq2Quantile,
                 'loader': TorchLoader.GeneralDataLoader,
                'extra_params': {'sequence_type': 'seq2quantile'}
            }
    }
}