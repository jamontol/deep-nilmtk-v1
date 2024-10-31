

import logging

import pandas as pd

from .utils.cross_validator import CrossValidator
from .utils.hparams_optimizer import HparamsOptimiser
from deep_nilmtk.config.models import __models__
from deep_nilmtk.data.pre_process.normalize import normalize
import numpy as np
from deep_nilmtk.data.post_process import aggregate_mean
import mlflow
import torch

import os

class Trainer:

    def __init__(self, imp, hparams):
        self.hparams = {}
        self.hparams.update(hparams)
        self.trainer_imp = imp
        self.model_class = self.hparams['model_class']  if  hparams['model_class'] else __models__[self.hparams['backend']][self.hparams['model_name']]['model']
        self.loader_class = self.hparams['loader_class']  if hparams['loader_class'] else None
        self.appliances = []
        self.models = {}
        self.appliance_params = {}
        self.run_id = {}

    def get_dataset(self, main, submain, seq_type,
                    in_size, out_size, point_position,
                    target_norm, quantiles= [0.1, 0.25, 0.5, 0.75, 0.90],  loader= None, hparams=None):
        """
        return the datset according the params specified and the DL backend used for training
        :param main: the aggregate power (normalized)
        :param submain: the target power (not normalized)
        :param seq_type: the type of the sequence
        :param in_size: the input sequence length
        :param out_size: the output sequence length
        :param point_position:  the point position in the case of the seq2point
        :param target_norm: the type of target normalization
        :param quantiles: the quantiles in the case of seq2quantile
        :param loader: the loader class in the case of custom loaders
        :param kwargs:
        :return: sequences generator and the normalization's params
        """
        submain_norm = submain.copy()
        params = {}
        
        # target normalisation (not necessary for BERT4NILM)
        if loader is None:
            # if a custom loader is used this part is left to the developer
            # since some models require state generation which can only be done using the
            # target power before normalization
            new_params, submain_norm = normalize(submain.values, target_norm)

        dataset, loader_params = self.trainer_imp.get_dataset(main, submain_norm, seq_type, in_size, out_size,
                                   point_position, target_norm, quantiles, loader=self.loader_class, hparams= hparams if hparams is not None else self.hparams)

        params = new_params if not loader else loader_params

        return dataset, params


    def fit(self, mains, submains):
        # Models initialization
        if len(self.models) == 0:
            self.appliances = list(submains.columns)
            logging.info(f"The list of appliances is : {self.appliances}")
            self.init_models()

        # (Re)-training the models for each appliance
        if self.hparams['use_optuna']:
            # hyper-parameters optimisation
            self.fit_hparams(mains, submains)
            return self.models, self.appliance_params
        elif self.hparams['kfolds'] > 1:
            # cross-validation
            self.fit_cv(mains, submains)
            return self.models, self.appliance_params

        for appliance_name in submains.columns:
            # normal training of the model
            # select experiment if it does not exist create it
            # an experiment is created for each appliance
            if isinstance(appliance_name, tuple):
                appliance_instance_name=appliance_name[0]+'_'+str(appliance_name[1])
            else:
                appliance_instance_name = appliance_name
                
            mlflow.set_experiment(appliance_instance_name)

            power = submains[appliance_name]
            dataset, params = self.get_dataset(mains, power, seq_type=self.hparams['seq_type'],
                                               target_norm=self.hparams['target_norm'],
                                                   in_size=self.hparams['in_size'],
                                                   out_size=self.hparams['out_size'],
                                                   point_position=self.hparams['point_position'], loader=self.loader_class, hparams={**self.hparams, **{'appliances':[appliance_name]}})
            with mlflow.start_run(run_name=self.hparams['model_name']):
                # Auto log all MLflow from lightening
                # Save the run ID to use in testing phase
                self.run_id[appliance_name] = mlflow.active_run().info.run_id
                # Log parameters of current run
                mlflow.log_params(self.hparams)
                # Model Training
                model, _ = self.trainer_imp.fit(self.models[appliance_name], dataset,
                                         chkpt_path = f'{self.hparams["checkpoints_path"]}/{appliance_name}/{self.hparams["template_name"]}/{self.hparams["model_name"]}/version_{self.hparams["version"]}',
                                         exp_name = self.hparams['exp_name'],
                                         results_path= self.hparams['results_path'],
                                         logs_path = self.hparams['logs_path'],
                                         version = self.hparams['version'],
                                         batch_size=self.hparams['batch_size'],
                                         epochs=self.hparams['max_nb_epochs'],
                                         optimizer = self.hparams['optimizer'],
                                         learning_rate = self.hparams['learning_rate'],
                                         patience_optim= self.hparams['patience_optim'],
                                         patience_check=self.hparams['patience_check'],
                                         validation_metric=self.hparams['validation_metric'])

            self.models[appliance_name] = model
            self.appliance_params[appliance_name] = params

        return self.models, self.appliance_params

    def fit_cv(self, mains, submains):
        cv = CrossValidator( kfolds=self.hparams['kfolds'],
                            test_size=self.hparams['test_size'], gap=self.hparams['gap'])
        for appliance_name in submains.columns:
            power = submains[appliance_name]
            dataset, params = self.get_dataset(mains, power, seq_type=self.hparams['seq_type'],
                                               target_norm=self.hparams['target_norm'],
                                               in_size=self.hparams['in_size'],
                                               out_size=self.hparams['out_size'],
                                               point_position=self.hparams['point_position'], loader=self.loader_class, hparams={**self.hparams, **{'appliances':[appliance_name]}})
            mlflow.set_experiment(appliance_name)
            model, run_id, _ = cv.cross_validate( self.trainer_imp, dataset, self.models[appliance_name], appliance_name, self.hparams)
            self.models[appliance_name] = model
            self.run_id[appliance_name] = run_id
            self.appliance_params[appliance_name] = params

    def fit_hparams(self, mains, submains):
        opt = HparamsOptimiser(self.trainer_imp, self.hparams)
        for appliance_name in submains.columns:
            power = submains[appliance_name]
            dataset, params = self.get_dataset(mains, power, seq_type=self.hparams['seq_type'],
                                               target_norm=self.hparams['target_norm'],
                                               in_size=self.hparams['in_size'],
                                               out_size=self.hparams['out_size'],
                                               point_position=self.hparams['point_position'], hparams={**self.hparams, **{'appliances':[appliance_name]}})

            if isinstance(appliance_name, tuple):
                appliance_name_exp = appliance_name[0]+'_'+str(appliance_name[1])
            else:
                appliance_name_exp = appliance_name

            mlflow.set_experiment(appliance_name_exp)

            model, run_id = opt.optimise(self.models[appliance_name],dataset, appliance_name)
            self.models[appliance_name] = model
            self.run_id[appliance_name] = run_id
            self.appliance_params[appliance_name] = params


    def init_models(self, hparams=None):
        self.models = {
            app:  self.model_class({**self.hparams, **{'appliances':[app]}}  if hparams is None else {**hparams, **{'appliances':[app]}}) for app in self.appliances
        }

    def predict_model(self, mains, model, chkpt, app):
        # load the model from the checkpoint

        #model = self.trainer_imp.load_model(model, chkpt, prediction=True)
        data, _ = self.trainer_imp.get_dataset(mains, seq_type=self.hparams['seq_type'],
                                            target_norm=self.hparams['target_norm'],
                                            in_size=self.hparams['in_size'],
                                            out_size=self.hparams['out_size'],
                                            point_position=self.hparams['point_position'], loader=self.loader_class,
                                            hparams={**self.hparams, **{'appliances':[app]}})

        y_pred = self.trainer_imp.predict(model, data, self.hparams['batch_size'])
        logging.info(f"{y_pred.shape}")
        return y_pred


    def predict(self, mains):
        """
        predicts the power consumption of a building
        :param mains:
        :return:
        """
        predictions={}

        for appliance in self.models:

            if isinstance(appliance, tuple):
                appliance_instance = appliance[0]+'_' + str(appliance[1])
            else:
                appliance_instance = appliance

            mlflow.set_experiment(appliance_instance)

            if self.hparams['use_optuna']:
                m, params, _= dict(mlflow.get_run(self.run_id[appliance]))['data']
                v = params[1]['version']
            else:
                v= self.hparams['version']
            chkpt = f'{self.hparams["results_path"]}/{self.hparams["checkpoints_path"]}/{appliance}/{self.hparams["template_name"]}/{self.hparams["model_name"]}/version_{v}'
            # if CV is used the predictions are averaged over the models trained on different folds
            y_pred = self.predict_model( mains, self.models[appliance], chkpt, appliance) if self.hparams['kfolds']<=1 else \
                torch.stack([
                        self.predict_model(mains, self.models[appliance][fold], f"{chkpt}/{fold+1}", appliance) for  fold in range(self.hparams['kfolds'])
                    ], dim=0).numpy().mean(axis=0)

            predictions[appliance] = y_pred

            if self.hparams['log_artificat']:
                with mlflow.start_run(self.run_id[appliance]):
                    mlflow.log_artifacts(self.hparams['results_path'] + f'/{appliance}', artifact_path="test_results")

        return predictions






