# pipeleak_prediction

## What is pipeleakprediction?
pipeleak_prediction is an open-source python program, intending to predict the leak of the pipes using AI.

Two types of prediction must be done:
- minsector
- pipes
    
## Dependences
To use this program you will have install diferent pakages for python, these are:
`pip install tensorflow`

`pip install tensorflow-addons`

`pip install tensorflow-probability`

`pip install seaborn`

`pip install psycopg2`

Also, you have got a csv, which is actuating as a database.
 If you want to improve it, you will have to search data for your own.

## Connections parameters
Copy-paste example.conf and rename it to config.conf, in order to parametrize your connection parameters

## Data model

On https://github.com/Giswater/pipeleak_prediction/wiki you can find all about datamodel to work with

Source tables
    ai_inventory
    ai_hydraulics
    ai_ndvi
    ai_leak
     
## Train

#### Database configuration

##### config_param_system table
    dataset_leak_interval -> years of leak data  to train
    treshold_arc_length_max -> max length for pipes  to train 
    treshold_arc_length_min -> min length for pies to train
    treshold_arc_pnom_min -> min pnom for pipes to train
    treshold_arc_slope_max -> max slope for pipes to train
    treshold_minsector_frequency_max -> max leak frequency (n/(yearkm) to train
    treshold_minsector_frequency_min -> min leak frequency (n/(yearkm) to train
    treshold_minsector_vel_max   

##### ai_cat_mat table
Parametrize the normalized name to integer values using 0 as other when there are less materials

#### Python code adjustment
- Configuration of model inputs (# Set model inputs)
- Normalize model inputs (# Set normalize inputs)    
- Adjustment of model parameters, optimizer, losses, metrics.... (# Set model parameters)
    * dynamic variables 
    * static variables
	
NOTES:
- Model inputs and normalized inputs must be the same

#### Execute
- train_arc_model
- train_minsector_model

Results will be stored on /training/saves/ folder with model name and other parameters to fast identification

#### Tensor board (to check losses and metrics)
go to training foder and open cmd
execute 'tensorboard --logdir=logs'

    
## Predict

#### Python code adjustment
- Predict inputs names must be the same as trained input names. (# Set model input names)
- Choose trained model to predict (# Choose trained model to predict)

#### Execute
- predict_arc
- predict_minsector

Results will be stored on /predict/ folder
