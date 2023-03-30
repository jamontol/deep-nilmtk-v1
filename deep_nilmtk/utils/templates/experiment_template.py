from deep_nilmtk.utils import setup
from deep_nilmtk.disaggregator import NILMExperiment
from deep_nilmtk.config import __models__ as models

from deep_nilmtk.utils.templates.baseline_templates import templates


class ExperimentTemplate:
    def __init__(self,
                 data_path,
                 template_name,
                 list_appliances,
                 list_baselines_backends,
                 experiment_details):
        self.experiment = templates[template_name]
        self.template_name = template_name
        self.data_path = data_path
        if list_appliances is not None:
            self.experiment.update({'appliances': list_appliances})
        methods = {}
        for baseline, backend in list_baselines_backends:
            # get model architecture info
            params = models[backend][baseline]['model'].get_template()
            # get training info 
            params.update(experiment_details)
            # get appliance specific activation info
            params.update(self.experiment['app_activation_params'])
            # get additional experiment info
            params.update(self.experiment['experiment_settings'])
            methods.update({
                baseline: NILMExperiment(params)
            })

        self.experiment.update({'methods': methods})
        # update the data path
        self.set_data_path()


    def set_data_path(self):
        for data in self.experiment['train']['datasets']:
            self.experiment['train']['datasets'][data].update({
                'path':self.data_path
            })
        for data in self.experiment['test']['datasets']:
            self.experiment['test']['datasets'][data].update({
                'path':self.data_path
            })

    def __print__(self):
        print(f""""
        The current experiment is based on template {self.template_name}
        Appliances {self.experiment['appliances']}
        NILM MODELS {list(self.experiment['methods'].keys())}
        Dataset path {self.data_path}
            - sampling rate :{self.experiment['sample_rate']}
            - training data 
                - uses following buildings {len(self.experiment['train']['datasets']['ukdale']['buildings'])}
                - uses following buildings {len(self.experiment['train']['datasets']['ukdale']['buildings'])}
            - testing data
                - uses following buildings {len(self.experiment['test']['datasets']['ukdale']['buildings'])}
        """)

    def extend_experiment(self, nilm_experiment_dictionnay):
        self.experiment['methods'].update(
            nilm_experiment_dictionnay
        )

    def run_template(self, experiment_name,
                     results_path,
                     mlflow_path):
        _ = setup(self.experiment, experiment_name=experiment_name,
                  results_path=results_path,
                  mlflow_repo=mlflow_path)
