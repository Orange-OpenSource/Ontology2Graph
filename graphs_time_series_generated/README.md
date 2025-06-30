# Graph generated at regular interval

In this folder are stored graph generated at regular intervals.  

In order to produce line charts based on kpi produced by robots you have to do the following step

## Produce robots results

Robot results are produce thanks to the script script.sh. This script must be adapted for each robots measurements procuced, regarding the folder where the script is located and the folders where the robots mesurement are located.
This script launch several robot command on knowledge graph. $1 argument correspond the time when the script has been launch in the following format hh:mm:ss. It must be pass to the script like that "bash script.sh hh:mm:ss"

## Generate Time Series 

Time series will be created thanks to trasnpose_kpis.py & concat.py

This script transpose file produce by robots. It take into account one argument corresponding to 
the date of the robot measurement file in the following format : 2025-06-16_16-00-02 You have to 
set up the MODEL constant accordingly to the MODEL used by graphllm.py

Then with concat.py you will merge all the transposed files in an only one and remove some useless kpis.
 Concat.py must be placed in the same folder than the trasnposed files.

The result concatenated_file.csv correspond to the KPIS's time series.

## Dysplay the line charts

plot_line_charts.py will plot the line chart, the name of the KPIs must be use as an argument when laucnhing the python file

