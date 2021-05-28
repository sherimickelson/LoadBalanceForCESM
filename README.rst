==================
LoadBalanceForCESM
==================

About
-----
This repository contains code and instructions relevant to the load balancing endeavor for CESM. The project was initiated in the Summer of 2020.


Contributors:
-------------
**Mentors:
John Dennis, Sheri Mickelson, and Brian Dobbins
**Students:
Soudeh Kamali and Thomas Johnson III

b2deg_alternative.py
Contains majority of the code related to building and running CESM models. The configuration for the built models happens within this python file. Depends on inputs from the cesm_allocation.py.

--prototype_run()
Original function that was devised based off of the bash implementation that was supplied by Brian Dobbins. The function takes two command line arguments that. Has no bearing on the current implementation of the code. Kept for preserving the original structure of code.

--processorMultiplierFunc(numOfProcessors, processorMultiplier,permissionToScale)
This function will scale the processors of the CESM models while building. There can be linear scaling by 2 or exponential scaling by 2. The information for scaling is stored within the dictionary for the CESM values.For functionality related to scaling, focus on this function in particular. Only call this function in the possiility that a CESM parameter will be scaled. Exponential scaling allows for scaling with the indicated powers and linear scaling allows for scaling with the indicated multiples.

--checkCompsetValue(assortmentOfCESMValue)
Can be used as a tool to check the compsets that will be ran in dictionary containing the CESM values for each model of CESM that will be built and ran.

--assignAmountOfTimeToBeSimulated(dictOfCESMValues)
The amount of time that will be utilized for simulation within the model. This function deals with the amount of time, not the units of said time.

--checkProcessorIncrementationLoops(valueSpecifiedForCESMRuns)
Ensures that the value inputted for the for loop to spin up threads for building separate CESM models and running them is a positive integer.

--optimize_values_allocation_run(assortment_of_optimized_values, target_directory_for_CESM)
Function that begins the process for building CESM models and manages the organization of the threads that said CESM models will be built and ran in. Includes checks to make sure that correct directories exist before being accessed. There are also checks to make sure that the threads are not accessing the same resources as the same time. The threads that are generated are organized through the use of a dictionary that uses numerical keys to identify each thread.

--acquirePermissionToScale()
The function acquirePermissionToScale() is used to acquire the information of whether user wants to scale the cores allocated for each. If the user decides to scale the number of cores, the method of scaling, linear or exponential must be inputted as well.

--startCESMProcess(targetCaseSubdirectory)
Initiates the basic commands to setup, build then run the CESM models.

--xmlchangeDefaultOptions(targetCaseSubdirectory,collectionOfCESMValues)
The xml options are set in this command. This includes the time being simulated and wallclock_time for the CESM model.

--checkTimingDirectoryListEdit(recordOfTimingDirectoryAccesses)
Checks for the access of the access of tht timing file directories. Each array element manages the the status of the threads as they attempt to access the timing file directory.

--assignValuesForNTASKS(assortmentOfModelComponentsValues, assortmentOfInvolvedComponents, numericalThreadIdentifier, targetCaseSubDirectory,permittedToScale)
The assignValuesForNTASKS() function is for setting the xml configurations for the amount of tasks to be allocated and to which component. The tasks for the WAV componenet are capped here to preserve the efficiency of the overall model. To edit such, edit the if statements. Due to the scaling of tasks if indicated by the user, the permittedToScale and numericalThreadIdentifier arguments are present.

--assignValuesForROOTPE(assortmentOfModelComponentsValues, assortmentOfInvolvedComponents, numericalThreadIdentifier, targetCaseSubDirectory, permittedToScale)
Assigns the rootpe for the various components. Possesses the ability to scale the inputs similar to theassignValuesForNTASKS() function.

--assignValuesForNTHRDS(assortmentOfModelComponentsValues, assortmentOfInvolvedComponents, numericalThreadIdentifier, targetCaseSubDirectory,permittedToScale)
Assigns the number of threads for each component. does not scale the component inputs provided to it.

--prepCESM(processorIncrementationLoops, collection_of_optimized_values, target_directory_for_CESM, assortmentOfTimingFileDirectory, accessingTimingFileDirectory, threadIdentifier, permittedToScale)
The prepCESM() function is designed take care of building and running the model after the optimize_values_allocation_run() function is called. The dirctory for the new case is developed hereas well as the call of the assignValuesForNTASKS(), assignValuesForROOTPE(), and assignValuesForNTHRDS() functions. The timing file directory is copied to be eventually shared with the load balancer later.

cesm_allocation.py
The load balncing software code is initiated in this file and the function that manages the highest level function amongst b2deg_alternative.py and cesm_allocation.py. This python file is the one that is run from the command line.

Setup:
Make the following challenges to optimize.py

Add this function:

_____________________________________________________________________________

"""The dict_optimized_values is a function to extract a dictionary of the CESM values that will be used by the next CESM model builds and runs."""
def dict_optimized_values(ntasksDictTarget, rootpeDictTarget, nthreadsDictTarget, totaltasksValue):# Place in optimize.py to return ntasks dictionary
    import os#Imports os
    import json#Imports json
    logger.info("Beginning to write the json")#Starts to write the json file
    json_location_prefix = "optimization_dictionaries"#Will be the prefix for the name of the job
    placeholderDictionary = {}#Dictionary to be used for storing the CESM parameters.
    placeholderDictionary.update({"ntasks": ntasksDictTarget})#The placeholherDictionary is being updated with the "ntasks" dictionary
    placeholderDictionary.update({"rootpe": rootpeDictTarget})#The placeholherDictionary is being updated with the "rootpe" dictionary
    placeholderDictionary.update({"nthrds": nthreadsDictTarget})#The placeholherDictionary is being updated with the "nthrds" dictionary
    placeholderDictionary.update({"totaltasks": totaltasksValue})#The placeholherDictionary is being updated with the "totaltasks" dictionary
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

_______________________________________________________________________________________________

Add call for said function in the write_pe_template() function of optimize_model.py for Load Balancing Code.

Basic Execution Instructions:
In the command line, type cesm_allocation.py [max_tasks_to_be_allocated].
Then proceed to type in the user responses to the inputs that are prompted.
Wait for CESM models to build and successfully run then confirm whether load balancing software should be initiated.


