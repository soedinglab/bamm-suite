#!/bin/zsh

#BSUB -q mpi
#BSUB -W 23:50
#BSUB -n 4
#BSUB -a openmpi
#BSUB -o ./jobs/gtrd_rat.%J
#BSUB -R "span[hosts=1]"
#BSUB -R scratch
#BSUB -J GTRDr[1-19]
#BSUB -m mpi mpi2 mpi3_all

source ./paths.sh

main_dir=/scratch/wge/GTRD/rat
fasta_dir=${main_dir}/fasta_summit100

bn=$(sed "${LSB_JOBINDEX}q;d" ${main_dir}/info.db)
bn=$(basename ${bn} .fasta)

result_dir=${main_dir}/PEnG_BaMM/
peng_dir=${result_dir}/initPWMs
bamm_dir=${result_dir}/models
logs_dir=${result_dir}/logs

mkdir -p ${peng_dir}
mkdir -p ${bamm_dir}
mkdir -p ${logs_dir}

python3 ${SHOOT_PENG} -o ${peng_dir}/${bn}.meme -d ${peng_dir}/${bn}_tmp -w 8 ${fasta_dir}/${bn}.fasta --threads 4 > ${logs_dir}/${bn}.shootpeng.logg

rm -fr ${peng_dir}/${bn}_tmp

${BAMMMOTIF} ${bamm_dir}/${bn} ${fasta_dir}/${bn}.fasta --PWMFile ${peng_dir}/${bn}.meme --maxPWM 1 --EM -k 4 --FDR -m 10 --scoreSeqset --extend 0 0 --threads 4 > ${logs_dir}/${bn}.bamm.logg

${plotRRC} ${bamm_dir}/${bn}/ ${bn} --plots 1

${DISTRIBUTION} ${bamm_dir}/${bn}/ ${bn}

${LOGO} ${bamm_dir}/${bn}/ ${bn} 0 --web WEB

${LOGO} ${bamm_dir}/${bn}/ ${bn} 1

${LOGO} ${bamm_dir}/${bn}/ ${bn} 2

rm -fr ${bamm_dir}/${bn}/${bn}.hbp

rm -fr ${bamm_dir}/${bn}/${bn}*.ihbp

