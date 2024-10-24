import numpy as np

from .trainer_implementor import TrainerImplementor
import torch
import logging
import lightning.pytorch as pl
#from lightning.pytorch.tuner import Tuner

from deep_nilmtk.utils.logger import DictLogger,  get_latest_checkpoint

from deep_nilmtk.models.pytorch import PlModel
from deep_nilmtk.data.loader.pytorch import GeneralDataLoader

import os
import mlflow

torch.set_float32_matmul_precision("medium") # to avoid warning about "trade-off precision for performance"

pl.seed_everything(42, workers=True)


class TorchTrainer(TrainerImplementor):
    def __init__(self):
        self.batch_size = 64

    def log_init(self, chkpt_path, results_path, logs_path,  exp_name, version, patience_check=5):
        """
        Initialise the callbacks for the current experiment

        :param chkpt_path:  the path to save the checkpoint
        :param exp_name:  the name of the mlflow experiment
        :param version:  the version of the model
        :return:  checkpoint_callback, early_stop_callback, logger
        """
        logging.info(f"The checkpoints are logged in {chkpt_path} metric: val_loss , mode: min")
        callbacks = []
        checkpoint_callback = pl.callbacks.model_checkpoint.ModelCheckpoint(dirpath=chkpt_path,
                                                                            monitor='val_loss',
                                                                            mode="min",
                                                                            save_top_k=1,
                                                                            save_weights_only = False) # only the model’s weights will be saved. Otherwise, the optimizer states, lr-scheduler states, etc are added in the checkpoint too.
        
        callbacks.append(checkpoint_callback)
        if patience_check != "None":
            early_stop_callback = pl.callbacks.EarlyStopping(monitor='val_loss',
                                                         min_delta=1e-4,
                                                         patience=patience_check,
                                                         mode="min")
            callbacks.append(early_stop_callback)

        logger = DictLogger(f'{results_path}/{logs_path}',
                            name=exp_name,
                            version="single_appliance_experiment" + str(version) if version != '' else "single_appliance_experiment")

        return callbacks, logger

    def fit(self, model, dataset,
            chkpt_path=None,exp_name=None,results_path=None, logs_path=None,  version=None,
            batch_size=64, epochs=20, use_checkpoint=False, learning_rate=1e-6, optimizer='adam', patience_optim=5, patience_check=5,
            train_idx=None, validation_idx=None, auto_lr=False):
        # Load weights from the last checkpoint if any in the checkpoints path

        best_checkpoint = get_latest_checkpoint(f'{results_path}/{chkpt_path}')
        self.batch_size = batch_size

        if auto_lr:
            pl_model = PlModel(model, optimizer=optimizer,  patience_optim=patience_optim)
        else:
            pl_model = PlModel(model, optimizer=optimizer, learning_rate=learning_rate, patience_optim=patience_optim)


        callbacks_lst, logger = self.log_init(f'{results_path}/{chkpt_path}',results_path, logs_path, exp_name, version, patience_check=patience_check)
        logging.info(f'Training started for {epochs} epochs')

        if not os.path.exists(f'{results_path}/{chkpt_path}/'):
            os.makedirs(f'{results_path}/{chkpt_path}/')

        mlflow.pytorch.autolog()

        trainer = pl.Trainer(logger=logger, # No es necesario para obtner las métricas (automático con logs y callback_metrics)  
                             max_epochs=epochs,
                             callbacks=callbacks_lst,
                             accelerator="auto",
                             deterministic='warn' # deterministic algorithms whenever possible
                            )
        
        # tuner = Tuner(self.trainer)
        # tuner.lr_find(pl_model)

        dataset_train, dataset_validation = self.data_split(dataset , batch_size, train_idx, validation_idx)
        # Fit the model using the train_loader, val_loader
        trainer.fit(pl_model, dataset_train, dataset_validation, ckpt_path=best_checkpoint if use_checkpoint else None)

        if not use_checkpoint: # No fucniona si e parte de checkpoint
            val_metric = trainer.callback_metrics["val_loss"].item() #last value
            print(f"VAL LOSS METRIC:{val_metric}")
        else:
            val_losses = [metric['val_loss'] for metric in logger.metrics if len(logger.metrics)>1 and 'val_loss' in metric] # metrics logged for all epochs as defined in (PlModel -> validation_step()) and (model -> step())
            val_metric = np.min(val_losses) if len(val_losses)>0 else -1 
            # metrics is empty if training starts from best_checkpoint (it is not improved?)     
        return pl_model, val_metric #np.min(val_losses) if len(val_losses)>0 else -1 #min value

    def get_dataset(self, main, submain=None, seq_type='seq2point',
                    in_size=99, out_size=1, point_position='mid_position',
                    target_norm='z-norm', quantiles= None,  loader= None, hparams=None):

        data = GeneralDataLoader(
            main, targets=submain,
            in_size=in_size,
            out_size=out_size,
            point_position=point_position,
            seq_type=seq_type,
            quantiles=quantiles,
            pad_at_begin=False
        ) if loader is None else \
            loader(main, submain, hparams)
        return data, data.params

    def data_split(self, data, batch_size, train_idx=None, val_idx=None):
        """
        Splits data to training and validation
        :param main:
        :param target:
        :param appliance_name:
        :return:
        """
        if train_idx is None or val_idx is None:
            train_idx = int(data.len * (1 - 0.15))
            val_idx = data.len - int(data.len * (1 - 0.15))
        else:
            if isinstance(train_idx,np.ndarray):
                train_idx = train_idx.shape[0]
                val_idx = val_idx.shape[0]
            
        
        train_data, val_data = torch.utils.data.random_split(data,
                                      [train_idx, val_idx],
                                      generator=torch.Generator().manual_seed(3407))

        train_loader = torch.utils.data.DataLoader(train_data,
                                                   batch_size,
                                                   shuffle=True)
            
        val_loader = torch.utils.data.DataLoader(val_data,
                                                 batch_size,
                                                 shuffle=False)
        
        return train_loader, val_loader

    def train_test_split(self, data, train_idx, val_idx, batch_size):
        return self.data_split(
            data,
            batch_size,
            train_idx,
            val_idx
        )

    def predict(self, model, mains, batch_size=64):

        test_loader = torch.utils.data.DataLoader(mains,
                                                   batch_size,
                                                   shuffle=False)

        network = model.model.eval()
        predictions = network.predict(model, test_loader)
        df = predictions['pred']

        return df

    def load_model(self, model, path, prediction= False):
        logging.info(f'Loading Torch models from path :{path}')

        #path = str(self.trainer.checkpoint_callback.best_model_path)
        #checkpoint = torch.load(path)

        print(f"CHECK_PATH: {path}")
        print(f"MODEL TYPE: {type(model)}")
        
        checkpoint = torch.load(get_latest_checkpoint(path))

        state_dict = checkpoint["state_dict"]
        model_state_dict = model.state_dict()
        is_changed = False
        for k in state_dict:
            if k in model_state_dict:
                if state_dict[k].shape != model_state_dict[k].shape:
                    # logger.info(f"Skip loading parameter: {k}, "
                    #             f"required shape: {model_state_dict[k].shape}, "
                    #             f"loaded shape: {state_dict[k].shape}")
                    model_state_dict[k] = state_dict[k]
                    is_changed = True
            else:
                # logger.info(f"Dropping parameter {k}")
                is_changed = True

        if is_changed:
            print("CHANGE")
            model.load_state_dict(model_state_dict) #.pop("optimizer_states", None)

        if not isinstance(model, PlModel):
            pl_model = PlModel(model)
        else:
            pl_model = model

        #pl_model.load_state_dict(checkpoint['state_dict'])
        pl_model.eval()

        return pl_model
        print('LOADED')
        
        """      
        pl_model = PlModel.load_from_checkpoint(path, testing = False, net=model)
        pl_model.eval()
        return pl_model
        """
       

       
 




