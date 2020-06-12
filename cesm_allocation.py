#!/usr/bin/env python
"""Reference: https://stackoverflow.com/questions/20063/whats-the-best-way-to-parse-command-line-arguments"""
"""To be ran to call b2deg_alternative.py to allow better control and manipulation of parameters from the command line."""
"""Reference: https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file"""
import argparse
import sys
import subprocess
import shutil
import os
import b2deg_alternative
# Possibility of using command line arguments

"""
Reference: https://www.pythoncentral.io/pythons-time-sleep-pause-wait-sleep-stop-your-code/
Reference: https://stackoverflow.com/questions/53513/how-do-i-check-if-a-list-is-empty
Reference: https://stackoverflow.com/questions/26151669/valueerror-max-arg-is-an-empty-sequence
"""
#
def command_line_parse():
    comd_line_cesm_parser = argparse.ArgumentParser(description = "Command line arguments submitted to the python script for CESM. Supply the file directory, the number of processors for the non-ESP components, and the number of processors for the ESP component.")
    comd_line_cesm_parser.add_argument("selected_file_directory", help="The file directory that the cesm files will be created within.")
    comd_line_cesm_parser.add_argument("num_of_non_ESP_processors", help="The number of processors that non-ESP componenets will receive during the run of CESM")
    comd_line_cesm_parser.add_argument("num_of_ESP_processors", help="The number of processors that the ESP component will receive during the run of CESM.")
    cesm_comd_args = comd_line_cesm_parser.parse_args()
    comd_line_inputs = [comd_line_cesm_parser.selected_file_directory, comd_line_cesm_parser.num_of_non_ESP_processors, comd_line_cesm_parser.num_of_ESP_processors]
   
def initiate_first_runCESM():
    comd_line_cesm_parser = argparse.ArgumentParser(description = "Command line arguments submitted to the python script for CESM. Supply the maximum amount of processors to be allocated to CESM.")
    comd_line_cesm_parser.add_argument("selected_maxtasks", help="The maximum amount of processors to be allocated to CESM runs must be submitted.")
    cesm_comd_args = comd_line_cesm_parser.parse_args()
    targeted_timing_files_directory, completeCESMComponentDictionaryForLoad = b2deg_alternative.default_max_tasks_json(cesm_comd_args.selected_maxtasks)#Running the function Initiating CESM and load_balancing_solve.py
    continueRunProcess = True
    while(continueRunProcess==True):
        continueRunProcess = checkBeforeNextRunOfLoadBalance()
        intiate_base_load_balancing(targeted_timing_files_directory, completeCESMComponentDictionaryForLoad)
        optimized_values_cesm_json = b2deg_alternative.retrieve_recent_cesm_ntasks_json_file(1)
        continueRunProcess = checkBeforeNextRunOfCESM() 
        targeted_timing_files_directory = optimize_values_allocation_run(optimized_values_cesm_json,total_tasks_for_cesm_json,target_directory_for_CESM)
 
def checkBeforeNextRunOfCESM():
    checkforLoadBalanceRun = raw_input("Do you want to run the CESM software? y/n?")
    if checkforLoadBalanceRun.lower() == "y":
        return True
    elif checkforLoadBalanceRun.lower() =="n":
        return False
    else:
        print("Instructions were unclear. Cancelling execution of the program.")
        exit()

def checkBeforeNextRunOfLoadBalance():
    checkforLoadBalanceRun = raw_input("Do you want to run the load balancing software? y/n?")
    if checkforLoadBalanceRun.lower() == "y":
        return True
    elif checkforLoadBalanceRun.lower() =="n":
        return False
    else:
        print("Instructions were unclear. Cancelling execution of the program.")
        exit()
    

