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
"""Reference: https://stackoverflow.com/questions/55529319/how-to-create-multiple-threads-dynamically-in-python
Reference: https://stackoverflow.com/questions/11350669/subprocess-call-env-var
Reference: https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file"""
"""Contains dependencies that cesm_allocation.py currently requires."""
import os
import sys
import subprocess
import shutil
import glob
from threading import Thread
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


        
def processorMultiplierFunc(numOfProcessors, processorMultiplier,permissionToScale):#processorMultiplierFunc() multiplies the number of processors allocated per run of a specified CESM model.
    if type(numOfProcessors) == type(2):#The if statement checks to make sure that the supplied input is not an integer. It it is, the input is changed to an string.
        numOfProcessors = str(numOfProcessors)
    #print("The number of processors: "+numOfProcessors)
    multiplierEntry = 0
    if (permissionToScale["permit-scaling"] == True):
        multiplierEntry = processorMultiplier
    else:
        pass
    numericalResult = 0
    if "exponential-scaling" in permissionToScale:
        if permissionToScale["exponential-scaling"] == True:
             numericalResult = int(numOfProcessors)*2**multiplierEntry#The processor value is multiplied by 2^(the iteration of CESM being ran)
    elif "linear-scaling" in permissionToScale:
        if permissionToScale["linear-scaling"] == True:
            if multiplierEntry >= 1:
                numericalResult = int(numOfProcessors)*2*multiplierEntry#The processor value is multiplied by 2*(the iteration of CESM being ran)
            else:
                numericalResult = int(numOfProcessors)
    else:
        numericalResult = int(numOfProcessors)
    strResult = str(numericalResult)#Convert the integer back to a string
    #print("The string result of the number of processors: "+strResult)
    return strResult#Returning the number fo processors that are allocated

def checkCompsetValue(assortmentOfCESMValues):
    for setOfCESMValues in assortmentOfCESMValues:
        print("______..______")
        print(assortmentOfCESMValues)
        print(setOfCESMValues)
        if "compset" in assortmentOfCESMValues[setOfCESMValues]:
            pass
        else:
            inputtedCompset = raw_input("No compset has been assigned. Please assign a compset...\n")
            assortmentOfCESMValues[setOfCESMValues].update({"compset":inputtedCompset})

def assignAmountOfTimeToBeSimulated(dictOfCESMValues):
    boolForAssignment = raw_input("Do you wish to assign the amount of time to be simulated by CESM. [y/n]\n")
    if boolForAssignment.lower() == "y" or boolForAssignment.lower() == "yes":
        measureForSimulation = int(input("Please enter a number for the amount of time to be simulated. Otherwise, the default value will be used.\n"))
        dictOfCESMValues.update({"sim-time-measure": str(measureForSimulation)})
    else:
        pass

def checkProcessorIncrementationLoops(valueSpecifiedForCESMRuns):
    if valueSpecifiedForCESMRuns == 0:
        valueSpecifiedForCESMRuns = 0
    elif valueSpecifiedForCESMRuns < 0:
        valueSpecifiedForCESMRuns = abs(valueSpecifiedForCESMRuns)
    elif type(valueSpecifiedForCESMRuns) == type(0.02):
        valueSpecifiedForCESMRuns = int(valueSpecifiedForCESMRuns)
    else:
        pass

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
    os.environ["CESMROOT"] = "/glade/work/"+os.environ["USER"]+"/Load_Balancing_Work/cesm2.1.3"#The CESMROOT environemnt variable is set.
    import json#imports the json library of python
    processorIncrementationLoops = input("Number of times that the CESM model will be ran shall be ran. (Only integer values greater than or equal to 1) \n")#Number of iterations to run CESM, will be doubling the number of processors used each time based on the values supplied by the json files that will be loaded
    checkProcessorIncrementationLoops(processorIncrementationLoops)
    #Initiating new function for simplistic threading
    collectThread = {}#A dictionary that will be used to store the number of threads that will be generated dynamically
    assortmentOfTimingFileDirectory = []#The list is to store the directories of the timing files to be used in the load balancing software.
    accessingTimingFileDirectory = []#The accessingTimingFileDirectory variable is utilized to identify whether assortmentOfTimingFileDirectory is being written to by a thread.
    for recordBool in range(processorIncrementationLoops):
        accessingTimingFileDirectory.append(False)
    print("Check access control list:", accessingTimingFileDirectory)
    permissionToScale = acquirePermissionToScale()
    if processorIncrementationLoops > 1:
        for runCount in range(processorIncrementationLoops):#For loop of the the specified number of loops as indicated earlier in the processorIncrementationLoops variable. The number of processors will double for each looop that is initiated.
            collection_of_optimized_values={}
            if runCount in assortment_of_optimized_values:
                collection_of_optimized_values = assortment_of_optimized_values[runCount]#Access the specific dictionary of CESM parameter values that has the key matching the value of the current iteration
            else:
                collection_of_optimized_values = assortment_of_optimized_values[(runCount % len(assortment_of_optimized_values))]
            CESMprocess = Thread(target=prepCESM, args=(processorIncrementationLoops, collection_of_optimized_values, target_directory_for_CESM, assortmentOfTimingFileDirectory, accessingTimingFileDirectory, runCount,permissionToScale,))#Starts a new CESM model be setup, built and run. Each one of the threads can be accessed using the keys of the dictionary they are stored in to access each thread as a value for the respective key in the dictionary.
            CESMprocess.start()#Initiates the CESM model to setup, build and run with the given arguments.
            collectThread.update({runCount:CESMprocess})#Stores access to the thread within a disctionary with a numeric key for each thread.
        for threadingNumber in collectThread:#For managing the threads that have been initiated.
            print("Gathering the threads.")
            collectThread[threadingNumber].join()# For ensuring that all the threads wait for the the others to conclude to prevent issues with later parts of tf the code execution.
            print("...___...")
    else:
        single_collection_of_optimized_values = assortment_of_optimized_values[0]
        prepCESM(processorIncrementationLoops, single_collection_of_optimized_values, target_directory_for_CESM, assortmentOfTimingFileDirectory, accessingTimingFileDirectory, 0,permissionToScale)
    print("Before the return, examine the timing files: ",assortmentOfTimingFileDirectory," and the CESM parameters: ", single_collection_of_optimized_values)
    return assortmentOfTimingFileDirectory, assortment_of_optimized_values#Returns the dictionary of values for the CESM parameters and the list of timing files.

