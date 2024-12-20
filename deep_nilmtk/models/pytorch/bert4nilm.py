# The original code was taken from the
# the repo: https://github.com/Yueeeeeeee/BERT4NILM/
# Paper Link: https://dl.acm.org/doi/pdf/10.1145/3427771.3429390

import math
import torch
from torch import nn
import torch.nn.functional as F

from tqdm import tqdm
import sys

import pandas as pd

import deep_nilmtk.data.loader.pytorch as TorchLoader
from deep_nilmtk.data.pre_process import bert_preprocess
from deep_nilmtk.data.post_process import bert_postprocess

from .layers import create_linear, create_conv1, create_deconv1

from torch.nn import TransformerEncoderLayer

import math
import torch
from torch import nn
import torch.nn.functional as F


class GELU(nn.Module):
    def forward(self, x):
        return 0.5 * x * (1 + torch.tanh(math.sqrt(2 / math.pi) * (x + 0.044715 * torch.pow(x, 3))))


class PositionalEmbedding(nn.Module):
    def __init__(self, max_len, d_model):
        super().__init__()
        self.pe = nn.Embedding(max_len, d_model)

    def forward(self, x):
        batch_size = x.size(0)
        return self.pe.weight.unsqueeze(0).repeat(batch_size, 1, 1)


class LayerNorm(nn.Module):
    def __init__(self, features, eps=1e-6):
        super(LayerNorm, self).__init__()
        self.weight = nn.Parameter(torch.ones(features))
        self.bias = nn.Parameter(torch.zeros(features))
        self.eps = eps

    def forward(self, x):
        mean = x.mean(-1, keepdim=True)
        std = x.std(-1, keepdim=True)
        return self.weight * (x - mean) / (std + self.eps) + self.bias


class Attention(nn.Module):
    def forward(self, query, key, value, mask=None, dropout=None):
        scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(query.size(-1))
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        p_attn = F.softmax(scores, dim=-1)
        if dropout is not None:
            p_attn = dropout(p_attn)

        return torch.matmul(p_attn, value), p_attn


class MultiHeadedAttention(nn.Module):
    def __init__(self, h, d_model, dropout=0.1):
        super().__init__()
        assert d_model % h == 0

        self.d_k = d_model // h
        self.h = h

        self.linear_layers = nn.ModuleList([nn.Linear(d_model, d_model) for _ in range(3)])
        self.output_linear = nn.Linear(d_model, d_model)
        self.attention = Attention()

        self.dropout = nn.Dropout(p=dropout)

    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)

        query, key, value = [l(x).view(batch_size, -1, self.h, self.d_k).transpose(1, 2)
                             for l, x in zip(self.linear_layers, (query, key, value))]

        x, attn = self.attention(
            query, key, value, mask=mask, dropout=self.dropout)

        x = x.transpose(1, 2).contiguous().view(
            batch_size, -1, self.h * self.d_k)

        return self.output_linear(x)


class PositionwiseFeedForward(nn.Module):
    def __init__(self, d_model, d_ff):
        super(PositionwiseFeedForward, self).__init__()
        self.w_1 = nn.Linear(d_model, d_ff)
        self.w_2 = nn.Linear(d_ff, d_model)
        self.activation = GELU()

    def forward(self, x):
        return self.w_2(self.activation(self.w_1(x)))


class SublayerConnection(nn.Module):
    def __init__(self, size, dropout):
        super(SublayerConnection, self).__init__()
        self.layer_norm = LayerNorm(size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, sublayer):
        return self.layer_norm(x + self.dropout(sublayer(x)))


class TransformerBlock(nn.Module):
    def __init__(self, hidden, attn_heads, feed_forward_hidden, dropout):
        super().__init__()
        self.attention = MultiHeadedAttention(
            h=attn_heads, d_model=hidden, dropout=dropout)
        self.feed_forward = PositionwiseFeedForward(
            d_model=hidden, d_ff=feed_forward_hidden)
        self.input_sublayer = SublayerConnection(size=hidden, dropout=dropout)
        self.output_sublayer = SublayerConnection(size=hidden, dropout=dropout)
        self.dropout = nn.Dropout(p=dropout)

    def forward(self, x, mask):
        x = self.input_sublayer(
            x, lambda _x: self.attention.forward(_x, _x, _x, mask=mask))
        x = self.output_sublayer(x, self.feed_forward)
        return self.dropout(x)

