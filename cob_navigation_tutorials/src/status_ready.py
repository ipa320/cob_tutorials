#!/usr/bin/python

import roslib
roslib.load_manifest('cob_navigation_tutorials')
import rospy

from simple_script_server import *
sss = simple_script_server()
		
if __name__ == "__main__":
	rospy.init_node("navigation_tutorials")
	rospy.sleep(2)

	# move robot components concurrent
	handle_arm = sss.move("arm","folded",False)
	handle_tray = sss.move("tray","down",False)
	handle_torso = sss.move("torso","front",False)
	handle_sdh = sss.move("sdh","cylclosed",False)
	handle_head = sss.move("head","front",False)
	
	#wait for all components to reach target
	handle_arm.wait()
	handle_tray.wait()
	handle_torso.wait()
	handle_sdh.wait()
	handle_head.wait()

	# move to side
	sss.move_base_rel("base",[0,-0.1,0])
	
	# robot is ready now
	sss.say(["I am ready now."])