def acquirePermissionToScale():
    permissionreceived = raw_input("Do you wish to run CESM models while scaling the components for each run? y/n\n")
    userPreferredOption = {"permit-scaling":False}
    while(True):
        if (permissionreceived.lower() == "y") or (permissionreceived.lower() == "yes"):
            userPreferredOption["permit-scaling"] = True
            scaling_Type = raw_input("Do you want exponential or linear scaling? [exp/lin]\n")
            if scaling_Type.lower() == "exponential" or scaling_Type.lower() == "exp":
                userPreferredOption.update({"exponential-scaling": True})
                break
            elif scaling_Type.lower() == "linear" or scaling_Type.lower() == "lin":
                userPreferredOption.update({"linear-scaling": True})
                break
            else:
                pass
        elif (permissionreceived.lower() == "n") or (permissionreceived.lower() == "no"):
            break
        else:
            permissionreceived = raw_input("Your previous input was unclear. Would you like to run CESM models while scaling the processors for the components for each run? y/n")
    return userPreferredOption


    

"""The CESM setup, build, and submit commands are defined in the startCESMProcess() function. The setup process followed by the build process followed by the submission to the queue."""

def startCESMProcess(targetCaseSubdirectory):
    print("Tracking the case commands and directory: ./"+targetCaseSubdirectory+"/case.setup caseroot "+os.getcwd()+"/"+targetCaseSubdirectory)
    setupCommand =[os.getcwd()+"/"+targetCaseSubdirectory+"/case.setup",os.getcwd()+"/"+targetCaseSubdirectory]
    buildCommand =[os.getcwd()+"/"+targetCaseSubdirectory+"/case.build",os.getcwd()+"/"+targetCaseSubdirectory]
    #submitCommand =[os.getcwd()+"/"+targetCaseSubdirectory+"/case.submit",os.getcwd()+"/"+targetCaseSubdirectory]
    submitCommand =["./case.submit"]
    subprocess.check_call(setupCommand,shell=False)#The setup for the CESM model is performed using this command
    subprocess.check_call(buildCommand,shell=False)#The building of the CESM model is performed using this command
    print("Model submission portion of the code.")
    subprocess.check_call(submitCommand,shell=False,cwd=os.getcwd()+"/"+targetCaseSubdirectory)#The submission of the CESM model to the job queue is performed using this command 
    print("The CESM model has been successfully submitted.")