class BERT4NILM(nn.Module):
    """
    .. _bert:
    BERT4NILM implementation.
    Original paper can be found here: https://dl.acm.org/doi/pdf/10.1145/3427771.3429390
    Original code can be found here: https://github.com/Yueeeeeeee/BERT4NILM
    The hyperparameter dictionnary is expected to include the following parameters

    :param threshold:  The threshold for states generation in the target power consumption, defaults to None
    :type threshold: List of floats
    :param cutoff: The cutoff for states generation in the target power consumption, defaults to None
    :type cutoff: List of floats
    :param min_on: The min on duration for states generation in the target power consumption, defaults to None
    :type min_on: List of floats
    :param min_off: The min off duration for states generation in the target power consumption, defaults to None
    :type min_off: List of floats
    :param in_size: The length of the input sequence, defaults to 488.
    :type in_size: int
    :param stride: The distance between two consecutive sequences, defaults to 1.
    :type stride: int
    :param hidden: The hidden size, defaults to 256
    :type hidden: int
    :param heads: The number of attention heads in each transformer block, defaults to 2
    :type heads: int
    :param n_layers: the number of transformer blocks in the model, defaults to 2
    :type n_layers: int
    :params dropout: The dropout, defaults to 0.2
    :type dropout: float
    it can be used as follow:
    .. code-block:: python
        'Bert4NILM': NILMExperiment({
                  "model_name": 'BERT4NILM',
                  'in_size': 480,
                  'feature_type':'main',
                  'stride':10,
                  'max_nb_epochs':1,
                  'cutoff':{
                      'aggregate': 6000,
                      'kettle': 3100,
                      'fridge': 300,
                      'washing machine': 2500,
                      'microwave': 3000,
                      'dishwasher': 2500
                  },
                  'threshold':{
                     'kettle': 2000,
                     'fridge': 50,
                     'washing machine': 20,
                     'microwave': 200,
                     'dishwasher': 10
                  },
                  'min_on':{
                    'kettle': 2,
                    'fridge': 10,
                    'washing machine': 300,
                    'microwave': 2,
                    'dishwasher': 300
                  },
                  'min_off':{
                      'kettle': 0,
                      'fridge': 2,
                      'washing machine': 26,
                      'microwave': 5,
                      'dishwasher': 300
                  },
                })
    """

    def __init__(self, params):

        super().__init__()

        self.original_len = params['in_size'] if 'in_size' in params else 480
        self.output_size = len(params['appliances']) if 'appliances' in params else 1
        self.stride = params['stride'] if 'stride' in params else 1
                
        # The original mode was proposed for several appliances
        self.threshold = [params['threshold']] if 'threshold' in params else None

        self.cutoff = [params['cutoff']] if 'cutoff' in params else None

        self.min_on = [params['min_on']] if 'min_on' in params else None
        self.min_off = [params['min_off']] if 'min_off' in params else None

        # self.C0 = [params['lambda'][params['appliances'][0]]] if 'lambda' in params else [1e-6]

        self.main_mu = params['main_mu']   # not used
        self.main_std = params['main_std'] # not used

        self.set_hpramas(self.cutoff, self.threshold, self.min_on, self.min_off)

        self.C0 = torch.tensor([params['c0'] if 'c0' in params else .3])

        self.latent_len = int(self.original_len / 2)
        self.dropout_rate = params['dropout'] if 'dropout' in params else 0.1

        self.hidden = params['hidden'] if 'hidden' in params else 256
        self.heads = params['heads'] if 'heads' in params else 2
        self.n_layers = params['n_layers'] if 'n_layers' in params else 2

        self.conv = create_conv1(in_channels=1, out_channels=self.hidden,
                                 kernel_size=5, stride=1, padding=2, padding_mode='replicate')

        self.pool = nn.LPPool1d(norm_type=2, kernel_size=2, stride=2)

        self.position = PositionalEmbedding(
            max_len=self.latent_len, d_model=self.hidden)
        self.layer_norm = LayerNorm(self.hidden)
        self.dropout = nn.Dropout(p=self.dropout_rate)



        self.transformer_blocks = nn.ModuleList([TransformerBlock(
            self.hidden, self.heads, self.hidden * 4, self.dropout_rate) for _ in range(self.n_layers)])

        self.deconv = create_deconv1(
            in_channels=self.hidden, out_channels=self.hidden, kernel_size=4, stride=2, padding=1,
            output_padding=0 if self.original_len % 2 == 0 else 1)
        self.linear1 = create_linear(self.hidden, 128)
        self.linear2 = create_linear(128, self.output_size)
        
        self.truncated_normal_init()

        #self.activation = nn.Sigmoid()

        self.kl = nn.KLDivLoss(reduction='batchmean')
        self.mse = nn.MSELoss()
        self.mae = nn.L1Loss(reduction='mean')
        self.margin = nn.SoftMarginLoss()
        self.l1_on = nn.L1Loss(reduction='sum')
    
    def truncated_normal_init(self, mean=0, std=0.02, lower=-0.04, upper=0.04):
        params = list(self.named_parameters())
        for n, p in params:
            if 'layer_norm' in n:
                continue
            else:
                with torch.no_grad():
                    l = (1. + math.erf(((lower - mean) / std) / math.sqrt(2.))) / 2.
                    u = (1. + math.erf(((upper - mean) / std) / math.sqrt(2.))) / 2.
                    p.uniform_(2 * l - 1, 2 * u - 1)
                    p.erfinv_()
                    p.mul_(std * math.sqrt(2.))
                    p.add_(mean)

    def forward(self, sequence):
        x_token = self.pool(self.conv(sequence.float().unsqueeze(1))).permute(0, 2, 1)

        embedding = x_token + self.position(sequence)
        x = self.dropout(self.layer_norm(embedding))

        mask = None
        for transformer in self.transformer_blocks:
            x = transformer.forward(x, mask)

        x = self.deconv(x.permute(0, 2, 1)).permute(0, 2, 1)
        x = torch.tanh(self.linear1(x))
        x = self.linear2(x)

        return x

    def step(self, batch, seq_type=None):
        """Disaggregates a batch of data
        :param batch: A batch of data.
        :type batch: Tensor
        :return: loss function as returned form the model and MAE as returned from the model.
        :rtype: tuple(float,float)
        """
        seqs, labels_energy, status = batch

        batch_shape = status.shape

        logits = self.forward(seqs).float()

        labels = (labels_energy / self.cutoff.to(seqs.device)).float()  # normalization of target data

        logits_energy = self.cutoff_energy(logits * self.cutoff.to(seqs.device)).float() # denormalization of predictions
        logits_status = self.compute_status(logits_energy).float()
        
        mask = (status >= 0)
        labels_masked = torch.masked_select(labels, mask).view((-1, batch_shape[-1]))
        logits_masked = torch.masked_select(logits, mask).view((-1, batch_shape[-1]))
        status_masked = torch.masked_select(status, mask).view((-1, batch_shape[-1]))
        logits_status_masked = torch.masked_select(logits_status, mask).view((-1, batch_shape[-1]))

        # Calculating the loss function on normalized targets and predictions but only for masked positions
        kl_loss = self.kl(torch.log(F.softmax(logits_masked.squeeze() / 0.1, dim=-1) + 1e-9),
                          F.softmax(labels_masked.squeeze() / 0.1, dim=-1))
        # print(f'margin:{kl_loss}')
        mse_loss = self.mse(logits_masked.contiguous().view(-1),
                            labels_masked.contiguous().view(-1))
        # print(f'margin:{mse_loss}')
        margin_loss = self.margin((logits_status_masked * 2 - 1).contiguous().view(-1),
                                  (status_masked * 2 - 1).contiguous().view(-1))
        # print(f'margin:{margin_loss}')
        total_loss = kl_loss + mse_loss + margin_loss
        on_mask = (status >= 0) * (((status == 1) + (status != logits_status)) >= 1)
        if on_mask.sum() > 0:
            total_size = torch.tensor(on_mask.shape).prod()
            logits_on = torch.masked_select(logits.reshape(on_mask.shape), on_mask)
            labels_on = torch.masked_select(labels.reshape(on_mask.shape), on_mask)
            loss_l1_on = self.l1_on(logits_on.contiguous().view(-1),
                                    labels_on.contiguous().view(-1))
            total_loss += self.C0.to(seqs.device)[0] * loss_l1_on / total_size

        # mean absolute error computed on all predictions
        mae = self.mae(logits.contiguous().view(-1),
                       labels.contiguous().view(-1))
        # print(total_loss)
        return total_loss, mae

    def set_hpramas(self, cutoff, threshold, min_on, min_off):
        """
        Setter for the hyper-parameters related to appliance state generation
        :param cutoff: The power cutoff
        :type cutoff: float
        :param threshold: Threshold of target power consumption
        :type threshold: float
        :param min_on: Minimum on duration
        :type min_on: float
        :param min_off: Minimum off duration
        :type min_off: float
        """
        if cutoff is not None:
            self.cutoff = torch.tensor(cutoff)
        if threshold is not None:
            self.threshold = torch.tensor(threshold)
        if min_on is not None:
            self.min_on = torch.tensor(min_on)
        if min_off is not None:
            self.min_off = torch.tensor(min_off)

    def cutoff_energy(self, data):
        """
        Removes the spikes from the data
        :param data: Power consumption
        :type data: tesnor
        :return: Updated ower consumption
        :rtype: tensor
        """
        columns = data.squeeze().shape[-1]

        # if no cutoff is specified
        if self.cutoff.size(0) == 0:
            self.cutoff = torch.tensor(
                [3100 for i in range(columns)])

        data[data < 5] = 0

        data = torch.min(data, self.cutoff.to(data.device))
        return data

    def compute_status(self, data):
        """
        Calculates the states for the  target data based on the threshold
        :param data: The target data
        :type data: tensor
        :return: The operational states
        :rtype: tensor
        """
        data_shape = data.shape
        columns = data.shape[-1]

        # if no threshold is specified
        if self.threshold.size(0) == 0:
            self.threshold = torch.tensor(
                [10 for i in range(columns)])

        status = (data >= self.threshold.to(data.device)) * 1

        return status

    def predict(self, model, test_dataloader):
        """Generates predictions for the test data loader
        :param model: Pre-trained model
        :type model: nn.Module
        :param test_dataloader: The test data
        :type test_dataloader: dataLoader
        :return: Generated predictions
        :rtype: dict
        """

        net = model.model.eval()
        num_batches = len(test_dataloader)
        values = range(num_batches)

        pred = []

        # energy and status predictions
        e_pred_curve = []
        s_pred_curve = []

        true = []

        with tqdm(total=len(values), file=sys.stdout) as pbar:
            with torch.no_grad():
                for batch_idx, batch in enumerate(test_dataloader):
                    seqs = batch

                    logits = self.forward(seqs)

                    true.append(seqs)

                    logits_energy = self.cutoff_energy(logits * self.cutoff.to(seqs.device))  # denormalization of predictions
                    logits_status = self.compute_status(logits_energy)
                    logits_energy = logits_energy * logits_status

                    # predicted status
                    status = (logits_status > 0) * 1

                    s_pred_curve.append(status)
                    e_pred_curve.append(logits_energy)

                    del batch
                    pbar.set_description('processed: %d' % (1 + batch_idx))
                    pbar.update(1)

                pbar.close()

        e_pred_curve = torch.cat(e_pred_curve, 0).detach()
        s_pred_curve = torch.cat(s_pred_curve, 0).detach()
    
        results = {
            "pred": e_pred_curve,
            "s_pred_curve": s_pred_curve
        }

        return results
    
    """
    def compute_custom_f1(pred_list):
        TODO: should compute f1 using the status predictions
        which have been cutoff by specified appliance thresholds
        (logits_status)
    """ 

    @staticmethod
    def suggest_hparams(trial):
        """
        Function returning list of params that will be suggested from optuna

        :param trial: Optuna Trial.
        :type trial: optuna.trial
        :return: Parameters with values suggested by optuna
        :rtype: dict
        """

        window_length = trial.suggest_int('in_size', low=128, high=480)
        learning_rate = trial.suggest_float('learning_rate', low=1e-6, high=1e-3)
        batch_size = trial.suggest_int('batch_size', low=32, high=128, step=32)
        latent_size = trial.suggest_int('latent_size', low=512, high=2028, step=512)
        #feature_type = trial.suggest_categorical('feature_type', ['mains', 'combined'])
        input_norm = trial.suggest_categorical('input_norm', ['z-norm', 'minmax', 'lognorm' ])
        target_norm = trial.suggest_categorical('target_norm', ['z-norm', 'minmax', 'lognorm'])


        return {
            'in_size': window_length,
            'latent_size':latent_size,
            'batch_size': batch_size,
            # 'feature_type': feature_type,
            'input_norm': input_norm,
            'target_norm': target_norm,
            'learning_rate': learning_rate,

        }  
        
    @staticmethod
    def get_template():
        return {
            'backend': 'pytorch',
            'model_name': 'BERT4NILM',
            # 'in_size': sequence_length,
            'out_size': 1,
            'feature_type': 'mains',
            'loader_class': TorchLoader.BERTDataset,
            'target_norm': 'z-norm',
            'seq_type': 'seq2point',
            'learning_rate': 10e-5,
            'point_position': 'mid_position',
            'custom_preprocess': 'bert_preprocess',
            'custom_postprocess': 'bert_postprocess',

            'in_size': 99, #480,
            'latent_size': 1024,
            'batch_size': 64,
            'input_norm': 'z-norm',
            'target_norm': 'z-norm'

        }

