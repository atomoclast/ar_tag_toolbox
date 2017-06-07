#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Point, PoseStamped
from ar_track_alvar_msgs.msg import AlvarMarkers

class TagsCOG():
    def __init__(self):
        rospy.init_node("ar_tags_cog")
        
        # Read in an optional list of valid tag ids
        self.tag_ids = rospy.get_param('~tag_ids', None)
        
        # Publish the COG on the /target_pose topic as a PoseStamped message
        self.tag_pub = rospy.Publisher("target_pose", PoseStamped, queue_size=5)

        rospy.Subscriber("ar_pose_marker", AlvarMarkers, self.get_tags)
        
        rospy.loginfo("Publishing combined tag COG on topic /target_pose...")
                
    def get_tags(self, msg):
        # Initialize the COG as a PoseStamped message
        tag_cog = PoseStamped()
        
        # Get the number of markers
        n = len(msg.markers)
        
        # If no markers detected, just return
        if n == 0:
            return

        # Iterate through the tags and sum the x, y and z coordinates            
        for tag in msg.markers:
            
            # Skip any tags that are not in our list
            if self.tag_ids is not None and not tag.id in self.tag_ids:
                continue
            
            # Sum up the x, y and z position coordinates of all tags
            tag_cog.pose.position.x += tag.pose.pose.position.x
            tag_cog.pose.position.y += tag.pose.pose.position.y
            tag_cog.pose.position.z += tag.pose.pose.position.z
            
             # Compute the COG
            tag_cog.pose.position.x /= n
            tag_cog.pose.position.y /= n
            tag_cog.pose.position.z /= n
            
            # Give the tag a unit orientation
            tag_cog.pose.orientation.w = 1

            # Add a time stamp and frame_id
            tag_cog.header.stamp = rospy.Time.now()
            tag_cog.header.frame_id = msg.markers[0].header.frame_id

            # Publish the COG
            self.tag_pub.publish(tag_cog)      
  
if __name__ == '__main__':
    try:
        TagsCOG()
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("AR Tag Tracker node terminated.")