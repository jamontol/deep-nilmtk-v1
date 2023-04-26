import pandas as pd
from nilmtk.disaggregate import Disaggregator
import warnings
from deep_nilmtk.data.pre_process import preprocess, bert_preprocess, generate_features
from deep_nilmtk.data.post_process import postprocess, bert_postprocess
from deep_nilmtk.trainers import Trainer, TorchTrainer#, KerasTrainer
#from deep_nilmtk.models.pytorch.bert4nilm import compute_custom_f1
from deep_nilmtk.config import get_exp_parameters
from deep_nilmtk.utils import check_model_backend
from collections import OrderedDict
import logging

warnings.filterwarnings("ignore")



class NILMExperiment(Disaggregator):
    """
    This class defines a NILM experiment. It is compatible with both
    single and multi-appliance models and offers different advanced features
    like cross-validation and hyper-parameters optimization during the
    training phase. The class is independent of the deep model used for
    load disaggregation.

    .. note:: For a PyTorch model to be compatible with this class, an entry should be added for this model in the config module.
    """

    def __init__(self, params):
        self.models = None
        super().__init__()

        hparams = get_exp_parameters()
        # hparams = vars(hparams.parse_args())
        hparams, remaining_args = hparams.parse_known_args()
        hparams = vars(hparams)
        hparams.update(params)
        self.hparams = hparams
        self.MODEL_NAME = hparams['model_name']
        self.models = OrderedDict()
        self.appliance_params = {}
        self.main_params =  {}
        assert self.hparams['backend'] == 'pytorch' or self.hparams['backend'] == 'tensorflow', \
            'The specified dl framework is not compatible'
        logging.info(f'The DL Framework used is:{self.hparams["backend"]}')
        self.trainer = Trainer(self.get_trainer(), self.hparams)
        check_model_backend(hparams['backend'], hparams['model_class'] if 'model_class' in hparams else None, hparams['model_name'])

    def result_path(self, path):
        self.hparams['results_path'] = path

    # ------------------------- Fit Functions -------------------------------
    def partial_fit(self, mains, sub_main, do_preprocessing=True, **load_kwargs):
        """
        Train the model for all appliances
        :param mains:
        :param sub_main:
        :param do_preprocessing:
        :param load_kwargs:
        """
        logging.info(f'Started the experiment with name {self.hparams["exp_name"]}')
        # STEP 01: Pre-processing

        if do_preprocessing:
            mains, params, sub_main = preprocess(mains,self.hparams['input_norm'], sub_main) if not self.hparams['custom_preprocess'] \
                else eval(self.hparams['custom_preprocess'])(mains, self.hparams['input_norm'], sub_main, self.hparams)

            self.main_params = params
            print("input normalisation before training creates main_params:")
            print(self.main_params)

        # STEP 02: Feature engineering
        mains = generate_features(mains, self.hparams)
        self.trainer.hparams.update(self.hparams)
        # STEP 03: Model Training
        self.models, self.appliance_params = self.trainer.fit(mains, sub_main)
        print("appliance_params after training:")
        print(self.appliance_params)

    def get_trainer(self):
        """
        return the trainer according to the chosen DL framework
        Possibility of extension in the future
        """
        if self.hparams['backend'] == 'pytorch':
            return TorchTrainer()
        #elif self.hparams['backend'] == 'tensorflow':
        #    return KerasTrainer()
        else:
            raise Exception('The specified deep learning framework is not compatible, possible values for backend are : pytorch, tensorflow')



    # ------------------------- Disaggregregation Functions -------------------------------
    def disaggregate_chunk(self, test_main_list, do_preprocessing=True):
        """

        :param test_main_list:
        :param do_preprocessing: Bool
        :return: list of dataFrames containing the prediction for each chunk
        """
        predictions_results = []
        for test_mains_df in test_main_list:
            # STEP 01: Pre Process
            print(test_mains_df.shape)
            if do_preprocessing:
                print("doing input normalisation on test data using main_params:")
                print(self.main_params)
                test_mains_df, params = eval(self.hparams['custom_preprocess'])([test_mains_df], norm_type=self.hparams['input_norm'], params=self.hparams) if  self.hparams['custom_preprocess'] \
                    else  preprocess([test_mains_df], norm_type=self.hparams['input_norm'], params=self.main_params)
            else:
                logging.warning('The data was not normalised, this may influence the performance of your model')

            # STEP 02: Generate the predictions
            predictions = self.trainer.predict(test_mains_df)

            # STEP 03: Post Process
            predictions = postprocess(predictions, self.hparams['target_norm'], self.appliance_params,\
                                      aggregate= (self.hparams['seq_type'] == 'seq2seq' or self.hparams['seq_type'] == 'seq2subseq'), stride=self.hparams['stride'])\
                if not self.hparams['custom_postprocess'] else eval(self.hparams[
                'custom_postprocess'])(predictions)

            predictions_results.append(pd.DataFrame(predictions))
        
        #if self.hparams['model_type'] == 'BERT4NILM':
            # TODO: custom f1 computation using specified threshold
            #custom_f1 = compute_custom_f1(predictions_results)
            #print("............ f1-score with appliance-specific threshold ..............")
            #print(custom_f1) 
        
        return predictions_results
