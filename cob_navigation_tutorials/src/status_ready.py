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
    handle_arm_left = sss.move("arm_left","folded",False)
    handle_arm_right = sss.move("arm_right","folded",False)
    
    #wait for all components to reach target
    handle_arm_left.wait()
    handle_arm_right.wait()

    # robot is ready now
    sss.say("sound", ["I am ready now."])
