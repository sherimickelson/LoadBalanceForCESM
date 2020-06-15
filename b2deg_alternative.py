#!/usr/bin/env python
"""Author: Thomas Johnson III"""
"""Based off of b2deg.sh written by Brian Dobbins"""
"""May 27th, 2020"""
"""Reference: https://github.com/ESMCI/cime/blob/master/tools/load_balancing_tool/load_balancing_submit.py"""
"""Reference:https://www.freecodecamp.org/news/python-for-system-administration-tutorial/"""
"""Reference: https://stackoverflow.com/questions/4256107/running-bash-commands-in-python"""
"""Reference: https://www.journaldev.com/24935/python-set-environment-variable"""
"""Reference: https://stackoverflow.com/questions/13222808/how-to-run-external-executable-using-python/13222809"""
"""Reference: https://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder-using-python"""
"""Reference:https://www.geeksforgeeks.org/multithreading-python-set-1/"""
"""Reference: https://stackoverflow.com/questions/55529319/how-to-create-multiple-threads-dynamically-in-python"""
import os
import sys
import subprocess
import shutil
import glob
import threading
import copy

def prototype_run():#Original implementation from the bash script supplied by Brian Dobbins
    """Checking if the first argument of the file directory has been submitted."""
    if sys.argv[1]:
        pass
    else:
        print("To use: b2deg_alternative.py <case name>")
        exit()


    """Does the file directory already exist? Now we check:"""
    if os.path.isfile(sys.argv[1]):
        print("The directory or file " +sys.argv[1] +" already exists.")
        exit()

    """Optional: Verifying the project environment variable is set."""
    if 'PROJECT' in os.environ:
        print("The PROJECT environment has been set.")
    else:
        print("The PROJECT has not been set. Aborting...")
        exit()

    """Setting up the case."""
    """Setting the version of CESM to be utilized."""
    os.environ["CESMROOT"] = "/glade/p/cesm/releases/cesm2_1_1/"

    for runCount in range(4):
        """Creation of the case."""
        subprocess.call([os.environ["CESMROOT"]+"/cime/scripts/create_newcase", "--case",sys.argv[1]+"proc_"+str(optimized_values_dict["totaltasks"])+"_"+str(runCount),"--compset","B1850","--res","f19_g17","--project",os.environ["PROJECT"]])

        """Assuming there are no errors, we change the directory."""
        os.chdir(sys.argv[1])
        processorMultiplier = 2**runCount
        """Now for altering the processor counts:"""
        subprocess.call(["./xmlchange", "NTASKS_ATM="+processorMultiplierFunc(sys.argv[2], processorMultiplier)])
        subprocess.call(["./xmlchange", "NTASKS_CPL="+processorMultiplierFunc(sys.argv[2], processorMultiplier)])
        subprocess.call(["./xmlchange", "NTASKS_OCN="+processorMultiplierFunc(sys.argv[2], processorMultiplier)])
        subprocess.call(["./xmlchange", "NTASKS_WAV="+processorMultiplierFunc(sys.argv[2], processorMultiplier)])
        subprocess.call(["./xmlchange", "NTASKS_GLC="+processorMultiplierFunc(sys.argv[2], processorMultiplier)])
        subprocess.call(["./xmlchange", "NTASKS_ICE="+processorMultiplierFunc(sys.argv[2], processorMultiplier)])
        subprocess.call(["./xmlchange", "NTASKS_ROF="+processorMultiplierFunc(sys.argv[2], processorMultiplier)])
        subprocess.call(["./xmlchange", "NTASKS_LND="+processorMultiplierFunc(sys.argv[2], processorMultiplier)])
        subprocess.call(["./xmlchange", "NTASKS_ESP="+processorMultiplierFunc("1", processorMultiplier)])

        """ROOTPE Values are being established"""
        subprocess.call(["./xmlchange", "ROOTPE_ATM=0"])
        subprocess.call(["./xmlchange", "ROOTPE_CPL=0"])
        subprocess.call(["./xmlchange", "ROOTPE_OCN="+processorMultiplierFunc(sys.argv[2], processorMultiplier)])
        subprocess.call(["./xmlchange", "ROOTPE_WAV=0"])
        subprocess.call(["./xmlchange", "ROOTPE_GLC=0"])
        subprocess.call(["./xmlchange", "ROOTPE_ICE=0"])
        subprocess.call(["./xmlchange", "ROOTPE_ROF=0"])
        subprocess.call(["./xmlchange", "ROOTPE_LND=0"])
        subprocess.call(["./xmlchange", "ROOTPE_ESP=0"])

        """setting the default parameters"""
        xmlchangeDefaultOptions()
        startCESMProcess()


        