#A function designed to dump a json of the optimized values
def dict_optimized_values(dictOfOptimizedValues):# Place in optimize.py to return ntasks dictionary
    import json
    json_location_prefix = input("Enter a name for the json to store ntasks...(Do not add .json)") #Input the name of the file that the json will be stored to 
    json_location_exist = True#Boolean for checking if the name for the json file already exists in the directory
    while json_location_exist == True:#While loop that will repeat the naming process until the json file has a name that is not present in the designated directory
        if os.path.isfile(json_location_prefix+".json"):#Check the file name with .json file extension appended
            json_location_prefix =input("The current file name entered already exists. Please input a prefix for the file that does not exist.")# Allows the user to attempt to input another file name until the file name does not match any that is in the directory
    with open("/glade/work/$USER/optimum_json/"+json_location_prefix+".json", "w") as amendableFile:# Now writing the json content to the file
        json.dump(dictOfOptimizedValues, amendableFile)# The json contents are not being stored into the file 
"""
Reference: https://docs.python.org/3/library/subprocess.html
Reference: https://stackoverflow.com/questions/2231227/python-subprocess-popen-with-a-modified-environment
Reference: https://stackoverflow.com/questions/40697845/what-is-a-good-practice-to-check-if-an-environmental-variable-exists-or-not
"""
def intiate_base_load_balancing(timing_file_directory, completeDictionaryForCESMComponents):# Runs the cesm and load balancing python code
    import time# Time imported on to allow for waiting
    run_CESM_on_optimal_outputs = raw_input("Do you want to run CESM with the optimized values? y/n (yes or no)\n")#For determining whether CESM will be run with optimized values or not
    run_CESM_on_optimal_outputs_decision = False#Boolean value for determining whether or not to run CESM with optimal values
    if run_CESM_on_optimal_outputs == "y":#Conditional statemtn that is run if y is previously inputted
        run_CESM_on_optimal_outputs_decision = True#Shifts run_CESM_on_optimal_outputs_decision boolean variable to true 
    elif run_CESM_on_optimal_outputs == "n":
        run_CESM_on_optimal_outputs_decision = False#if run_CESM_on_optimal_outputs= "n" the run_CESM_on_optimal_outputs_decision boolean will be false
    mconda_environ = os.environ.copy()#Now making a clone of the environment to assign the environment variables of "PATH," "CIME_DIR," "PYTHONPATH," and "LB" for usage in running the Load balacing code
    mconda_environ["PATH"] = "/glade/u/home/"+mconda_environ["USER"]+"/miniconda2/bin/"#Assigning the "PATH" variable to the copied environment
    mconda_environ["CIME_DIR"] ="/glade/work/"+mconda_environ["USER"]+"/Load_Balancing_Work/cesm2.1.3/cime"#Assigning the "CIME_DIR" variable to the copied environment
    mconda_environ["PYTHONPATH"] = mconda_environ["CIME_DIR"]+"/scripts:"+mconda_environ["CIME_DIR"]+"/tools/load_balancing_tool"#Assigning the "PYTHONPATH" variable to the copied environment
    mconda_environ["LB"] = mconda_environ["CIME_DIR"]+"/tools/load_balancing_tool"#Assigning the "LB" variable to the copied environment
    time.sleep(2)#Give a period of time for the bash outputs to be shown before the python outputs are displayed
    if "CIME_DIR" in mconda_environ:#Check to see if the "CIME_DIR" environment variable has been set within the cloned environment
        print("The environment variable CIME_DIR has been set.")#The "CIME_DIR" environment variable has been set within the cloned environment 
    else: 
        print("Environment variable CIME_DIR has not been set.")#The "CIME_DIR" environment variable has not been set within the cloned environment 
        exit()#Exiting to keep the code from running into issues from "CIME_DIR" environment variable not being set
    if "PYTHONPATH" in mconda_environ:#Check to see if the "PYTHONPATH" environment variable has been set within the cloned environment
        print("The environment variable PYTHONPATH has been set.")#The "PYTHONPATH" environment variable has been set within the cloned environment
    else:
        print("Environment variable PYTHONPATH has not been set.")#The "PYTHONPATH" environment variable has not been set within the cloned environment
        exit()#Exiting to keep the code from running into issues from "PYTHONPATH" environment variable not being set
    if "LB" in mconda_environ:#Check to see if the "LB" environment variable has been set within the cloned environment
        print("The environment variable LB has been set.")#The "LB" environment variable has been set within the cloned environment
    else:
        print("Environment variable LB has not been set.")#The "LB" environment variable has not been set within the cloned environment
        exit()#Exiting to keep the code from running into issues from "LB" environment variable not being set
    print("Environment variables are successfully exported.")#Confirms the envrionment variables have been successfully exported
    show_environment_variables_paths(mconda_environ,mconda_environ["PATH"],mconda_environ["CIME_DIR"], mconda_environ["PYTHONPATH"], mconda_environ["LB"])#Check to ensure that the environment variables have been successfully loaded into the mconda_environ for usage in the load balancing script
    numOfIterations = input("How many times do you wish to run the load_balancing.py software?\n")#How many times the load balancing software is to be ran.
    for iterationRun in range(numOfIterations):#Runs the load balancing software for the designated number of loops
        #print(mconda_environ["LB"] + "/load_balancing_solve.py "+"--total-tasks "+" 108"+" --timing-dir"+ "/glade/work/"+mconda_environ["USER"]+"/Load_Balancing_Work/timing_files/ "+" --pe-output " +"new_env_mach_pes_run_"+str(iterationRun)+".xml")
        print("Load balancing run ",iterationRun," has been initiated")
        subcommand = mconda_environ["LB"]+"/load_balancing_solve.py --total-tasks "+completeDictionaryForCESMComponents["totaltasks"]+" --timing-dir "+os.getcwd()+"/timing/ --pe-output new_env_mach_pes_run_"+str(iterationRun)+".xml"
	subprocess.Popen([subcommand],stderr=subprocess.PIPE,stdout=subprocess.PIPE,shell=True,env=mconda_environ)
        print("Load balancing run is executed: ", iterationRun)
