from deep_nilmtk.utils import setup
from deep_nilmtk.disaggregator import NILMExperiment
from deep_nilmtk.config import __models__ as models

from deep_nilmtk.utils.templates.baseline_templates import templates
from deep_nilmtk.utils.check_dataset_buildings import buildings_available


class ExperimentTemplate:
    def __init__(self,
                 data_path,
                 template_name,
                 list_appliances,
                 list_baselines_backends,
                 model_config):
        self.experiment = buildings_available(templates[template_name], list_appliances[0])
        self.template_name = template_name
        self.data_path = data_path
        if list_appliances is not None:
            self.experiment.update({'appliances': list_appliances})
        methods = {}
        for baseline, backend in list_baselines_backends:
            # get model architecture info
            params = models[backend][baseline]['model'].get_template()
            # get model training info 
            params.update(model_config)
            # get appliance specific activation info
            for aap in self.experiment['app_activation_params'].keys():
                params[aap] = self.experiment['app_activation_params'][aap][list_appliances[0]]
            # get additional experiment info
            params.update(self.experiment['experiment_settings'])
            params.update({'aggregate_cutoff': self.experiment['aggregate_cutoff']})
            # store template name
            params.update({'template_name': self.template_name})
            methods.update({
                baseline: NILMExperiment(params)
            })

        self.experiment.update({'methods': methods})
        # update the data path
        self.set_data_path()


    def set_data_path(self):
    
        dataset_name = self.experiment['train']['datasets'][list(self.experiment['train']['datasets'].keys())[0]]['path']

        self.experiment['data'] = dataset_name

        for data in self.experiment['train']['datasets']:
            self.experiment['train']['datasets'][data].update({
                'path':self.data_path + self.experiment['train']['datasets'][data]['path']
            })
        for data in self.experiment['test']['datasets']:
            self.experiment['test']['datasets'][data].update({
                'path':self.data_path + self.experiment['test']['datasets'][data]['path']
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
