#!/usr/bin/env bash

STACK=$1
ENV=$2
REGION=$3
MODE=$4
OVERRIDE_TFVARS=$5

if [[ ! -f terraform.sh ]]
then
  echo "$0 must be run from the same directory"
  exit 1
fi

if [[ ( "$#" -lt 4 ) || ( "$#" -gt 5 ) ]]
then
	printf "\n $RED  Usage: $0 <stack> <tfvars env name> <tfvars region name> <plan|apply> <tfvars overrides (optional)>\n"
	printf "\n     e.g. $0 app-mesh dev-k8s eu-west-2 plan \n"
	exit 1
fi

if [[ $MODE == 'plan' ]]
then
  TF_ACTION_STRING='plan'
elif [[ $MODE = 'apply' ]]
then
  TF_ACTION_STRING='apply -auto-approve'
elif [[ $MODE = 'plan-destroy' ]]
then
  TF_ACTION_STRING='plan -destroy'
elif [[ $MODE = 'destroy' ]]
then
  TF_ACTION_STRING='destroy -auto-approve'
else
  echo "invalid mode $MODE"
  exit 1
fi

TFVARS_FILE="../../tfvars/env/$ENV.tfvars"
GLOBAL_TFVARS_FILE="../../tfvars/global/global.tfvars"
STACKDIR="../stacks/$STACK"
TF_OUTPUT_FILE="/var/tmp/$ENV-$STACK-output.txt"

> $TF_OUTPUT_FILE

# Generate undeclared tfvars to prevent warnings
# ./generateMissingTFvars.sh $ENV $REGION $STACK

echo '=============================='
pwd
cd $STACKDIR
pwd
ls $GLOBAL_TFVARS_FILE
echo '=============================='


tfenv use 1.6.0

echo $ENV
terraform --version

terraformStateBucket="nhsd-texasplatform-terraform-service-state-store-lk8s-nonprod"
keyToUse="vsmt/$ENV/$STACK"
awsRegion="eu-west-2"
terraform init -upgrade -reconfigure -backend-config="bucket=$terraformStateBucket" -backend-config="key=$keyToUse/terraform.tfstate" -backend-config="region=$awsRegion" -no-color

if [[ ${OVERRIDE_TFVARS} == '' ]]
then
    terraform $TF_ACTION_STRING -var-file=${GLOBAL_TFVARS_FILE} -var-file=${TFVARS_FILE} 2>&1 | tee $TF_OUTPUT_FILE
else
    terraform $TF_ACTION_STRING -var-file=${GLOBAL_TFVARS_FILE} -var-file=${TFVARS_FILE} -var="${OVERRIDE_TFVARS}" 2>&1 | tee $TF_OUTPUT_FILE
fi

# Make TF/pipeline error if a stack fails
if [[ "$(grep '^.*Error:' $TF_OUTPUT_FILE)" != '' ]]
then
  exit 1
fi