"""Remaining default options for CESM are set using the xmlchangeDefaultOptions() function."""
def xmlchangeDefaultOptions(targetCaseSubdirectory,collectionOfCESMValues):
    if "sim-time-designation" in collectionOfCESMValues:
        subprocess.call(["./"+targetCaseSubdirectory+"/xmlchange","--caseroot",os.getcwd()+"/"+targetCaseSubdirectory,"STOP_N="+collectionOfCESMValues["sim-time-designation"]])
    else:
        subprocess.call(["./"+targetCaseSubdirectory+"/xmlchange","--caseroot",os.getcwd()+"/"+targetCaseSubdirectory,"STOP_N=2"])
    if "sim-time-unit" in collectionOfCESMValues:
        subprocess.call(["./"+targetCaseSubdirectory+"/xmlchange","--caseroot",os.getcwd()+"/"+targetCaseSubdirectory,"STOP_OPTION="+collectionOfCESMValues["sim-time-unit"]])
    else:
        subprocess.call(["./"+targetCaseSubdirectory+"/xmlchange","--caseroot",os.getcwd()+"/"+targetCaseSubdirectory,"STOP_OPTION=ndays"])
    subprocess.call(["./"+targetCaseSubdirectory+"/xmlchange","--caseroot",os.getcwd()+"/"+targetCaseSubdirectory,"REST_OPTION=never"])
    subprocess.call(["./"+targetCaseSubdirectory+"/xmlchange","--caseroot",os.getcwd()+"/"+targetCaseSubdirectory,"COMP_RUN_BARRIERS=TRUE"])
    subprocess.call(["./"+targetCaseSubdirectory+"/xmlchange","--caseroot",os.getcwd()+"/"+targetCaseSubdirectory,"DOUT_S=FALSE"])
    subprocess.call(["./"+targetCaseSubdirectory+"/xmlchange","--caseroot",os.getcwd()+"/"+targetCaseSubdirectory,"GMAKE_J=6"])
    subprocess.call(["./"+targetCaseSubdirectory+"/xmlchange","--caseroot",os.getcwd()+"/"+targetCaseSubdirectory,"JOB_WALLCLOCK_TIME=0:30"])# Allocated the amount time the job is allowed to run for upon submission to the queue.
"""
Reference: https://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder-using-python
Reference: https://www.pythoncentral.io/pythons-time-sleep-pause-wait-sleep-stop-your-code/
"""
def checkTimingDirectoryListEdit(recordOfTimingDirectoryAccesses):
    for record in recordOfTimingDirectoryAccesses:
        if record == True:
            return True
    return False
            
def assignValuesForNTASKS(assortmentOfModelComponentsValues, assortmentOfInvolvedComponents, numericalThreadIdentifier, targetCaseSubDirectory,permittedToScale):
    #function to catch any componenets that have not been assigned a value from ntasks. Will be scaled based on the numerical identifier of the thread.
    xmlNTASKSParameter = []# The list of the "ntasks" related commands to be submitted for the configuration of the CESM model build and run
    for componentNumericalIdentifier in assortmentOfInvolvedComponents:#Looping through the components to access each of them and make sure to access each component of the CESM model
        if assortmentOfInvolvedComponents[componentNumericalIdentifier] == "wav":#The "wav" component is picked out for particular restrictions since it can become highly inefficent as more processors are assigned.
            #wavValue = int(assortmentOfModelComponentsValues["ntasks"]["wav"])
            #print(wavValue)
            if int(assortmentOfModelComponentsValues["ntasks"][assortmentOfInvolvedComponents[componentNumericalIdentifier]]) > 108:#If the "wav" coponeent current has more than 108 sllocated for the ntasks
                xmlNTASKSParameter = ["./"+targetCaseSubDirectory+"/xmlchange","--caseroot",targetCaseSubDirectory ,"NTASKS_"+assortmentOfInvolvedComponents[componentNumericalIdentifier].upper()+"="+str(108)]#Caps the WAV component at the value of 108
            else:#When the "WAV" component possesses 108 or less allocated ntasks, assign that value for the "wav" component
                xmlNTASKSParameter = ["./"+targetCaseSubDirectory+"/xmlchange","--caseroot",targetCaseSubDirectory ,"NTASKS_"+assortmentOfInvolvedComponents[componentNumericalIdentifier].upper()+"="+str((checkComponentValue(assortmentOfModelComponentsValues["ntasks"], "ntasks", assortmentOfInvolvedComponents[componentNumericalIdentifier]),numericalThreadIdentifier,permittedToScale))]#The assignment of the
        else:
            xmlNTASKSParameter = ["./"+targetCaseSubDirectory+"/xmlchange","--caseroot",targetCaseSubDirectory,"NTASKS_"+assortmentOfInvolvedComponents[componentNumericalIdentifier].upper()+"="+str(processorMultiplierFunc(checkComponentValue(assortmentOfModelComponentsValues["ntasks"], "ntasks", assortmentOfInvolvedComponents[componentNumericalIdentifier]),numericalThreadIdentifier,permittedToScale))]#All other components are given ntasks allocations here
        subprocess.call(xmlNTASKSParameter,shell=False,env=os.environ)#Submit commands to the configuration of the model for ntasks
        
    