def processorMultiplierFunc(numOfProcessors, processorMultiplier):#processorMultiplierFunc() multiplies the number of processors allocated per run of a specified CESM model.
    if type(numOfProcessors) == type(2):#The if statement checks to make sure that the supplied input is not an integer. It it is, the input is changed to an string.
        numOfProcessors = str(numOfProcessors)
    print("The number of processors: "+numOfProcessors)
    numericalResult = int(numOfProcessors)*2**processorMultiplier#The processor value is multiplied by 2^(the iteration of CESM being ran)
    strResult = str(numericalResult)#Convert the integer back to a string
    print("The string result of the number of processors: "+strResult)
    return strResult#Returning the number fo processors that are allocated
    
"""Reference: https://www.geeksforgeeks.org/convert-json-to-dictionary-in-python/"""
def optimize_values_allocation_run(assortment_of_optimized_values, target_directory_for_CESM):#The optimize_values_allocation_run function takes values from jsons that have the specifications for the number of processors for each component as well as the totla number of processors
    """Does the file directory already exist? Now we check:"""
    if os.path.isfile(target_directory_for_CESM):#If statement that checks that the target dirctory specified does not already exist...
        print("The directory or file " +target_directory_for_CESM +" already exists.")#If the specified directory exists, this message will be printed out before exiting the program
        exit()

    """Optional: Verifying the project environment variable is set."""
    if 'PROJECT' in os.environ:#Checks that the PROJECT environment variable was set.
        print("The PROJECT environment has been set.")#Confirms that the PROJECT environment variable is 
    else:
        print("The PROJECT has not been set. Aborting...")#exiting from the PROJECT variable not being set
        exit()

    """Setting up the case."""
    """Setting the version of CESM to be utilized."""
    os.environ["CESMROOT"] = "/glade/p/cesm/releases/cesm2_1_1/"#The CESMROOT environemnt variable is set.
    import json#imports the json library of python
    processorIncrementationLoops = input("Number of times that the CESM model will be ran shall be ran.\n")#Number of iterations to run CESM, will be doubling the number of processors used each time based on the values supplied by the json files that will be loaded

    #Initiating new function for simplistic threading
    collectThread = {}#A dictionary that will be used to store the number of threads that will be generated dynamically
    assortmentOfTimingFileDirectory = []#The list is to store the directories of the timing files to be used in the load balancing software.
    accessingTimingFileDirectory = False#The accessingTimingFileDirectory variable is utilized to identify whether assortmentOfTimingFileDirectory is being written to by a thread.
    for runCount in range(processorIncrementationLoops):#For loop of the the specified number of loops as indicated earlier in the processorIncrementationLoops variable. The number of processors will double for each looop that is initiated.
        collection_of_optimized_values = assortment_of_optimized_values[runCount]#Access the specific dictionary of CESM parameter values that has the key matching the value of the current iteration
        CESMprocess = Thread(target=prepCESM, args=(processorIncrementationLoops, collection_of_optimized_values, target_directory_for_CESM, assortmentOfTimingFileDirectory, accessingTimingFileDirectory, runCount,))#Starts a new CESM model be setup, built and run. Each one of the threads can be accessed using the keys of the dictionary they are stored in to access each thread as a value for the respective key in the dictionary.
        CESMprocess.start()#Initiates the CESM model to setup, build and run with the given arguments.
        collectThread.uptdate(runCount:CESMprocess)#Stores access to the thread within a disctionary with a numeric key for each thread.
    for threadingNumber in collectThread:#For managing the threads that have been initiated.
        collectThread[threadingNumber].join()# FOr wnsuring that all the threads wait for the the others to conclude to prevent issues with later parts of tf the code execution.
    return timing_file_directory, collection_of_optimized_values#Returns the dictionary of values for the CESM parameters and the list of timing files.

