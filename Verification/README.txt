The scripts in this folder create a graph to determine if one configuartion is reachable from another. Python 2.7 is required to run these scripts.

*************************************
RelocationSolutionVerification.py
*************************************
	This script verifies that there exists a sequence of tilts to traverse from one side of the gadget to the other if a directed tunnel from its entrance to its exit exists, i.e. the state tile is in the correct path to indicate that directed tunnel. The state tile being stuck in the NE path indicates tunnels pointing South and West, the state tilke being stuck in the SW path indicates directed tunnels pointing North and East. The script will place the state tile in each path and calculate all possible positions it can be in while stuck in that path. It will combine every starting state tile position with every of the four starting robot positions (N,E,S,W entrances). With 11 locations in each state tile path and 4 starting robot positions this allows for 88 starting positions. Half of these are valid, meaning a directed tunnel exists from the robots starting location to the location opposite of the gadget. The other half are invalid, meaning that a directed tunnel does not exist from the robots location to the location opposite on the gadget. Our goal was to show that for the invalid starting positions there is no sequence of tilts that will get you to the other side of the gadget. Using the starting configurations it will create a graph of all the possible configurations reached by recursively performing tilts on each configuration, and adding an edge between configurations that are reachable from one another. It will not add configurations already in the graph. We mark nodes that achieve the solution configuration, and add pointers to these nodes to a seperate set. Our script shows that the robot can only traverse a gadget from a starting position such that a directed tunnel exists from the robots starting location to the location on the opposite side of the gadget.

	Running:
		python RelocationSolutionVerification.py

	Modifiers:
		Line 33: checkFor = "invalid" 

		- This can be changed to "valid", 			"invalid", or "all". This will change the starting configurations that the script will calculate.




*************************************
StateChangeVerification.py
*************************************