def assignValuesForROOTPE(assortmentOfModelComponentsValues, assortmentOfInvolvedComponents, numericalThreadIdentifier, targetCaseSubDirectory, permittedToScale):#The assignValuesForROOTPE function is to proper allocate the the model's values for the ROOTPE parameters for the CESM model
    xmlROOTPEParameter =[]# An array that will collect a number of commands that will be used to run the processes in the system.
    for componentNumericalIdentifier in assortmentOfInvolvedComponents:#Loops through the componenets available to get to each component to assign rootpe parameters.
        xmlROOTPEParameter = ["./"+targetCaseSubDirectory+"/xmlchange","--caseroot",targetCaseSubDirectory ,"ROOTPE_"+assortmentOfInvolvedComponents[componentNumericalIdentifier].upper()+"="+str(checkComponentValue(assortmentOfModelComponentsValues["rootpe"], "rootpe", assortmentOfInvolvedComponents[componentNumericalIdentifier]))]#The number of rootpe resources that will be allocated to the specified model component
        subprocess.call(xmlROOTPEParameter,shell=False,env=os.environ)#The list of commands will be submitted to the configuration for the CESM model.


def assignValuesForNTHRDS(assortmentOfModelComponentsValues, assortmentOfInvolvedComponents, numericalThreadIdentifier, targetCaseSubDirectory,permittedToScale):#The assignValuesForNTHRDS function is for assigning the values for NTHRDS. Each component should have a value of 1 unless otherwise specified in the code.
    xmlNTHRDSParameter =[]#XMLNTHRDSParameter will store the necessary commands to allow the proper allocations for nthrds
    for componentNumericalIdentifier in assortmentOfInvolvedComponents:#Looping through the components to acquire each model component
        xmlNTHRDSParameter = ["./"+targetCaseSubDirectory+"/xmlchange","--caseroot", targetCaseSubDirectory,"NTHRDS_"+assortmentOfInvolvedComponents[componentNumericalIdentifier].upper()+"="+str(checkComponentValue(assortmentOfModelComponentsValues["nthrds"], "nthrds", assortmentOfInvolvedComponents[componentNumericalIdentifier]))]#The number of processors that will be allocated to the specified model component
        subprocess.call(xmlNTHRDSParameter,shell=False,env=os.environ)#Submit the NTHRDS allocations to be made when building the model.


def prepCESM(processorIncrementationLoops, collection_of_optimized_values, target_directory_for_CESM, assortmentOfTimingFileDirectory, accessingTimingFileDirectory, threadIdentifier, permittedToScale):#prepCESM() function serves to prepare the basic configurations for the setup, building and submission of the CESM model.
    """Creation of the case."""
    print("Printing the CESMROOT environment variable ",os.environ["CESMROOT"])#Visual check over for the CESMROOT environment variable
    print("The directory for the CESM contents: "+ target_directory_for_CESM)#Visual check over the for the directory that CESM will be building contents within
    print("Now the dictionary containing the value for the total amount of tasks:")#printing the dictionary containing the total amount of tasks
    print(collection_of_optimized_values["totaltasks"])#The dictionary containg the total number of tasks
    print("The PROJECT environment variable: ", os.environ["PROJECT"])#Visual confirmation of the PROJECT environment variable being passed
    if "compset" not in collection_of_optimized_values:
       collection_of_optimized_values.update({"compset" : "B1850"})
    commandRunCESM =[os.environ["CESMROOT"]+"/cime/scripts/create_newcase","--case",target_directory_for_CESM+"_processors_"+processorMultiplierFunc(str(collection_of_optimized_values["totaltasks"]),threadIdentifier,permittedToScale)+"_run"+str(threadIdentifier), "--compset",collection_of_optimized_values["compset"],"--res","f09_g17","--project",os.environ["PROJECT"],]#The command to be ran in the shell for constructing a new instance of CESM to run.
    print("CESM commands:")
    print(commandRunCESM)#Visual check over te commands to be ran for CESM
    subprocess.check_call(commandRunCESM,shell=False,env=os.environ)#Initiating the command line script to be ran within bash
    
    print(target_directory_for_CESM+"_processors_"+processorMultiplierFunc(str(collection_of_optimized_values["totaltasks"]),threadIdentifier, permittedToScale)+"_run"+str(threadIdentifier))# Prints the subdirectory of the relevant files of the case.
    caseRunSubdirectory= target_directory_for_CESM+"_processors_"+processorMultiplierFunc(str(collection_of_optimized_values["totaltasks"]),threadIdentifier,permittedToScale)+"_run"+str(threadIdentifier)# Stores the case subdirectory as a string to use later
    caseSubDirectory =str("/glade/work/"+os.environ["USER"]+"/"+caseRunSubdirectory)#Absolute path to the caseRunSubdirectory.
    caseSubDirectoryExists = False# Check to make sure the Case's subdirectory exists before executing the remainder of the code.
    import time#Import the time module of Python
    for restCounter in range(25):#The counter to enable
        if os.path.isdir(caseSubDirectory):#If the directory exists
        #os.chdir(target_directory_for_CESM+"_processors_"+processorMultiplierFunc(str(collection_of_optimized_values["totaltasks"]),threadIdentifier)+"_run"+str(threadIdentifier))#Changes the directory for the CESM project
            #print(caseSubDirectory+" has been located.")#Inform the user the directory has been located
            break#Break out of the for loop.
        else:
            time.sleep(3)#If not found, wait 3 seconds for each of the 25 loops.
            print("Still searching for "+caseSubDirectory)#Inform the user that the directory is still being searched for.
    #name_of_json = input("What is the name of the json file where the data is stored?")


    """Now for altering the processor counts:"""
    componentDictionary = {0:"atm", 1:"cpl", 2:"ocn", 3:"wav", 4:"glc",5:"ice",6:"rof", 7:"lnd", 8:"esp"}#A dictionary of the components for the CESM model to build with
    #function to catch any components that have not been assigned a value from ntasks. Will be scaled based on the numerical identifier of the thread.
    assignValuesForNTASKS(collection_of_optimized_values, componentDictionary, threadIdentifier, caseRunSubdirectory,permittedToScale)#Assigning the NTASKS values.

    """ROOTPE Values are being established"""
    #The ./xmlchange command rewrites xml files that provide parameters for building the project
    assignValuesForROOTPE(collection_of_optimized_values, componentDictionary, threadIdentifier, caseRunSubdirectory,permittedToScale)#Assigning the ROOTPE values.

    """NTHRDS Values are being established"""
    #The ./xmlchange command rewrites xml files that provide parameters for building the project
    assignValuesForNTHRDS(collection_of_optimized_values, componentDictionary, threadIdentifier, caseRunSubdirectory,permittedToScale)#Assigning the NTHRDS values.

    timing_file_directory =os.getcwd()+"/"+caseRunSubdirectory+"/timing/"#Concatenates the directory with that of the timing files subdirectory.
    """setting the default parameters"""
    xmlchangeDefaultOptions(caseRunSubdirectory,collection_of_optimized_values)#Calls the xmlchangeDefaultOptions() function that will call for the remaining values in the xml files to be taken
    startCESMProcess(caseRunSubdirectory)#Runs the CESM commands necessary for prepping and running a CESM project

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
    print("The contents of the timing file directory: ", assortmentOfTimingFileDirectory)        
    print("Timing file directory appended for thread"+ str(threadIdentifier))
     



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