"""The CESM setup, build, and submit commands are defined in the startCESMProcess() function. The setup process followed by the build process followed by the submission to the queue."""

def startCESMProcess():
    subprocess.check_call(["./case.setup"])#The setup for the CESM model is performed using this command
    subprocess.check_call(["./case.build"])#The building of the CESM model is performed using this command
    subprocess.check_call(["./case.submit"])#The submission of the CESM model to the job queue is performed using this command 
    print("The CESM model has been successfully submitted.")
    os.chdir("../")# moves to the upper level directory

"""Remaining default options for CESM are set using the xmlchangeDefaultOptions() function."""
def xmlchangeDefaultOptions():
    subprocess.call(["./xmlchange", "STOP_N=1"])
    subprocess.call(["./xmlchange", "STOP_OPTION=ndays"])
    subprocess.call(["./xmlchange", "REST_OPTION=never"])
    subprocess.call(["./xmlchange", "COMP_RUN_BARRIERS=TRUE"])
    subprocess.call(["./xmlchange", "DOUT_S=FALSE"])
    subprocess.call(["./xmlchange", "GMAKE_J=6"])
    subprocess.call(["./xmlchange", "JOB_WALLCLOCK_TIME=0:20"])# Allocated the amount time the job is allowed to run for upon submission to the queue.
"""
Reference: https://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder-using-python
Reference: https://www.pythoncentral.io/pythons-time-sleep-pause-wait-sleep-stop-your-code/
"""
def checkTimingDirectoryListEdit(recordOfTimingDirectoryAccesses):
    for record in recordOfTimingDirectoryAccesses:
        if record == True:
            return True
    return False
            
def assignValuesForNTASKS(assortmentOfModelComponentsValues, assortmentOfInvolvedComponents, numericalThreadIdentifier):
    #function to catch any componenets that have not been assigned a value from ntasks. Will be scaled based on the numerical identifier of the thread.
    #Possible for loop implementation
    xmlNTASKSParameter =[]
    for componentNumericalIdentifier in assortmentOfInvolvedComponents:
        xmlNTASKSParameter = ["./xmlchange NTASKS_"+assortmentOfInvolvedComponents[componentNumericalIdentifier].upper()+"="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["ntasks"], "ntasks", assortmentOfInvolvedComponents[componentNumericalIdentifier]),numericalThreadIdentifier))])#The number of processors that will be allocated to the specified model component
        subprocess.call(xmlNTASKSParameter)
        
    #subprocess.call(["./xmlchange", "NTASKS_ATM="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["ntasks"], "ntasks", assortmentOfInvolvedComponents[0]),numericalThreadIdentifier))])#The number of processors that will be allocated to the "ATM" model component
    #subprocess.call(["./xmlchange", "NTASKS_CPL="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["ntasks"], "ntasks", assortmentOfInvolvedComponents[1]),numericalThreadIdentifier))])#The number of processors that will be allocated to the "CPL" component
    #subprocess.call(["./xmlchange", "NTASKS_OCN="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["ntasks"], "ntasks", assortmentOfInvolvedComponents[2]),numericalThreadIdentifier))])#The number of processors that will be allocated ot the "OCN" component
    #subprocess.call(["./xmlchange", "NTASKS_WAV="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["ntasks"], "ntasks", assortmentOfInvolvedComponents[3]),numericalThreadIdentifier))])#The number of processors that will be allocated to the "WAV" component
    #subprocess.call(["./xmlchange", "NTASKS_GLC="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["ntasks"], "ntasks", assortmentOfInvolvedComponents[4]),numericalThreadIdentifier))])#The number of processors that will be allocated to the "GLC" component
    #subprocess.call(["./xmlchange", "NTASKS_ICE="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["ntasks"], "ntasks", assortmentOfInvolvedComponents[5]),numericalThreadIdentifier))])#The number of processors that will be allocated to the "ICE" component
    #subprocess.call(["./xmlchange", "NTASKS_ROF="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["ntasks"], "ntasks", assortmentOfInvolvedComponents[6]),numericalThreadIdentifier))])# The number of processors that will be allocated to the "ROF" component
    #subprocess.call(["./xmlchange", "NTASKS_LND="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["ntasks"], "ntasks", assortmentOfInvolvedComponents[7]),numericalThreadIdentifier))])# The number of processors that will be allocated to the "LND" component
    #subprocess.call(["./xmlchange", "NTASKS_ESP="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["ntasks"], "ntasks", assortmentOfInvolvedComponents[8]),numericalThreadIdentifier))])#The number of processors that will be allocated to the "ESP" component
    
