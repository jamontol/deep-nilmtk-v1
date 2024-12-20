
import torch.nn as nn
import torch.nn.functional as F

from tqdm import tqdm
import sys
from .layers import  create_conv1,  create_linear

import torch
import numpy as np

from collections import OrderedDict

from deep_nilmtk.data.post_process import denormalize, aggregate_seq
# =============================================================================
# Sequence-to-Sequence models
# =============================================================================

class S2S(nn.Module):
    """
    This class is an abstract class  for Sequence to Sequence models. By implementing this class,
    you can avoid to implement the predict and the forward functions.

    :param params: dictionnary of values relative to hyper-parameters.
    :type params: dict

    The dictionnay is expected to include the following keys:

    :param target_norm: the type of normlization of the target power, defaults to 'z-norm'.
    :type target_norm: str.
    :param mean: The mean consumption value of the target appliance, defaults to 0.
    :type mean: float.
    :param std: The std consumption value  the target power, defaults to 1
    :type std: float.
    :param min: The mininum consumption value of the target appliance, defaults to 0.
    :type min: float.
    :param max: The maximum consumption value  the target power, defaults to 1
    :type max: float.

    """

    def __init__(self,params):
        """
        Initialise the NILM model

        Parameters
        ----------
            params (dict): dictionnary of values relative to hyper-parameters.

        """
        super(S2S, self).__init__()

        self.original_len = params['in_size']  if 'in_size' in params else 99
        self.original_len += params['out_size'] if 'out_size' in params else 0
        #self.original_len += params['out_size']  if 'out_size' in params else 0
        self.target_norm = params['target_norm'] if 'target_norm' in params else 'z-norm'
        self.mean = params['mean'] if 'mean' in params else 0
        self.std = params['std'] if 'std' in params else 1

        self.min = params['min'] if 'min' in params else 0
        self.max = params['max'] if 'max' in params else 1

    def step(self, batch):
        """Disaggregates a batch of data

        :param batch: A batch of data.
        :type batch: Tensor
        :return: loss function as returned form the model and MAE as returned from the model.
        :rtype: tuple(float,float)
        """


        x, y  = batch
        out   = self(x)  # BxCxT


        error = (y - out)
        loss = F.mse_loss(out, y)
        mae = error.abs().data.mean()
        # mae = loss
        return  loss, mae

    def predict(self,  model, test_dataloader):
        """Generate prediction during testing for the test_dataLoader

        :param model: pre-trained model.
        :param test_dataloader: data loader for the testing period.

        :return: data loader for the testing period.
        :rtype: tensor
        """

        net = model.model.eval()
        num_batches = len(test_dataloader)
        values = range(num_batches)

        pred = []
        true = []

        with tqdm(total = len(values), file=sys.stdout) as pbar:
            with torch.no_grad():
                for batch_idx, batch in enumerate(test_dataloader):
                    if len(batch)==2:
                        x, y  = batch
                        out = net(x)
                        pred.append(out)
                        true.append(y)
                    else:
                        x  = batch
                        out = net(x)
                        pred.append(out)
                    del  batch
                    pbar.set_description('processed: %d' % (1 + batch_idx))
                    pbar.update(1)

                pbar.close()
        pred = torch.cat(pred, 0).detach().numpy()
        # Perform denormalisation here

        results = {"pred":pred[self.original_len // 2:]}

        return results

    @staticmethod
    def suggest_hparams( trial):
        """
        Function returning list of params that will be suggested from optuna

        :param trial: Optuna Trial.
        :type trial: optuna.trial
        :return: Parameters with values suggested by optuna
        :rtype: dict
        """

        in_size = trial.suggest_int('in_size', low=99, high=480)
        in_size += 1 if in_size % 2 == 0 else 0
        learning_rate = trial.suggest_float('learning_rate', low=1e-6, high=1e-3)
        batch_size = trial.suggest_int('batch_size', low=32, high=128, step=32)
        latent_size = trial.suggest_int('latent_size', low=512, high=2028, step=512)
        #feature_type = trial.suggest_categorical('feature_type', ['mains', 'combined'])
        input_norm = trial.suggest_categorical('input_norm', ['z-norm', 'minmax', 'lognorm'])
        target_norm = trial.suggest_categorical('target_norm', ['z-norm', 'minmax', 'lognorm'])

        return {
            'in_size': in_size,
            'out_size': in_size,
            'latent_size':latent_size,
            'learning_rate': learning_rate,
            'batch_size': batch_size,
            #'feature_type': feature_type,
            'input_norm': input_norm,
            'target_norm': target_norm
        }


    @staticmethod
    def get_template():
        return  {
                'backend': 'pytorch',
                'custom_preprocess': None,
                'feature_type': 'mains',
                'input_norm': 'z-norm',
                'target_norm': 'z-norm',
                'seq_type': 'seq2seq',
                'learning_rate': 10e-5,

                'in_size': 99,
                'out_size': 99,
                'latent_size': 1024,
                'batch_size': 64,

                # 'max_nb_epochs': max_nb_epochs
            }


class Seq2Seq(S2S):
    """
        .. _seqseq:

        PyTorch implementation of the Window-GRU
        NILM model as porposed in :
        https://dl.acm.org/doi/pdf/10.1145/3360322.3360844

        :param params: dictionnary of values relative to hyper-parameters.
        :type params: dict

        Besides the additional paramter from teh parent model, the params dictionnay is expected to include the following keys:

        :param feature_type: The number of input features, defaults to 1.
        :type feature_type: int
        :param appliances: A list of appliances.
        :type appliances: list of str
        :param pool_filter: The size of pooling filter, defaults to 50.
        :type pool_filter: int

        :param latent_size: The number of nodes in the last layer, defaults to 1024.
        :type latent_size: int
    """
    def __init__(self, params):

        super(Seq2Seq, self).__init__(params)

        in_size=4 if params['feature_type']=="combined" else 1 #4 if params['feature_type']=="combined" else 1
        output_size = len(params['appliances']) if 'appliances' in params else 1

        pool_filter= params['pool_filter'] if 'pool_filter' in params else 8
        latent_size=params['latent_size'] if 'latent_size' in params else 1024
        seq_len = params['in_size'] if 'in_size' in params else 99

        self.pool_filter = pool_filter
        self.out_dim = output_size
        self.enc_net = nn.Sequential(create_conv1(in_size, 30, 10, bias=True, stride=2),
                                     nn.ReLU(),
                                     create_conv1(30, 30, 8, bias=True, stride=2),
                                     nn.ReLU(),
                                     create_conv1(30, 40, 6, bias=True, stride=1),
                                     nn.ReLU(),
                                     create_conv1(40, 50, 5, bias=True, stride=1),
                                     nn.ReLU(),
                                     nn.Dropout(0.2),
                                     create_conv1(50, 50, 5, bias=True, stride=1),
                                     nn.ReLU(),
                                     nn.AdaptiveAvgPool1d(self.pool_filter),
                                     nn.Flatten()
                                     )
        self.fc = nn.Sequential(create_linear(50*pool_filter, latent_size),

                                nn.Dropout(0.2),
                                nn.Linear(latent_size, output_size*seq_len))


    def forward(self, x):
        if x.ndim!=3:
            x = torch.unsqueeze(x, 1)
        else:
            x = x.permute(0,2,1)
        x = self.enc_net(x)
        x = self.fc(x).reshape(x.size(0), -1, self.out_dim)
        x = F.softplus(x) if self.target_norm =='lognorm' else F.relu(x)
        return x

    @staticmethod
    def get_template():
        params = S2S.get_template()
        params.update({
            'model_name': 'Seq2Seqbaseline',
        })
        return params


class DAE(S2S):
    """
        .. _dae:
        PyTorch implementation of the DAE
        NILM model as porposed in :
        https://dl.acm.org/doi/pdf/10.1145/3360322.3360844

        :param params: dictionnary of values relative to hyper-parameters.
        :type params: dict

        Besides the additional paramter from teh parent model, the params dictionnay is expected to include the following keys:

        :param feature_type: The number of input features, defaults to 1.
        :type feature_type: int
        :param appliances: A list of appliances.
        :type appliances: list of str
        :param pool_filter: The size of pooling filter, defaults to 50.
        :type pool_filter: int

        :param latent_size: The number of nodes in the last layer, defaults to 1024.
        :type latent_size: int
    """

    def __init__(self, params):


        super(DAE, self).__init__(params)

        self.input_features = 4 if params['feature_type']=="combined" else 1
        self.sequence_length = params['in_size'] if 'in_size' in params else 99
        self.n_appliances = len(params['appliances']) if 'appliances' in params else 1
        self.output_size = len(params['appliances']) if 'appliances' in params else 1
        self.net = nn.Sequential(OrderedDict([
            ('conv1', nn.Conv1d(
                in_channels = self.input_features,
                out_channels = 8,
                kernel_size = 4,
                stride = 1
            )),
            ('flatten', nn.Flatten()),
            ('Linear1', nn.Linear(
                in_features = self.sequence_length * 8,
                out_features= self.sequence_length * 8
            )),
            ('relu1', nn.ReLU()),
            ('Linear2', nn.Linear(
                in_features = self.sequence_length * 8,
                out_features= 128
            )),
            ('relu2', nn.ReLU()),
            ('Linear3', nn.Linear(
                in_features = 128,
                out_features= self.sequence_length * 8
            )),
            ('relu3', nn.ReLU())]))
        self.output_layer = nn.Conv1d(
            in_channels = 8,
            out_channels = self.n_appliances,
            kernel_size = 4,
            stride = 1
        )

    def forward(self,x):

        y_pred = nn.functional.pad(x.permute(0,2,1), (2,1))

        y_pred =self.net(y_pred)
        y_pred = torch.reshape(y_pred, (-1,8,self.sequence_length))

        y_pred = self.output_layer(nn.functional.pad(y_pred, (2,1)))
        if self.target_norm =='lognorm' :
            x = F.softplus(x)
        elif self.target_norm =='min-max':
            F.relu(x)
        return y_pred

    @staticmethod
    def get_template():
        params = S2S.get_template()
        params.update({
            'model_name': 'DAE',
        })
        return params