def directoryCheckSafeguard(inputDirectoryPath):#For checking if the directory passed as an argument to the function exists
    if os.path.isdir(inputDirectoryPath):# If the directory exists, do nothing
        pass
    else:
        os.mkdir(inputDirectoryPath)#If the directory does not exist, make said directory
    
def retrieve_recent_cesm_ntasks_json_file(numberOfRetrievals):#retrieve_recent_cesm_ntasks_json_file() function is utilized to retrieve the most recent json files that are generated by the load balancing code.
    import json#importing json module of python.
    directory_prefix = "/glade/work/"+os.environ["USER"]+"/optimum_json/"#A directory for storing the json files that are created from the load balancing code to preserve the optimal parameters for the ran CESM model.
    directoryCheckSafeguard(directory_prefix)
    model_CESM_values_dict ={}#For storing the optimal CESM parameter values that can be used to optimize CESM models.
    collection_of_files = []#A list for the file directories that will be used for accessing the json files that are generated.
    collection_of_files = glob.glob("/glade/work/"+os.environ["USER"]+"/optimum_json/optimization_dictionaries*.json")#acquiring the optimization_dictionaries json files to acquire the most recent variations that have been produced from the recent CESM model run.
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
                dictionaryOfRecentJSONs.update({counterNum:model_CESM_values_dict})#Adding the dictionary of optimized CESM parameters to the dictionary that contains the entiretly of the recent json files that were collected
                print("Structure of the dictionary: ")
                print(model_CESM_values_dict)
            counterNum+=1#increase the value by 1
        return dictionaryOfRecentJSONs#returns the json of relevant CESM parameter values

def folder_name():#The function of folder_name() is used for the purpose of getting the file name for CESM as well as checking if the file does not already exist within the directory
    named_folder = raw_input("Please name the folder that the contents will be stored within...\n")#Input for the name of the file
    print("The name of the folder is "+ named_folder)
    while(os.path.isfile(named_folder)):#As long as the name of the folder exists in the directory, ask for a new name to be used
        print("Please choose a new name for the folder. The name that was entered happens to already exist.")
        named_folder = raw_input("Input the new name of the folder.\n")#New input name
    return named_folder# Return the submitted the name for the folder

def checkSumOfTasksToMaxTasks(maxQuantityOfTasks,cesmTasksCalculated):#For ensuring that a calculated sum of the number of tasks is assigned is equivalent to the maximum number fo tasks.
    if cesmTasksCalculated == maxQuantityOfTasks:#When they are equivalent, then the value of True is returned
        return True#The cesmTasksCalculated is equal to the value of the maxQuantityOfTasks
    else:#otherwise False is returned
        return False#There is an inequality between cesmTasksCalculated and maxQuantityOfTasks