def assignValuesForROOTPE(assortmentOfModelComponentsValues, assortmentOfInvolvedComponents, numericalThreadIdentifier):
    xmlROOTPEParameter =[]
    for componentNumericalIdentifier in assortmentOfInvolvedComponents:
        xmlNTASKSParameter = ["./xmlchange ROOTPE_"+assortmentOfInvolvedComponents[componentNumericalIdentifier].upper()+"="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["rootpe"], "rootpe", assortmentOfInvolvedComponents[componentNumericalIdentifier]),numericalThreadIdentifier))])#The number of processors that will be allocated to the specified model component
        subprocess.call(xmlNTASKSParameter)
    #subprocess.call(["./xmlchange", "ROOTPE_ATM="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["rootpe"], "rootpe", assortmentOfInvolvedComponents[0]),numericalThreadIdentifier))])#ROOTPE value assigned for the "ATM" component
    #subprocess.call(["./xmlchange", "ROOTPE_CPL="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["rootpe"], "rootpe", assortmentOfInvolvedComponents[1]),numericalThreadIdentifier))])#ROOTPE value assigned for the "CPL" component
    #subprocess.call(["./xmlchange", "ROOTPE_OCN="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["rootpe"], "rootpe", assortmentOfInvolvedComponents[2]),numericalThreadIdentifier))])#ROOTPE value assigned for the "OCN" component
    #subprocess.call(["./xmlchange", "ROOTPE_WAV="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["rootpe"], "rootpe", assortmentOfInvolvedComponents[3]),numericalThreadIdentifier))])#ROOTPE value assigned for the "WAV" component
    #subprocess.call(["./xmlchange", "ROOTPE_GLC="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["rootpe"], "rootpe", assortmentOfInvolvedComponents[4]),numericalThreadIdentifier))])#ROOTPE value assigned for the "GLC" component
    #subprocess.call(["./xmlchange", "ROOTPE_ICE="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["rootpe"], "rootpe", assortmentOfInvolvedComponents[5]),numericalThreadIdentifier))])#ROOTPE value assigned for the "ICE" component
    #subprocess.call(["./xmlchange", "ROOTPE_ROF="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["rootpe"], "rootpe", assortmentOfInvolvedComponents[6]),numericalThreadIdentifier))])#ROOTPE value assigned for the "ROF" component
    #subprocess.call(["./xmlchange", "ROOTPE_LND="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["rootpe"], "rootpe", assortmentOfInvolvedComponents[7]),numericalThreadIdentifier))])#ROOTPE value assigned for the "LND" component
    #subprocess.call(["./xmlchange", "ROOTPE_ESP="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["rootpe"], "rootpe", assortmentOfInvolvedComponents[8]),numericalThreadIdentifier))])#ROOTPE value assigned for the "ATM" component


