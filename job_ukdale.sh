#!/bin/bash
#SBATCH --time=2880
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --output=job_ukdale2.out
#SBATCH --error=error_ukdale2.out
#SBATCH --job-name=bert4nilm_ukdale2

SECONDS=0

python run.py --appliance 'washing machine' --model_config bert4nilm_ukdale2.json --experiment_template uk_dale_acts_from_paper --results_path results_ukdale
python run.py --appliance 'washing machine' --model_config bert4nilm_ukdale2.json --experiment_template uk_dale_acts_from_repo --results_path results_ukdale
python run.py --appliance 'dish washer' --model_config bert4nilm_ukdale2.json --experiment_template uk_dale_acts_from_paper --results_path results_ukdale
python run.py --appliance 'dish washer' --model_config bert4nilm_ukdale2.json --experiment_template uk_dale_acts_from_repo --results_path results_ukdale
python run.py --appliance 'fridge' --model_config bert4nilm_ukdale2.json --experiment_template uk_dale_acts_from_paper --results_path results_ukdale
python run.py --appliance 'fridge' --model_config bert4nilm_ukdale2.json --experiment_template uk_dale_acts_from_repo --results_path results_ukdale
python run.py --appliance 'microwave' --model_config bert4nilm_ukdale2.json --experiment_template uk_dale_acts_from_paper --results_path results_ukdale
python run.py --appliance 'microwave' --model_config bert4nilm_ukdale2.json --experiment_template uk_dale_acts_from_repo --results_path results_ukdale


duration=$SECONDS
echo "$(($duration / 3600)):$(($duration % 60)) (h:m)"