def make_equivalent_to_max_tasks(max_tasks_allocation, ntasks_dictionary):#make_equivalent_to_max_tasks() function is used to allocate tasks amongst the CESM components
    sumOfCESMTasks = 0#Initiated to keep track of the total number of tasks that have been allocated.
    tasksProperlyAllocated = False#The tasksProperlyAllocated is assigned False to indicate that the total number of tasks have not been properly allocated yet.
    max_tasks_allocation_num = int(max_tasks_allocation)#Gets integer value for the total number of tasks inputted for the CESM model
    sumOfCESMTasks += ntasks_dictionary["ocn"] + ntasks_dictionary["atm"]#Adds said value from the ntask allocation to be added to the sumOfCESMTasks for the purpose of tracking the total of the number of tasks for CESM
    while(tasksProperlyAllocated ==False):#While loop checking if CESM tasks have been checked to be properly allocated.
        if sumOfCESMTasks == max_tasks_allocation_num:#If the sumOfCESMTasks is equivalent to max_tasks_allocation_num, then tasksProperlyAllocatedis True and the loop will conclude
            tasksProperlyAllocated = True
        elif sumOfCESMTasks < max_tasks_allocation_num:#When the sumOfCESMTasks is less than the max_tasks_allocation_num, addition is utilized to add to the values of the ntasks of the components
            for key in ntasks_dictionary:#Iterating through the components to get the value of the components to add to the values of said components.
                if key != "ocn":
                    ntasks_dictionary[key] += 1#For each iteration fo the for loop, add one to the value of the current component.
            sumOfCESMTasks += 1#Add to the sumOfCESMTasks to maintain an updated count of the sum of ntasks allocations.
            tasksProperlyAllocated = checkSumOfTasksToMaxTasks(max_tasks_allocation, sumOfCESMTasks)#Checking if the sum of the ntasks allocation is equivalent to the total number of ntasks that have been set for the entirety of the CESM model.
            if tasksProperlyAllocated ==True:#When the tasks are are allocated, the while loop will be broken.
                break
            else:
                ntasks_dictionary["ocn"] +=1
                sumOfCESMTasks += 1
            tasksProperlyAllocated = checkSumOfTasksToMaxTasks(max_tasks_allocation, sumOfCESMTasks)#Checking if the sum of the ntasks allocation is equivalent to the total number of ntasks that have been set for the entirety of the CESM model.
            if tasksProperlyAllocated ==True:#When the tasks are are allocated, the while loop will be broken.
                break 
        elif sumOfCESMTasks > max_tasks_allocation_num:#When the sumOfCESMTasks is greater than the max_tasks_allocation_num, subtraction is applied until the sum of the ntasks allocations is equivalent to the value of max_tasks_allocation
            for key in ntasks_dictionary:#The for loop iterates through the components to enable access to the values that assigned to the component keys.
                if key != "ocn":
                    ntasks_dictionary[key] -= 1#The is decermented by one for the current ly accessed component key
            sumOfCESMTasks -= 1#Decrementing the calculated sum of ntasks allocations
            tasksProperlyAllocated = checkSumOfTasksToMaxTasks(max_tasks_allocation, sumOfCESMTasks)#Check to ensure that the max_tasks_allocation and sumOfCESMTasks are equivalent
            if tasksProperlyAllocated ==True:#When proper allocation is achieved, break the loop.
                break
            else:
                ntasks_dictionary["ocn"] -=1#Subtracts the ntask value of the OCN component by 1
                sumOfCESMTasks -= 1#Subtracts 1 from the sum of total ntasks
            tasksProperlyAllocated = checkSumOfTasksToMaxTasks(max_tasks_allocation, sumOfCESMTasks)#Checking if the sum of the ntasks allocation is equivalent to the total number of ntasks that have been set for the entirety of the CESM model.
            if tasksProperlyAllocated ==True:#When the tasks are are allocated, the while loop will be broken.
                break
    return ntasks_dictionary#Returns the ntasks dictionary after correct allocations and checks have been perfromed
        
        

