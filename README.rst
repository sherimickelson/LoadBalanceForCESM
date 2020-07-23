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

--

cesm_allocation.py
The load balncing software code is initiated in this file and the function that manages the highest level function amongst b2deg_alternative.py and cesm_allocation.py. This python file is the one that is run from the command line.

Setup

Basic Execution Instructions:
In the command line, type cesm_allocation.py [max_tasks_to_be_allocated].
Then proceed to type in the user responses to the inputs that are prompted.
Wait for CESM models to build and successfully run then confirm whether load balancing software should be initiated. 