def assignValuesForNTHRDS(assortmentOfModelComponentsValues, assortmentOfInvolvedComponents, numericalThreadIdentifier):
    xmlNTASKSParameter =[]
    for componentNumericalIdentifier in assortmentOfInvolvedComponents:
        xmlNTASKSParameter = ["./xmlchange NTHRDS_"+assortmentOfInvolvedComponents[componentNumericalIdentifier].upper()+"="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["nthrds"], "nthrds", assortmentOfInvolvedComponents[componentNumericalIdentifier]),numericalThreadIdentifier))])#The number of processors that will be allocated to the specified model component
        subprocess.call(xmlNTASKSParameter)
    #subprocess.call(["./xmlchange", "NTHRDS_ATM="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["nthrds"], "nthrds", assortmentOfInvolvedComponents[0]), numericalThreadIdentifier))])#NTHRDS value assigned for the "ATM" component
    #subprocess.call(["./xmlchange", "NTHRDS_CPL="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["nthrds"], "nthrds", assortmentOfInvolvedComponents[1]), numericalThreadIdentifier))])#NTHRDS value assigned for the "CPL" component
    #subprocess.call(["./xmlchange", "NTHRDS_OCN="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["nthrds"], "nthrds", assortmentOfInvolvedComponents[2]), numericalThreadIdentifier))])#NTHRDS value assigned for the "OCN" component
    #subprocess.call(["./xmlchange", "NTHRDS_WAV="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["nthrds"], "nthrds", assortmentOfInvolvedComponents[3]), numericalThreadIdentifier))])#NTHRDS value assigned for the "WAV" component
    #subprocess.call(["./xmlchange", "NTHRDS_GLC="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["nthrds"], "nthrds", assortmentOfInvolvedComponents[4]), numericalThreadIdentifier))])#NTHRDS value assigned for the "GLC" component
    #subprocess.call(["./xmlchange", "NTHRDS_ICE="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["nthrds"], "nthrds", assortmentOfInvolvedComponents[5]), numericalThreadIdentifier))])#NTHRDS value assigned for the "ICE" component
    #subprocess.call(["./xmlchange", "NTHRDS_ROF="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["nthrds"], "nthrds", assortmentOfInvolvedComponents[6]), numericalThreadIdentifier))])#NTHRDS value assigned for the "ROF" component
    #subprocess.call(["./xmlchange", "NTHRDS_LND="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["nthrds"], "nthrds", assortmentOfInvolvedComponents[7]), numericalThreadIdentifier))])#NTHRDS value assigned for the "LND" component
    #subprocess.call(["./xmlchange", "NTHRDS_ESP="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["nthrds"], "nthrds", assortmentOfInvolvedComponents[8]),numericalThreadIdentifier))])#NTHRDS value assigned for the "ESP" component