def default_max_tasks_json(acquired_command_line_args):#default_max_tasks_json() function constructs basic json for submission to be setup and modeled by CESM. Takes an argument of the maximum amount of tasks that will be used by the model of CESM.
    fraction_max_tasks_callocation = int(acquired_command_line_args.selected_maxtasks)/2#In this initial setup the value of max_tasks_allocation is used to provide values by dividing the ntasks amounts.
    ntasks_dictionary ={"atm":fraction_max_tasks_callocation, "cpl":fraction_max_tasks_callocation, "ocn":fraction_max_tasks_callocation, "wav":fraction_max_tasks_callocation, "glc":fraction_max_tasks_callocation, "ice":fraction_max_tasks_callocation, "rof":fraction_max_tasks_callocation, "lnd":fraction_max_tasks_callocation, "esp":fraction_max_tasks_callocation}#There are allocations maintaining that each componeent initially a fraction that is roughly equivalent to the value of max_tasks_allocation
    max_tasks_allocation = int(acquired_command_line_args.selected_maxtasks)
    recalculated_ntasks_dictionary = make_equivalent_to_max_tasks(max_tasks_allocation, ntasks_dictionary)#Recalculates the values of ntasks for each of the components to make sure that the sum of the ntasks of the components is equivalent to the value of max_tasks_allocation
    totalTasksDictConversion ={"totaltasks": max_tasks_allocation}#Creates a dictionary with the first key being "totaltasks" with the value max_tasks_allocation
    rootpeDictCopy = copy.deepcopy(recalculated_ntasks_dictionary)#The ROOTPE dictionary is created prototype_run(). Placeholder until proper scaling for the allocations can be introduced.
    rootpeDictCopy = rootperecalculate(rootpeDictCopy, max_tasks_allocation)
    nthrdsDictCopy = copy.deepcopy(recalculated_ntasks_dictionary)#The NTHRDS dictionaty is being created. Placeholder until proper scaling for the allocations can be introduced.
    for componentKey in nthrdsDictCopy:#Ensures that the nthrds are limited to 1 for each component
        nthrdsDictCopy[componentKey] = "1"#Sets each component's nthrds components to 1.
    temporaryDictionaryForSubmission ={}#Creates a new dictionary to store all of the CESM parameters.
    temporaryDictionaryForSubmission.update({"ntasks": recalculated_ntasks_dictionary}) # temporaryDictionaryForSubmission updated with the "ntasks" dictionary
    temporaryDictionaryForSubmission.update({"rootpe": rootpeDictCopy})# temporaryDictionaryForSubmission updated with the "rootpe" dictionary
    temporaryDictionaryForSubmission.update({"nthrds": nthrdsDictCopy}) # temporaryDictionaryForSubmission updated with the "nthrds" dictionary
    temporaryDictionaryForSubmission.update(totalTasksDictConversion)#Putting all of the default CESM paramter dictionaries into one complete dictionary
    obtainCompset(temporaryDictionaryForSubmission, acquired_command_line_args)#Will obtain a compset for the CESM model if it has not already been provided.
    simTimeMeasure(temporaryDictionaryForSubmission, acquired_command_line_args)#Will obtain a measure of time for the CESM model if it has not already been provided.
    simTimeUnits(temporaryDictionaryForSubmission, acquired_command_line_args)#Will obtain a unit of time for the CESM model if it has not already been provided.
    collectionOfDictionariesForCESM={0:temporaryDictionaryForSubmission}#The JSON struccture conforming for the remainder of the code.
    chosen_directory = folder_name()#Asks for the name of the folder that the contents will be stored within.
    #print("Visual of the structure of initial dictionary:", collectionOfDictionariesForCESM)
    timingFileDirectoryListConstruct, optimizedCESMParemterValuesDictionaryConstruct = optimize_values_allocation_run(collectionOfDictionariesForCESM, chosen_directory)#Launches the first execution of a CESM model.
    return timingFileDirectoryListConstruct, optimizedCESMParemterValuesDictionaryConstruct 

def rootperecalculate(rootpeDict,allocatedMaxTasks):#rootperecalculate() function that is recalculating the pe values allocated to each component.
    for componentKey in rootpeDict:#For loop that iterates through the component keys of the rootpeDict
        if componentKey=="ocn":#Ocean component gets the declared rootpe allocation
            rootpeDict[componentKey] = int(allocatedMaxTasks)/2#The rootpe values are being rewritten for ocn component
        else:
            rootpeDict[componentKey] = "0"# The rootpe for any component that is not the OCN component is 0.
    return rootpeDict

def obtainCompset(constructedDict, collectionOfComdArgs):# function for acquiring the compset of the CESM model to be built and ran.
    if collectionOfComdArgs.compset_designation == None:# Checks if the compset has be set previously, if not the remainder of the fuction continues.
        inputDecision = raw_input("Do you wish to use a specified compset or use the default compset? [y/n]")# There are choices of yes or no. Yes to input a compset. No to use the default compset that is set.
        if inputDecision.lower() == "y" or inputDecision.lower() == "yes":#If the input is 'y' or 'yes'
            specifiedcompset = raw_input("Please enter the compset you want to build the CESM model for and run. Examples: B1850, BWma1850...\n")#User can input the compset that is be used to build and run the model.
            constructedDict.update({"compset": specifiedcompset})#Updates the compset utilizing the dictionary that will be fed into later parts of the code.
        elif inputDecision.lower() == "n" or inputDecision.lower() == "no":#When the input is "n" or "no"
            constructedDict.update({"compset": "B1850"})#Set the compset to the default B1850
        else:
            constructedDict.update({"compset": "B1850"})#Otherwise set the default is B1850
    else:
        pass#Otherwise do nothing

