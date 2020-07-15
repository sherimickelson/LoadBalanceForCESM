==================
LoadBalanceForCESM
==================

About
-----
This repository contains code and instructions relevant to the load balancing endeavor for CESM.

Contributors:
-------------
**Mentors:
John Dennis, Sheri Mickelson, and Brian Dobbins
**Students:
Soudeh Kamali and Thomas Johnson III

b2deg_alternative.py
Contains majority of the code related to building and running CESM models. The configuration for the built models happens within this python file.

--

cesm_allocation.py
The load balncing software code is initiated in this file and the function that manages the highest level function amongst b2deg_alternative.py and cesm_allocation.py. This python file is the one that is run from the command line.
