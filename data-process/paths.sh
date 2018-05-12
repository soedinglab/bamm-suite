#!/bin/zsh

# DIRECTORIES
export FDR=~/opt/BaMM/bin/FDR
export BAMMMOTIF=~/opt/BaMM/bin/BaMMmotif
export PENGMOTIF=~/opt/PEnG/bin/peng_motif

# PATH to R and Python scripts
export SHOOT_PENG=~/opt/PEnG/bin/shoot_peng.py
export EVALUATION=~/opt/BaMM/bin/evaluateBaMM.R
export plotRRC=~/opt/BaMM/bin/plotPvalStats.R
export DISTRIBUTION=~/opt/BaMM/bin/plotMotifDistribution.R
export LOGO=~/opt/BaMM/bin/plotBaMMLogo.R
export FILTER_PWM=~/opt/BaMM/bin/filterPWM.py

# UPDATE paths
export PATH=${PATH}:${HOME}/opt/BaMM/bin
export PATH=${PATH}:${HOME}/opt/PEnG/bin

# update runnning environment variable
source ~/.bashrc
#module load gcc/6.3.0
#module load python/3.5.1