def simTimeMeasure(constructedDict, collectionOfComdArgs):#Function to acquire the quantity of time that the model will be simulating.
    if collectionOfComdArgs.sim_time_designation == None:# Checks if a value for the simulated time has already been declared.
        inputDecision = raw_input("Do you wish to use a specified measure of time or use the default measure of time? [y/n]")# The input is "yes" or "no"
        if inputDecision.lower() == "y" or inputDecision.lower() == "yes":#When the response is "y" or "yes"
            specifiedTimeLength = raw_input("Please enter the measure of time you want to configure for the CESM model run.\n")#The measure of time to be simulated can be inputted here.
            constructedDict.update({"sim-time-designation": specifiedTimeLength})#The quantity of time to be simulated by the model may be specified here.
        elif inputDecision.lower() == "n" or inputDecision.lower() == "no":# If the response is n or no
            constructedDict.update({"sim-time-designation": "5"})#Default measure of time to be simulated for the CESM model
        else:
            constructedDict.update({"sim-time-designation": "5"})#Defualt measure of time to be simulated for the CESM model
    else:
        pass

def simTimeUnits(constructedDict, collectionOfComdArgs):# Function to acquire the unit of time that the model will be simulating
    if collectionOfComdArgs.sim_time_unit == None:#When the unit for the time simulated has not been assigned
        inputDecision = raw_input("Do you wish to use a specified unit of time or use the default unit of time? [y/n]")#Obtain the response by the user which is either yes (or y) or no (or n)
        if inputDecision.lower() == "y" or inputDecision.lower() == "yes":#When the response is yes or y
            specifiedTimeUnits = raw_input("Please enter the measure of time you want to configure for the CESM model run. [Example: ndays]\n")#The user can now input the unit time of time that will be utilized for the configuration of the CESM model.
            constructedDict.update({"sim-time-unit": specifiedTimeLength})#Places the unit of time within the dictionary to make sure that it will be ran.
        elif inputDecision.lower() == "n" or inputDecision.lower() == "no":#When the response is 'no' or 'n'
            constructedDict.update({"sim-time-unit": "ndays"})#The default value for the unit of time that will be used by the CESM models to be built and ran
        else:#Otherwise (if anything else is submitted)
            constructedDict.update({"sim-time-unit": "ndays"})#The default value for the unit of time that will be used by the CESM models to be built and ran
    else:
        pass

"""The dict_optimized_values is a function to extract a dictionary of the CESM values that will be used by the next CESM model builds and runs."""
def dict_optimized_values(ntasksDictTarget, rootpeDictTarget, nthreadsDictTarget, totaltasksValue):# Place in optimize.py to return ntasks dictionary
    import os#Imports os
    import json#Imports json
    logger.info("Beginning to write the json")#Starts to write the json file
    json_location_prefix = "optimization_dictionaries"#Will be the prefix for the name of the job
    placeholderDictionary = {}#Dictionary to be used for storing the CESM parameters.
    placeholderDictionary.update({"ntasks": ntasksDictTarget})#The placeholherDictionary is being updated witht he "ntasks" dictionary
    placeholderDictionary.update({"rootpe": rootpeDictTarget})#The placeholherDictionary is being updated witht he "rootpe" dictionary
    placeholderDictionary.update({"nthrds": nthreadsDictTarget})#The placeholherDictionary is being updated witht he "nthrds" dictionary
    placeholderDictionary.update({"totaltasks": totaltasksValue})#The placeholherDictionary is being updated witht he "totaltasks" dictionary
    json_location_exist = True#Boolean to chck that the file name eists
    iteration = 1#Increments to provide a number to differentiate the json files from one another
    logger.info("Checking json file presence.")#Start of the process to check for presence of file with proposed file name.
    while json_location_exist == True:#True to ensure that there the process is being checked.
        json_location_prefix_iteration_combo = json_location_prefix+str(iteration)#Puts together the file name with the number appended.
        if os.path.isfile("/glade/work/"+os.environ["USER"]+"/optimum_json/"+json_location_prefix_iteration_combo+".json"):#Checks to make sure the proposed file name is not already in usage in the specified directory.
            logger.info("Must edit file name.")#If the file name is already in use, edits must be name to the proposed file name
            iteration += 1#Increment the iteration up by 1.
        else:
            logger.info("New json file name is available.")#The JSON file name can be utilized.
            json_location_prefix = json_location_prefix_iteration_combo#Assign the proposed JSON file name to the json_location_prefix variable
            json_location_exist= False#Boolean json_location_exist variable is assigned the value of False
    with open("/glade/work/"+os.environ["USER"]+"/optimum_json/"+json_location_prefix+".json", "w") as amendableFile:#Opening up the new json file to be written to.
        json.dump(placeholderDictionary, amendableFile)#Writes to the opened jsonfile
