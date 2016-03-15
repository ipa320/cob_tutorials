#!/usr/bin/python

import time

import roslib
roslib.load_manifest('cob_script_server_tutorial')
import rospy


from simple_script_server import script

import tf
from geometry_msgs.msg import *
from moveit_msgs.srv import *

#this should be in manipulation_msgs
#from cob_mmcontroller.msg import *

class GraspScript(script):

	def Initialize(self):

		# initialize components (not needed for simulation)
		self.sss.init("tray")
		self.sss.init("torso")
		self.sss.init("arm")
		self.sss.init("sdh")
		self.sss.init("base")
		self.istener = tf.TransformListener(True, rospy.Duration(10.0))

		# move to initial positions
		handle_arm = self.sss.move("arm","folded",False)
		handle_torso = self.sss.move("torso","home",False)
		handle_sdh = self.sss.move("sdh","home",False)
		self.sss.move("tray","down")
		handle_arm.wait()
		handle_torso.wait()
		handle_sdh.wait()
		if not self.sss.parse:
			print "Please localize the robot with rviz and press ENTER"
		self.sss.wait_for_input()


	def callIKSolver(self, current_pose, goal_pose):
		req = GetPositionIKRequest()
		req.ik_request.ik_link_name = "sdh_grasp_link"
		#req.ik_request.ik_seed_state.joint_state.position = current_pose # does not exist in moveit_msgs
		req.ik_request.pose_stamped = goal_pose
		resp = self.iks(req)
		result = []
		for o in resp.solution.joint_state.position:
			result.append(o)
		return (result, resp.error_code)

	def Run(self):
		self.iks = rospy.ServiceProxy('/arm_kinematics/get_ik', GetPositionIK)
		listener = tf.TransformListener(True, rospy.Duration(10.0))
		rospy.sleep(2)

		# prepare for grasping
		handle01 = self.sss.move("base","kitchen")
		handle01.wait()
		handle02 = self.sss.move("base",[-2.116, 0.089, 0.000])
		handle02.wait()
		self.sss.move("arm","pregrasp")
		#self.sss.wait_for_input()
		handle_sdh = self.sss.move("sdh","cylopen",False)
		handle_sdh.wait()

		# caculate tranformations, we need cup coordinates in arm_7_link coordinate system it is done for milk_box
		object_pose_bl = PoseStamped()
		object_pose_bl.header.stamp = rospy.Time.now()
		object_pose_bl.header.frame_id = "/map"
		object_pose_bl.pose.position.x = -2.95
		object_pose_bl.pose.position.y = 0.05
		object_pose_bl.pose.position.z = 1.07
		rospy.sleep(2)


		if not self.sss.parse:
			object_pose_in = PoseStamped()
			object_pose_in = object_pose_bl
			object_pose_in.header.stamp = listener.getLatestCommonTime("/base_link",object_pose_in.header.frame_id)
			object_pose_bl = listener.transformPose("/base_link", object_pose_in)
			rospy.sleep(2)
			[new_x, new_y, new_z, new_w] = tf.transformations.quaternion_from_euler(-1.552, -0.042, 2.481) # rpy
			object_pose_bl.pose.orientation.x = new_x
			object_pose_bl.pose.orientation.y = new_y
			object_pose_bl.pose.orientation.z = new_z
			object_pose_bl.pose.orientation.w = new_w

			arm_pre_grasp = rospy.get_param("/script_server/arm/pregrasp")


			# calculate ik solutions for grasp configuration
			(grasp_conf, error_code) = self.callIKSolver(arm_pre_grasp[0], object_pose_bl)
			if(error_code.val != error_code.SUCCESS):
				rospy.logerr("Ik grasp Failed")
				#return 'retry'
			handle_arm = self.sss.move("arm", [grasp_conf])
			handle_arm.wait()
			handle01 = self.sss.move("sdh","cylclosed")
			handle01.wait()
			self.sss.move("arm","grasp")


		handle01 = self.sss.move("arm","grasp-to-tray",False)
		self.sss.move("tray","up")
		handle01.wait()
		self.sss.move("arm","tray")
		self.sss.move("sdh","cylopen")
		handle01 = self.sss.move("arm","tray-to-folded",False)
		self.sss.sleep(4)
		self.sss.move("sdh","cylclosed",False)
		handle01.wait()

		# deliver cup to order position
		self.sss.move("base","order")
		self.sss.say("Here's your drink.")
		self.sss.move("torso","nod")

if __name__ == "__main__":
	SCRIPT = GraspScript()
	SCRIPT.Start()
