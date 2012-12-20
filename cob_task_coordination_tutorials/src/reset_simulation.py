#!/usr/bin/python

import roslib
roslib.load_manifest('cob_task_coordination_tutorials')
import rospy

from std_srvs.srv import *

from simple_script_server import *
sss = simple_script_server()
		
if __name__ == "__main__":
	rospy.init_node("reset_simulation")
	reset = rospy.ServiceProxy('/gazebo/reset_simulation', Empty)
	rospy.wait_for_service('/gazebo/reset_simulation')
	
	# wait for some time until all objects are spawned
	rospy.sleep(5)
	
	print "reset simulation"
	reset()