def prepCESM(processorIncrementationLoops, collection_of_optimized_values, target_directory_for_CESM, assortmentOfTimingFileDirectory, accessingTimingFileDirectory, threadIdentifier):#prepCESM() function serves to prepare the basic configurations for the setup, building and submission of the CESM model.
    """Creation of the case."""
    print("Printing the CESMROOT environment variable ",os.environ["CESMROOT"])#Visual check over for the CESMROOT environment variable
    print("The directory for the CESM contents: "+ target_directory_for_CESM)#Visual check over the for the directory that CESM will be building contents within
    print("Now the dictionary containing the value for the total amount of tasks:")#printing the dictionary containing the total amount of tasks
    print(total_tasks_dict)#The dictionary containg the total number of tasks
    print("The PROJECT environment variable: ", os.environ["PROJECT"])#Visual confirmation of the PROJECT environment variable being passed
    commandRunCESM =os.environ["CESMROOT"]+"cime/scripts/create_newcase "+"--case "+target_directory_for_CESM+"_processors_"+processorMultiplierFunc(str(collection_of_optimized_values["totaltasks"]),threadIdentifier)+"_run"+str(threadIdentifier)+" --compset "+"B1850 "+"--res "+"f19_g17 "+"--project "+os.environ["PROJECT"]#The command to be ran in the shell for constructing a new instance of CESM to run.
    print("CESM commands:")
    print(commandRunCESM)#Visual check over te commands to be ran for CESM
    subprocess.call([commandRunCESM],stderr=subprocess.PIPE,stdout=subprocess.PIPE,shell=True,env=os.environ)#Initiating the command line script to be ran within bash

    """Assuming there are no errors, we change the directory."""
    os.chdir(target_directory_for_CESM+"_processors_"+processorMultiplierFunc(str(collection_of_optimized_values["totaltasks"]),runCount)+"_run"+str(threadIdentifier))#Changes the directory for the CESM project
    #name_of_json = input("What is the name of the json file where the data is stored?")


    """Now for altering the processor counts:"""
    componentDictionary = {0:"atm", 1:"cpl", 2:"ocn", 3:"wav", 4:"glc",5:"ice",6:"rof", 7:"lnd", 8:"esp"}#A dictionary of the components for the CESM model to build with
    #function to catch any componenets that have not been assigned a value from ntasks. Will be scaled based on the numerical identifier of the thread.
    assignValuesForNTASKS(collection_of_optimized_values, componentDictionary, threadIdentifier)#Assigning the NTASKS values.

    """ROOTPE Values are being established"""
    #The ./xmlchange command rewrites xml files that provide parameters for building the project
    assignValuesForROOTPE(collection_of_optimized_values, componentDictionary, threadIdentifier)#Assigning the ROOTPE values.

    """NTHRDS Values are being established"""
    #The ./xmlchange command rewrites xml files that provide parameters for building the project
    assignValuesForNTHRDS(assortmentOfModelComponentsValues, assortmentOfInvolvedComponents, numericalThreadIdentifier)#Assigning the NTHRDS values.

    timing_file_directory =os.getcwd()+"timing/"#Concatenates the directory with that of the timing files subdirectory.
    """setting the default parameters"""
    xmlchangeDefaultOptions()#Calls the xmlchangeDefaultOptions() function that will call for the remaining values in the xml files to be taken
    startCESMProcess()#Runs the CESM commands necessary for prepping and running a CESM project

    print("CESM job is submitted")
    #print("This is run: "+str(runCount))
    print("Conclusion of CESM run...")
    accessControl = True#The accessControl variable is used to make sure that the current thread that the prepCESM code is in does not attempt to write a timing to the list of timing file directories at the same time as another timing file directory.
    while(accessControl == True):#Initiate a loop for checking the access to the timing file directory.
        accessControl = checkTimingDirectoryListEdit(accessingTimingFileDirectory)#checks the value of the accessControl in order to verify the assortmentOfTimingFileDirectory is not being accessed at a given time  by a different thread. 
        if accessControl == True:#When accessControl is True, this indicates that the assortmentOfTimingFileDirectory is being accessed and thus this thred will be unable to write to assortmentOfTimingFileDirectory until the thread currently accessing assortmentOfTimingFileDirectory free to access
            pass
        else:#When the accessControl value is False
            accessingTimingFileDirectory[threadIdentifier] = True#First, make sure to write to the accessingTimingFileDirectory to ensure that the thread as a True value to make sure that the other threads have been restricted.
            assortmentOfTimingFileDirectory.append(timing_file_directory)#Appends the timing file directory to the assortmentOfTimingFileDirectory to add another entry to record the total number of timing file directories. 
            accessingTimingFileDirectory[threadIdentifier] = False# The accessingTimingFileDirectory list accessed after the thread is finished writing to the assortmentOfTimingFileDirectory list to permit the next thread to access assortmentOfTimingFileDirectory to write to it.
            accessControl = False#Set accessControl is set to False to force the while loop to break.
            
    print("Timing file directory appended for "+ str(threadIdentifier))
     



def checkComponentValue(componentOptimizedValues, categoryForValues, modelComponent):#check checkComponentValue ensures that each component will be passed a value and if one is not present then the value passed will be 1
    if categoryForValues == "ntasks":#For when the NTASKS parameters are being set. 
        if modelComponent in componentOptimizedValues:#An if condition that pairs the componenets with the values for their parameters.
            return componentOptimizedValues[modelComponent]#Returns the value of the NTASKS parameter for the respective CESM componenet.
        else:
            return "1"# Otherwise NTASKS is assigned to be 1
    else:
        if modelComponent in componentOptimizedValues:#An if condition for assigning the values of ROOTPE and NTHRDS
            return componentOptimizedValues[modelComponent]#Assigns the respective value for the ROOTPE and NTHRDS parameters for the CESM model.
        else:
            return "0"

