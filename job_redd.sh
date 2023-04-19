#!/bin/bash
#SBATCH --time=240
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --output=job_redd2_6h.out
#SBATCH --error=error_redd2_6h.out
#SBATCH --job-name=bert4nilm_redd2_6h

SECONDS=0

python run.py --appliance 'washing machine' --model_config bert4nilm_redd2.json --experiment_template redd_acts_from_repo --results_path results_redd_6h
python run.py --appliance 'dish washer' --model_config bert4nilm_redd2.json --experiment_template redd_acts_from_repo --results_path results_redd_6h
python run.py --appliance 'fridge' --model_config bert4nilm_redd2.json --experiment_template redd_acts_from_repo --results_path results_redd_6h
python run.py --appliance 'microwave' --model_config bert4nilm_redd2.json --experiment_template redd_acts_from_repo --results_path results_redd_6h

duration=$SECONDS
echo "$(($duration / 3600)):$(($duration % 60)) (h:m)"
