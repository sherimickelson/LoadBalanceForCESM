#!/usr/bin/env python
"""Based on the Load Balancing code provided by Sheri Mickelson and Yuri Alekseev"""
"""Reference: https://stackoverflow.com/questions/20063/whats-the-best-way-to-parse-command-line-arguments"""
"""To be ran to call b2deg_alternative.py to allow better control and manipulation of parameters from the command line."""
"""Reference: https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file
https://stackoverflow.com/questions/45078474/required-is-an-invalid-argument-for-positionals-in-python-command
    
https://stackoverflow.com/questions/4666973/how-to-extract-the-substring-between-two-markers#:~:text=In%20python%2C%20extracting%20substring%20form,regular%20expression%20(%20re%20)%20module.&text=You%20can%20find%20first%20substring,what%20is%20after%20a%20substring.&text=%3E%3E%3E%20s%20%3D%20'%2Ftmp%2F10508.
https://stackoverflow.com/questions/4480075/argparse-optional-positional-arguments
    """
import argparse
import sys
import subprocess
import shutil
import os
import b2deg_alternative
from threading import Thread


"""
Reference: https://www.pythoncentral.io/pythons-time-sleep-pause-wait-sleep-stop-your-code/
Reference: https://stackoverflow.com/questions/53513/how-do-i-check-if-a-list-is-empty
Reference: https://stackoverflow.com/questions/26151669/valueerror-max-arg-is-an-empty-sequence
Reference: https://stackoverflow.com/questions/3964681/find-all-files-in-a-directory-with-extension-txt-in-python
Reference: https://stackoverflow.com/questions/123198/how-do-i-copy-a-file-in-python
"""
   
def initiate_first_runCESM():#Function that intiates the default CESM run and in turn allows for succeeding runs of the load balancing software and the CESM model software.
    comd_line_cesm_parser = argparse.ArgumentParser(description = "Command line arguments submitted to the python script for CESM. Supply the maximum amount of processors to be allocated to CESM.")# The command line arguments are being read by this object for further usage and initiating the CESM model run
    comd_line_cesm_parser.add_argument("selected_maxtasks", help="The maximum amount of processors to be allocated to CESM runs must be submitted.")#Adds the max tasks argument ot the command line input for parsing.
    comd_line_cesm_parser.add_argument("--compset_designation", help="The compset that will be specified for the CESM model.")#Adds the compset argument ot the command line input for parsing.
    comd_line_cesm_parser.add_argument("--sim_time_designation", help="The measure of time that will be specified for the CESM model.")#Adds the compset argument ot the command line input for parsing.
    comd_line_cesm_parser.add_argument("--sim_time_unit", help="The unit of times that will be specified for the CESM model.")#Adds the compset argument ot the command line input for parsing.
    comd_line_cesm_parser.add_argument("--scaling-factor-for-processors", help="The input for the scaling that will be utilized for concurrent building and running of CESm models.")#Adds the compset argument ot the command line input for parsing.
    cesm_comd_args = comd_line_cesm_parser.parse_args()#The collection of parsing arguments to launch the CESM model with. 
    targeted_timing_files_directory, completeCESMComponentDictionaryForLoad = b2deg_alternative.default_max_tasks_json(cesm_comd_args)#Running the function Initiating CESM first to generate the timing files in the timing directory to enable the load_balancing_solve.py to run with the generated timing files for optimization
    continueRunProcess = True# A record of user response of whether the user wants to continue with initiating load balancing and CESM runs
    while(continueRunProcess==True):#The loop is here for continuing the process of running the load balancing code then running the CESM models.
        continueRunProcess = checkBeforeNextRunOfLoadBalance()#Checking if the user desires to run the load balancing code for this iteration.
        loopControlForCESMAndLoadBalance(continueRunProcess)#If the user does not want to run the load balancing code, the while loop will be broken.
        intiate_base_load_balancing(targeted_timing_files_directory, completeCESMComponentDictionaryForLoad) #Load balancing code is initiated. Will produce a fresh json file necessary for the running of a CESM model.
        optimized_values_cesm_json = b2deg_alternative.retrieve_recent_cesm_ntasks_json_file(len(targeted_timing_files_directory))#Running the retrieve_recent_cesm_ntasks_json_file() function that will retrieve the most recently created json files. The recent json files returned to be used by later CESM models.
        continueRunProcess = checkBeforeNextRunOfCESM() #Checking if the user desires to build the CESM model for this iteration.
        loopControlForCESMAndLoadBalance(continueRunProcess)#If the user does not want to run the CESM model, the while loop will be broken.
        target_directory_for_CESM = b2deg_alternative.folder_name() 
        targeted_timing_files_directory = b2deg_alternative.optimize_values_allocation_run(optimized_values_cesm_json,target_directory_for_CESM)#Returning timing files directories for the CESM model that will be built and ran

def collect_timing_files_one_folder(list_record_of_timing_files):#The function collect_timing_files_one_folder() takes the list with the directories to the timing files as an argument and will connect the timing files from preceding CESM runs.
    stroageDirForTiming ="/glade/work/"+os.environ["USER"]+"/load_balancing_access_timing/"#The directory that the timing files will be
    if os.path.isdir(stroageDirForTiming):#Checks if the time file storage directory is present
        pass
    else:#If the time file storage directory is not present, create said directory
        os.mkdir(stroageDirForTiming)
    import glob#importing the glob library of python
    for fileItem in list_record_of_timing_files:#FOr loop that will acquire each timing file from the timing file directory.
        acquired_timing_file=glob.glob(fileItem+"cesm_timing.*")#Stores the collected timing file in a list
        timingFileCopyCommand = ["cp",acquired_timing_file[0],stroageDirForTiming]#Command that copies the the timing file to the sircrectory that was made to store timing files
        subprocess.check_call(timingFileCopyCommand,shell=False)#Subprocess runs the copy command
    