#

"""
Reference: https://docs.python.org/3/library/os.html
"""
def show_environment_variables_paths(created_environment,var_PATH,var_CIME_DIR, var_PYTHONPATH, var_LB):
    print("The environment mconda_environ is being examined:")
    print("The PATH environment variable: "+var_PATH)
    print("The CIME_DIR environment variable: "+var_CIME_DIR)
    print("The PYTHONPATH environment variable: "+var_PYTHONPATH)
    print("The LB environment variable: "+var_LB)
    print("The paths have been displayed")
    if os.path.isfile(var_LB+"/load_balancing_solve.py"):
        print("Load balancing python script is present.")
    else:
        print("Load balancing python script is not present")

"""subprocess.Popen(["export", "PATH=/glade/u/home/$USER/miniconda2/bin/"],shell=True)#subprocess.Popen("export", shell=True, env={"PATH":"/glade/u/home/$USER/miniconda2/bin/"},)#Start of the setup process for running the process
    subprocess.Popen(["export","CIME_DIR=/glade/work/$USER/Load_Balancing_Work/cesm2.1.3/cime"],shell=True)#subprocess.Popen("export", shell=True, env={"CIME_DIR":"/glade/work/$USER/Load_Balancing_Work/cesm2.1.3/cime"},)
    subprocess.Popen(["export","PYTHONPATH=$CIME_DIR/scripts:$CIME_DIR/tools/load_balancing_tool"],shell=True)#subprocess.Popen("export", shell=True, env={"PYTHONPATH":"$CIME_DIR/scripts:$CIME_DIR/tools/load_balancing_tool"},)
    subprocess.Popen(["export","LB=$CIME_DIR/tools/load_balancing_tool/"],shell=True)#subprocess.Popen("export", shell=True, env={"LB":"$CIME_DIR/tools/load_balancing_tool/"},)
    time.sleep(10)
"""     
initiate_first_runCESM() 