def retrieve_recent_cesm_ntasks_json_file(numberOfRetrievals):#retrieve_recent_cesm_ntasks_json_file() function is utilized to retrieve the most recent json files that are generated by the load balancing code.
    import json#importing json module of python.
    directory_prefix = "/glade/work/"+os.environ["USER"]+"/optimum_json/"#A directory for storing the json files that are created from the load balancing code to preserve the optimal parameters for the ran CESM model.
    model_CESM_values_dict ={}#For storing the optimal CESM parameter values that can be used to optimize CESM models.
    collection_of_files = []#A list for the file directories that will be used for accessing the json files that are generated.
    if prefix_keyword=="optimization_dictionaries":#Makes sure that the correct title for the json that will be created.
        collection_of_files = glob.glob("/glade/work/"+os.environ["USER"]+"/optimum_json/optimization_dictionaries*.json")#acquiring the optimization_dictionaries json files to acquire the most recent variations that have been produced from the recent CESM model run.
    else:
        print("An error has occurred in the json searching process...")#The error for is being printed out to inform the user of what has occurred
        print("Please reexamine process...")
        print("Exiting...")
        exit()
    print("The current inventory of json files:")#Printing the list of json files that havve been accumulated in the collection_of_files list.
    print(collection_of_files)
    if not collection_of_files:#If there are collection_of_files is empty the result is that the function waits for 10 second intervals to give time for earlier components of the script to have time to write the json files
        while(collection_of_files == []):#While the collection_of_files remains an empty list... there is a wait of 10 seconds
            import time
            time.sleep(10)
            json_file_storage =False#Used to verify that the correct number of recent json files have been stored within the collection_of_files
            while(json_file_storage == False):#While loop that will continue as long as the correct number of json files have not been acquired.
                collection_of_files = glob.glob("/glade/work/"+os.environ["USER"]+"/optimum_json/optimization_dictionaries*.json")#Accumulating the recently created json files directories within the collection_of_files
                if ("/glade/work/"+os.environ["USER"]+"/optimum_json/optimization_dictionaries*.json" not in collection_of_files) and (len(collection_of_files)< numberOfRetrievals):#If statement that ensures the correct number of json files have been collected. If the correct number has not be collected, the process of collecting the json files will be recollected
                    time.sleep(4)#Waiting four seconds
                    print("Still searching for json files")
                else: #Once all the recent json files are created form the CESM model runs
                    break#Exit the loop
    else:#Once te json files have been collected
        recentVersionsJSON = []#The list of most recently created json directories
        for counter in range(numberOfRetrievals):#For loop that counts up to the number of expected json files to be retrieved
            name_of_recent_json_file = max(collection_of_files, key = os.path.getctime)#Retrieves the most recently created json file.
            recentVersionsJSON.append(name_of_recent_json_file)#Appends the most recently created json file to the list of recently generated json files that will be passed to the next iteration of CESM.
            collection_of_files.remove(name_of_recent_json_file)#Remove the most recently added file path in recentVersionsJSON from the collection_of_files list
        dictionaryOfRecentJSONs = {}#The dictionary for the recent jsons that have been created
        counterNum = 0#For generating keys for a dictionary starting with 0
        for jsonFile in recentVersionsJSON:#The iteration through the file paths for the the collected json files collected here
            with open(jsonFile) as location_of_dict:#Opening a reading process to extract the dictionary values that were stored within the json
                model_CESM_values_dict = json.load(location_of_dict)#The dictionary of optimized CESM values is extracted.
                print("Structure of the dictionary: ")
                print(model_CESM_values_dict)
                dictionaryOfRecentJSONs.update(counterNum:model_CESM_values_dict)#Adding the dictionary of optimized CESM parameters to the dictionary that contains the entiretly of the recent json files that were collected
             counterNum+=1#increase the value by 1
        return dictionaryOfRecentJSONs#returns the json of relevant CESM parameter values

def folder_name():#The function of folder_name() is used for the purpose of getting the file name for CESM as well as checking if the file does not already exist within the directory
    named_folder = raw_input("Please name the folder that the CESM contents will be stored within...\n")#Input for the name of the file
    print("The name of the folder is "+ named_folder)
    while(os.path.isfile(named_folder)):#As long as the name of the folder exists in the directory, ask for a new name to be used
        print("Please choose a new name for the folder. The name that was entered happens to already exist.")
        named_folder = raw_input("Input the new name of the folder.\n")#New input name
    return named_folder# Return the submitted the name for the folder

