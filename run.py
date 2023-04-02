
from deep_nilmtk.utils.templates import ExperimentTemplate
import json
from argparse import ArgumentParser

DATA_PATH = "datasets/ukdale.h5"
RESULTS_PATH = "new_results"

parser = ArgumentParser(add_help=False)

parser.add_argument('--model_config', type=str)
parser.add_argument('--appliance', type=str)
parser.add_argument('--experiment_template', type=str)

args = parser.parse_args()

with open(f"model_configs/{args.model_config}","r") as f:
    model_config = json.load(f)
    
e_template = args.experiment_template
    
# template initialization
template = ExperimentTemplate(data_path=DATA_PATH,
                              template_name=e_template,
                              list_appliances=[args.appliance],
                              list_baselines_backends=[(model_config["model_type"], "pytorch")],
                              model_config=model_config)

template.run_template(e_template, 
                      f"{RESULTS_PATH}/baselines",
                      f"{RESULTS_PATH}/mlflow/mlruns")