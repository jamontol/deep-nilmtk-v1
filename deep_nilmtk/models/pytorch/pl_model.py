import torch
from torchmetrics import MinMetric, MeanMetric

import lightning as pl
import mlflow


class PlModel(pl.LightningModule):
    """
    Lightning module that is compatible
    with PyTorch models included in Deep-NILMtk.
    """

    def __init__(self, net, optimizer="adam", learning_rate=1e-4, patience_optim=5):
        super().__init__()
        self.save_hyperparameters() #"net", logger=True
        self.model = net
        self.optimizer = optimizer
        self.learning_rate = learning_rate
        self.patience_optim = patience_optim

        # for tracking best so far validation loss
        # self.val_loss_best = MinMetric()
        # self.val_mae_best = MinMetric()


    def forward(
        self,
        x,
    ):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        loss, mae = self.model.step(batch)
        self.log(
            "train_loss", loss, on_step=False, on_epoch=True, prog_bar=True, logger=True
        )
        self.log(
            "train_mae", mae, on_step=False, on_epoch=True, prog_bar=True, logger=True
        )
        # self.log("rmse", rmse, on_step=False, on_epoch=True, prog_bar=True, logger=True)
        return loss

    def validation_step(self, batch, batch_idx):
        loss, mae = self.model.step(batch)

        self.log(
            "val_loss", loss, on_step=False, on_epoch=True, prog_bar=True, logger=True
        )
        self.log(
            "val_mae", mae, on_step=False, on_epoch=True, prog_bar=True, logger=True
        )
        # self.log("rmse", rmse, on_step=False, on_epoch=True, prog_bar=True, logger=True)

    """
    def on_validation_epoch_end(self, outs: List[Any]):

        val_loss = self.val_loss.compute()  # get current val loss
        val_mae = self.val_mae.compute()  # get current val accuracy
        self.val_loss_best(val_loss)  # update best so far val loss
        self.val_mae_best(val_mae)  # update best so far val loss
        # log `val_acc_best` as a value through `.compute()` method, instead of as a metric object
        # otherwise metric would be reset by lightning after each epoch
        self.log("val_loss_best", self.val_loss_best.compute(), on_step=False, on_epoch=True, prog_bar=False, logger=True)
    """

    def configure_optimizers(self):
        """
        Choose what optimizers and learning-rate schedulers to use in your optimization.


        Returns:
            two lists: a list of optimzer and a list of scheduler
        """

        if self.optimizer == "adamw":
            optim = torch.optim.AdamW(self.parameters(), lr=self.learning_rate)
        elif self.optimizer == "adam":
            optim = torch.optim.Adam(self.parameters(), lr=self.learning_rate)
        elif self.optimizer == "sgd":
            optim = torch.optim.SGD(
                self.parameters(), lr=self.learning_rate, momentum=0.9
            )
        else:
            raise ValueError

        if self.patience_optim == "None":
            return [optim], []
        else:
            sched = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optim, patience=self.patience_optim, verbose=True, mode="min"
            )
            scheduler = {
                "scheduler": sched,
                "monitor": "val_loss",
                "interval": "epoch",
                "frequency": 1,
            }

            return [optim], [scheduler]
    """
    def on_load_checkpoint(self, checkpoint: dict) -> None:
        state_dict = checkpoint["state_dict"]
        model_state_dict = self.state_dict()
        is_changed = False
        for k in state_dict:
            if k in model_state_dict:
                if state_dict[k].shape != model_state_dict[k].shape:
                    # logger.info(f"Skip loading parameter: {k}, "
                    #             f"required shape: {model_state_dict[k].shape}, "
                    #             f"loaded shape: {state_dict[k].shape}")
                    state_dict[k] = model_state_dict[k]
                    is_changed = True
            else:
                # logger.info(f"Dropping parameter {k}")
                is_changed = True

        if is_changed:
            checkpoint.pop("optimizer_states", None)
    """