#!/bin/bash
#SBATCH --time=20
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=job.out
#SBATCH --error=error.out
#SBATCH --mem=4000
#SBATCH --job-name=bert4nilm0

SECONDS=0

python run.py --appliance fridge --model_config bert4nilm_ukdale.json --experiment_template uk_dale_acts_from_paper --results_path dummy_results

duration=$SECONDS
echo "$(($duration / 3600)):$(($duration % 60)) (h:m)"