def checkSumOfTasksToMaxTasks(maxQuantityOfTasks,cesmTasksCalculated):#For ensuring that a calculated sum of the number of tasks is assigned is equivalent to the maximum number fo tasks.
    if cesmTasksCalculated == maxQuantityOfTasks:#When they are equivalent, thenthe value of True is returned 
        return True
    else:#otherwise False is returned
        return False

    

def make_equivalent_to_max_tasks(max_tasks_allocation, ntasks_dictionary):
    sumOfCESMTasks = 0
    tasksProperlyAllocated = False
    max_tasks_allocation_num = int(max_tasks_allocation)
    for key in ntasks_dictionary:
        sumOfCESMTasks += ntasks_dictionary[key]
    while(tasksProperlyAllocated ==False):
        if sumOfCESMTasks == max_tasks_allocation_num:
            tasksProperlyAllocated = True
        elif sumOfCESMTasks < max_tasks_allocation_num:
            for key in ntasks_dictionary:
                ntasks_dictionary[key] += 1
                sumOfCESMTasks += 1
                tasksProperlyAllocated = checkSumOfTasksToMaxTasks(max_tasks_allocation, sumOfCESMTasks)
                if tasksProperlyAllocated ==True:
                    break
        elif sumOfCESMTasks > max_tasks_allocation_num:
            for key in ntasks_dictionary:
                ntasks_dictionary[key] -= 1
                sumOfCESMTasks -= 1
                tasksProperlyAllocated = checkSumOfTasksToMaxTasks(max_tasks_allocation, sumOfCESMTasks)
                if tasksProperlyAllocated ==True:
                    break
    return ntasks_dictionary
        
        

def default_max_tasks_json(max_tasks_allocation):
    fraction_max_tasks_callocation = int(max_tasks_allocation)/9
    ntasks_dictionary ={"atm":fraction_max_tasks_callocation, "cpl":fraction_max_tasks_callocation, "ocn":fraction_max_tasks_callocation, "wav":fraction_max_tasks_callocation, "glc":fraction_max_tasks_callocation, "ice":fraction_max_tasks_callocation, "rof":fraction_max_tasks_callocation, "lnd":fraction_max_tasks_callocation, "esp":fraction_max_tasks_callocation}
    recalculated_ntasks_dictionary = make_equivalent_to_max_tasks(max_tasks_allocation, ntasks_dictionary)
    totalTasksDictConversion ={"totaltasks": max_tasks_allocation}
    rootpeDictCopy = deepcopy(ntasks_dictionary)
    nthrdsDictCopy = deepcopy(ntasks_dictionary)
    temporaryDictionaryForSubmission.update("ntasks": recalculated_ntasks_dictionary, "rootpe": rootpeDictCopy, "nthrds": nthrdsDictCopy, totalTasksDictConversion)
    chosen_directory = folder_name()
    optimize_values_allocation_run(temporaryDictionaryForSubmission, chosen_directory)

def generate_defualt_cesm_tasks_allocation(max_tasks_allocation):
    path_to_default_json = "/glade/work/"+os.environ["USER"]+"/optimum_json/"
    

def initiate_premiere_runCESM(maximum_num_of_tasks):
    first_cesm_run_defaults = retrieve_recent_cesm_ntasks_json_file("default_cesm_tasks_values")
    first_cesm_run_total_tasks_default_value = retrieve_recent_cesm_ntasks_json_file("default_total_tasks_cesm_values")
    chosen_directory = folder_name()
    optimize_values_allocation_run(first_cesm_run_defaults, first_cesm_run_total_tasks_default_value, chosen_directory)

def initiate_run():
    load_balancing_optimize_dict = retrieve_recent_cesm_ntasks_json_file("optimize_cesm_values")
    load_balancing_total_tasks_dict = retrieve_recent_cesm_ntasks_json_file("total_tasks_cesm_values")
    print("Check to make sure total tasks dictionary has loaded:")
    print(load_balancing_total_tasks_dict)
    chosen_directory = folder_name()
    optimize_values_allocation_run(load_balancing_optimize_dict,load_balancing_total_tasks_dict, chosen_directory)

def singleRunCESM(collection_of_optimized_values, target_directory_for_CESM):

#initiate_run()
#initiate_premiere_runCESM(maximum_num_of_tasks)
#prototype_run()