def loopControlForCESMAndLoadBalance(recordForControlCheck):#loopControlForCESMAndLoadBalance() function is used to check if the user wants the software to continue for load balancing and cesm executions.
    if recordForControlCheck == True:#Do nothing
        pass
    else:#Exit the code, the user no longer wants to continue
        exit()

def checkBeforeNextRunOfCESM():#checkBeforeNextRunOfCESM() function is used to acquire the information as to whether user wants to run a CESM model.
    checkforLoadBalanceRun = raw_input("Do you want to run the CESM software? y/n?")#Takes the user's response.
    if checkforLoadBalanceRun.lower() == "y":#Yes, continue contnue with execution of the CESM run
        return True
    elif checkforLoadBalanceRun.lower() =="n":#No, do not continue with execution of the CESM run
        return False
    else:
        print("Instructions were unclear. Cancelling execution of the program.")
        exit()

def checkBeforeNextRunOfLoadBalance():#checkBeforeNextRunOfLoadBalance() function Ensures that the user wants to run the next iteration of the load balance software
    checkforLoadBalanceRun = raw_input("Do you want to run the load balancing software? y/n?")#Asks user if they want to run the load balancing software again.
    if checkforLoadBalanceRun.lower() == "y":#Run the load balancing software this iteration.
        return True
    elif checkforLoadBalanceRun.lower() =="n":#Do not run the load balancing software this iterarion.
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
    print("Load balancing software initiated.")
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
    numOfIterations = 1#How many times the load balancing software is to be ran.
    collectionOfThreadsForLoadBalancing= {}#Dictionary to keep track of the threads that will be generated dynamically in the for loop below.
    collect_timing_files_one_folder(timing_file_directory)
    for iterationRun in range(numOfIterations):#Runs the load balancing software for the designated number of loops
        threadDesignatedDictionaryOfCESMComponentParameters = completeDictionaryForCESMComponents[iterationRun]
        produced_thread = Thread(target=loadBalanceThreadSpinUpConstruct, args=(iterationRun, mconda_environ, threadDesignatedDictionaryOfCESMComponentParameters, timing_file_directory,))#The construction of a thread to with necessary arguments for the launching execution of load balancing code
        produced_thread.start()#Initiation of said thread with previously assigned arguments
        collectionOfThreadsForLoadBalancing.update({iterationRun:produced_thread})#Numerical key whose value is the thread that was previously intiated. 
    for numericalIdentityOfThreadKey in collectionOfThreadsForLoadBalancing:#For loop for managing the multiple threads that are created.
        collectionOfThreadsForLoadBalancing[numericalIdentityOfThreadKey].join()#Ensuring that all threads will wait until all the threads have completed their processes. Then continue with the code execution.
    print("All load balancing processes have finished.")
#
def loadBalanceThreadSpinUpConstruct(numericalIdentifierForThread, mconda_designated_environ, entireDictionaryOfCESMComponents, assortment_of_directories_for_timing_files):#loadBalanceThreadSpinUpConstruct() function the executes the load balancing the python code  with the arguments provided for the function.
    print("Load balancing run ", numericalIdentifierForThread," has been initiated")
    subcommand = [mconda_designated_environ["LB"]+"/load_balancing_solve.py","--total-tasks",str(entireDictionaryOfCESMComponents["totaltasks"]),"--timing-dir","/glade/work/"+os.environ["USER"]+"/load_balancing_access_timing/","--pe-output","new_env_mach_pes_run_"+str(numericalIdentifierForThread)+".xml"]#The command that will be utilized to executed for an instance of the load balancing code. Note that it should be in the same format as what would be submitted to the command line.
    #print(subcommand)#Perint the contents of the command to be submitted to make sure that the formatis correct and the inputs are accurate.
    subprocess.check_call(subcommand,shell=False,env=mconda_designated_environ)#subprocess that will execute the above command in the shell.
    print("Load balancing run is executed: ", numericalIdentifierForThread)
"""
Reference: https://docs.python.org/3/library/os.html
"""
def show_environment_variables_paths(created_environment,var_PATH,var_CIME_DIR, var_PYTHONPATH, var_LB):#For checking the environmental variables to make sure they are accurately submitted.
    print("The environment mconda_environ is being examined:")#The environment variables are being printed to verify that they 1. exist and 2. are correctly assigned.
    print("The PATH environment variable: "+var_PATH)#The PATH variable is printed to verify that it has been properly assigned
    print("The CIME_DIR environment variable: "+var_CIME_DIR)#The CIME_DIR variable is printed to verify that it has been properly assigned
    print("The PYTHONPATH environment variable: "+var_PYTHONPATH)#The PYTHONPATH variable is printed to verify that it has been properly assigned
    print("The LB environment variable: "+var_LB)#The LB variable is printed to verify that it has been properly assigned
    print("The paths have been displayed")#confirming path variables are assigned
    if os.path.isfile(var_LB+"/load_balancing_solve.py"):#Checking that Load balaclancing python script is available
        print("Load balancing python script is present.")
    else:
        print("Load balancing python script is not present")
        exit()#If load balancing code is not present, then exit the code.

   
initiate_first_runCESM() 
