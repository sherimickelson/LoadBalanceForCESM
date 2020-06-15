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

def prototype_run():
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


        
def processorMultiplierFunc(numOfProcessors, processorMultiplier):
    if type(numOfProcessors) == type(2):
        numOfProcessors = str(numOfProcessors)
    print("The number of processors: "+numOfProcessors)
    numericalResult = int(numOfProcessors)*2**processorMultiplier
    strResult = str(numericalResult)
    print("The string result of the number of processors: "+strResult)
    return strResult
    
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
    collectThread = {}
    assortmentOfTimingFileDirectory = []
    accessingTimingFileDirectory = False
    for runCount in range(processorIncrementationLoops):#For loop of the the specified number of loops as indicated earlier in the processorIncrementationLoops variable. The number of processors will double for each looop that is initiated.
        CESMprocess = Thread(target=prepCESM, args=(processorIncrementationLoops, collection_of_optimized_values, target_directory_for_CESM, assortmentOfTimingFileDirectory, accessingTimingFileDirectory, runCount,))
        CESMprocess.start()
        collectThread.uptdate(runCount:CESMprocess)
    for threadingNumber in collectThread:
        collectThread[threadingNumber].join()
    return timing_file_directory, collection_of_optimized_values

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


def prepCESM(processorIncrementationLoops, collection_of_optimized_values, target_directory_for_CESM, assortmentOfTimingFileDirectory, accessingTimingFileDirectory, threadIdentifier):
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
    assignValuesForNTASKS(collection_of_optimized_values, componentDictionary, threadIdentifier)

    """ROOTPE Values are being established"""
    #The ./xmlchange command rewrites xml files that provide parameters for building the project
    assignValuesForROOTPE(collection_of_optimized_values, componentDictionary, threadIdentifier)

    """NTHRDS Values are being established"""
    #The ./xmlchange command rewrites xml files that provide parameters for building the project
    assignValuesForNTHRDS(assortmentOfModelComponentsValues, assortmentOfInvolvedComponents, numericalThreadIdentifier)

    timing_file_directory =os.getcwd()+"timing/"
    """setting the default parameters"""
    xmlchangeDefaultOptions()#Calls the xmlchangeDefaultOptions() function that will call for the remaining values in the xml files to be taken
    startCESMProcess()#Runs the CESM commands necessary for prepping and running a CESM project

    print("CESM job is submitted")
    #print("This is run: "+str(runCount))
    print("Conclusion of CESM run...")
    accessControl = False
    while(accessControl == False):
        accessControl = checkTimingDirectoryListEdit(accessingTimingFileDirectory)
        if accessControl == True:
            pass
        else:
            accessingTimingFileDirectory[threadIdentifier] = True
            assortmentOfTimingFileDirectory.append(timing_file_directory)
            accessingTimingFileDirectory[threadIdentifier] = False
    print("Timing file directory appended for "+ str(threadIdentifier))
     



def checkComponentValue(componentOptimizedValues, categoryForValues, modelComponent):#check checkComponentValue ensures that each component will be passed a value and if one is not present then the value passed will be 1
    if categoryForValues == "ntasks":
        if modelComponent in componentOptimizedValues:#An if condition
            return componentOptimizedValues[modelComponent]
        else:
            return "1"
    else:
        if modelComponent in componentOptimizedValues:#An if condition
            return componentOptimizedValues[modelComponent]
        else:
            return "0"
def retrieve_recent_cesm_ntasks_json_file(numberOfRetrievals):
    import json
    directory_prefix = "/glade/work/"+os.environ["USER"]+"/optimum_json/"
    model_CESM_values_dict ={}
    collection_of_files = []
    if prefix_keyword=="optimization_dictionaries":
        collection_of_files = glob.glob("/glade/work/"+os.environ["USER"]+"/optimum_json/optimization_dictionaries*.json")
    else:
        print("An error has occurred in the json searching process...")
        print("Please reexamine process...")
        print("Exiting...")
        exit()
    print("The current inventory of json files:")
    print(collection_of_files)
    if not collection_of_files:
        while(collection_of_files == []):
            import time
            time.sleep(10)
            json_file_storage =False
            while(json_file_storage == False):
                collection_of_files = glob.glob("/glade/work/"+os.environ["USER"]+"/optimum_json/*.json")
                if "/glade/work/"+os.environ["USER"]+"/optimum_json/optimization_dictionaries*.json" not in collection_of_files:
                    time.sleep(4)
                    print("Still searching for json files")
                else: 
                    break
    else:
        recentVersionsJSON = []
        for counter in range(numberOfRetrievals):
            name_of_recent_json_file = max(collection_of_files, key = os.path.getctime)
            recentVersionsJSON.append(name_of_recent_json_file)
            collection_of_files.remove(name_of_recent_json_file)
        dictionaryOfRecentJSONs = {}
        counter = 0
        for jsonFile in recentVersionsJSON:
            with open(jsonFile) as location_of_dict:
                model_CESM_values_dict = json.load(location_of_dict)
                print("Structure of the dictionary: ")
                print(model_CESM_values_dict)
                dictionaryOfRecentJSONs.update(counter:model_CESM_values_dict)
             counter+=1
        return dictionaryOfRecentJSONs

def folder_name():
    named_folder = raw_input("Please name the folder that the CESM contents will be stored within...\n")
    print("The name of the folder is "+ named_folder)
    while(os.path.isfile(named_folder)):
        print("Please choose a new name for the folder. The name that was entered happens to already exist.")
        named_folder = raw_input("Input the new name of the folder.\n")
    return named_folder

def checkSumOfTasksToMaxTasks(maxQuantityOfTasks,cesmTasksCalculated):
    if cesmTasksCalculated == maxQuantityOfTasks:
        return True
    else:
        False

    

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
