The scripts in this folder create a graph to determine if one configuartion is reachable from another. Python 2.7 is required to run these scripts.

*************************************
RelocationSolutionVerification.py
*************************************
		
	Running:
	* python RelocationSolutionVerification.py

	This script verifies that there exists a sequence of tilts to traverse from one side of the gadget to the other if a directed tunnel from its entrance to its exit exists, i.e. the state tile is in the correct path to indicate that directed tunnel. The state tile being stuck in the NE path indicates tunnels pointing South and West, the state tilke being stuck in the SW path indicates directed tunnels pointing North and East. The script will place the state tile in each path and calculate all possible positions it can be in while stuck in that path. It will combine every starting state tile position with every of the four starting robot positions (N,E,S,W entrances). With 11 locations in each state tile path and 4 starting robot positions this allows for 88 starting positions. Half of these are valid, meaning a directed tunnel exists from the robots starting location to the location opposite of the gadget. The other half are invalid, meaning that a directed tunnel does not exist from the robots location to the location opposite on the gadget. Our goal was to show that for the invalid starting positions there is no sequence of tilts that will get you to the other side of the gadget. Using the starting configurations it will create a graph of all the possible configurations reached by recursively performing tilts on each configuration, and adding an edge between configurations that are reachable from one another. It will not add configurations already in the graph. We mark nodes that achieve the solution configuration, and add pointers to these nodes to a seperate set. Our script shows that the robot can only traverse a gadget from a starting position such that a directed tunnel exists from the robots starting location to the location on the opposite side of the gadget.

	Running:
		python RelocationSolutionVerification.py

	Modifiers:
		Line 33: checkFor = "invalid" 

		- This can be changed to "valid", "invalid", or "all". This will change the starting configurations that the script will calculate. "valid" will record all starting configurations that the robot polyomino should be able to traverse through the gadget. "invalid" will record starting positions that the robot polyomino is not able to traverse through the gadget. "all" will calculate both of these.

		Output:
		For every starting position (represented as a string e.g. "05253125"), a tree will be created representing every position reachable by a sequence of tilts. If the solution configuration is reached from that starting position the node is marked and solved, after the creation of a tree the node is marked as solved. The number of solution nodes is outputted for each starting position.

				Tree Creation Complete for: 26501624
				Total Nodes: 580
				Solution Nodes: 10

				- This shows that there are 10 configurations such that the robot polyomino made it across the gadget. it can be seen that if invalid starting positions are used then no solutions will be found.




*************************************
StateChangeVerification.py
*************************************

	Running:
	* python StateChangeVerification.py

	This script checks if it is possible to traverse our gadget without changing the path that our state tile is confined to. The path of the state tile is crucial to our gadget as it implies the state that our gadget is in. We must ensure that the state tile changes its path when the gadget is traversed if we want to ensure that it can mimic the properties of a C2T gadget. This gadget uses the same method as before, the output is slightly different:

			Tree Creation Complete for: 26501624
			Total Nodes: 580
			Solution Nodes: 10
			Broken Nodes: 0

			- The only difference is the "Broken Nodes", which represent configurations where the robot polyomino has traversed the gadget and the state tile has not changed the confined path that it is on. The script tells us that for every starting configuration, there is no sequence of tilts that will allow you to traverse the gadget in a way that the state tile does not change its confined path. This ensure the toggling function of our gadget.

*************************************
ReconfigurationSolutionVerification.py
*************************************

	Running:
	* python ReconfigurationSolutionVerification.py

	This script has the same function and same modifiers as RelocationSolutionVerification.py.




