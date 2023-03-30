
from deep_nilmtk.utils.templates import ExperimentTemplate
import json
import sys

DATA_PATH = "datasets/ukdale.h5"
RESULTS_PATH = "new_results"

with open(f"param_configs/{sys.argv[1]}","r") as f:
    experiment_details = json.load(f)

# template initialization
template = ExperimentTemplate(data_path=DATA_PATH,
                              template_name="test_experiment",
                              list_appliances=experiment_details["appliances"],
                              list_baselines_backends=[(experiment_details["model_type"], "pytorch")],
                              experiment_details=experiment_details)

template.run_template(experiment_details["experiment_name"], 
                      f"{RESULTS_PATH}/baselines",
                      f"{RESULTS_PATH}/mlflow/mlruns")