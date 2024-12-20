import pandas as pd

from .denormalize import denormalize
from .aggregate import aggregate_mean

def remove_negatives(pred):
    pred[pred<0]=0
    return pred

def postprocess(predictions, type_target, params, aggregate=False, stride=1):
    """
    Post processing function for the predictions
    :param predictions: a 2d np array
    :param hparams: hparameters
    :return: processed energy consumption
    """

    processed_predictions = {
        app: remove_negatives(denormalize(aggregate_mean(predictions[app], stride), type=type_target, params=params[app])).reshape(-1) \
         if aggregate else remove_negatives(denormalize(predictions[app], type=type_target, params=params[app]).reshape(-1) ) for app in predictions
    }
    
    return processed_predictions


def bert_postprocess(predictions, aggregate=False, stride=1):
    """
    Post processing function for the predictions
    of BERT4NILM, skips denormalization because that already happens
    in the BERT4NILM class
    :param predictions: a 2d np array
    :param hparams: hparameters
    :return: processed energy consumption
    """

    processed_predictions = {
        app: remove_negatives(aggregate_mean(predictions[app], stride)).reshape(-1) \
         if aggregate else remove_negatives(predictions[app]).reshape(-1) for app in predictions
    }
    
    return processed_predictions
