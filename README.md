# pipeleak_prediction

## What is pipeleakprediction?
pipeleak_prediction is an open-source python program, intending to predict the leak of the pipes using AI.

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

## Hello world
To use this program you will have to follow the following steps:
- First, you have to train the model, with the program train_minsector_model.py or train_arc_model.py.
- Now use predict.py to get the network output for all your data.
