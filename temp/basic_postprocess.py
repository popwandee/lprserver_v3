import hailo

# Importing VideoFrame before importing GST is must
from gsthailo import VideoFrame
from gi.repository import Gst

# Create 'run' function, that accepts one parameter - VideoFrame, more about VideoFrame later.
# `run` is default function name if no name is provided
def run(video_frame: VideoFrame):
    print("My first Python postprocess!")

    return Gst.FlowReturn.OK