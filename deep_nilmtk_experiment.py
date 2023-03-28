
from deep_nilmtk.utils.templates import ExperimentTemplate


DATA_PATH = "datasets/ukdale.h5"
EXPERIMENT_NAME = "trees"
RESULTS_PATH = "new_results"

model_type1 = "Seq2Pointbaseline"
model_type2 = "RNNbaseline"
model_type3 = "BERT4NILM"
appliances = ["fridge"] #, "washing machine"]
seq_length = 99
out_sequence = 1
max_epochs = 1

# template initialization
template = ExperimentTemplate(data_path=DATA_PATH,
                              template_name="test_experiment",
                              list_appliances=appliances,
                              list_baselines_backends=[(model_type1, "pytorch")],
                              in_sequence=seq_length,
                              out_sequence=out_sequence,
                              max_epochs=max_epochs)

template.run_template(EXPERIMENT_NAME, 
                      f"{RESULTS_PATH}/baselines",
                      f"{RESULTS_PATH}/mlflow/mlruns")