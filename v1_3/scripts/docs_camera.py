from threading import Condition
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from picamera2.controls import Controls


""" Video format descriptions:
 XBGR8888 - every pixel is packed into 32-bits, with a dummy 255 value at the end, so a pixel would look like [R, G, B,
 255] when captured in Python. (These format descriptions can seem counter-intuitive, but the underlying
 infrastructure tends to take machine endianness into account, which can mix things up!)
 • XRGB8888 - as above, with a pixel looking like [B, G, R, 255].
 • RGB888 - 24 bits per pixel, ordered [B, G, R].
 • BGR888 - as above, but ordered [R, G, B].
 • YUV420 - YUV images with a plane of Y values followed by a quarter plane of U values and then a quarter plane of V
 values
"""

""" Raw stream and sensor configuration"""
from pprint import *
from picamera2 import Picamera2
picam2 = Picamera2()
 # output omitted
pprint(picam2.sensor_modes)
 # output omitted
"""
 [{'bit_depth': 10,
  'crop_limits': (696, 528, 2664, 1980),
  'exposure_limits': (31, 66512892),
  'format': SRGGB10_CSI2P,
  'fps': 120.05,
  'size': (1332, 990),
  'unpacked': 'SRGGB10'},
 {'bit_depth': 12,
  'crop_limits': (0, 440, 4056, 2160),
  'exposure_limits': (60, 127156999),
 4.2. Configurations in more detail
 21
The Picamera2 Library
  'format': SRGGB12_CSI2P,
  'fps': 50.03,
  'size': (2028, 1080),
  'unpacked': 'SRGGB12'},
 {'bit_depth': 12,
  'crop_limits': (0, 0, 4056, 3040),
  'exposure_limits': (60, 127156999),
  'format': SRGGB12_CSI2P,
  'fps': 40.01,
  'size': (2028, 1520),
  'unpacked': 'SRGGB12'},
 {'bit_depth': 12,
  'crop_limits': (0, 0, 4056, 3040),
  'exposure_limits': (114, 239542228),
  'format': SRGGB12_CSI2P,
  'fps': 10.0,
  'size': (4056, 3040),
  'unpacked': 'SRGGB12'}
"""

"""
This gives us the exact sensor modes that we can request, with the following information for each mode:
 • bit_depth - the number of bits in each pixel sample.
 • crop_limits - this tells us the exact field of view of this mode within the full resolution sensor output. In the example
 above, only the final two modes will give us the full field of view.
 • exposure_limits - the maximum and minimum exposure values (in microseconds) permitted in this mode.
 • format - the packed sensor format. This can be passed as the "format" when requesting the raw stream.
 • fps - the maximum framerate supported by this mode.
 • size - the resolution of the sensor output. This value can be passed as the "size" when requesting the raw stream.
 • unpacked - use this in place of the earlier format in the raw stream request if unpacked raw images are required (see
 below). We recommend anyone wanting to access the raw pixel data to ask for the unpacked version of the
 format
"""

""" The Raw Stream Configuration
 >>> modes = picam2.sensor_modes
 >>> mode = modes[0]
 >>> mode
 {'format': SRGGB10_CSI2P, 'unpacked': 'SRGGB10', 'bit_depth': 10, 'size': (1332, 990), 'fps':
 120.05, 'crop_limits': (696, 528, 2664, 1980), 'exposure_limits': (31, 2147483647, None)}
 >>> config = picam2.create_preview_configuration(sensor={'output_size': mode['size'],
 'bit_depth': mode['bit_depth']})
 >>> picam2.configure(config)
 >>> picam2.camera_configuration()['raw']
 {'format': 'SBGGR10_CSI2P', 'size': (1332, 990), 'stride': 1696, 'framesize': 1679040}

  >>> config = picam2.create_preview_configuration(raw={'format': 'SRGGB12'},
 sensor={'output_size': mode['size'], 'bit_depth': mode['bit_depth']})
 >>> picam2.configure(config)
 >>> picam2.camera_configuration()['raw']
 {'format': 'SBGGR10', 'size': (1332, 990), 'stride': 2688, 'framesize': 2661120}

  >>> config = picam2.create_preview_configuration(raw={'format': 'SRGGB10', 'size': (1332, 990)})
 >>> picam2.configure(config)
 >>> picam2.camera_configuration()['sensor']
 {'bit_depth': 10, 'output_size': (1332, 990)}

  >>> config = picam2.create_preview_configuration(raw={'format': 'SBGGR10_CSI2P', 'size': (1332,
 990)})
 >>> picam2.configure(config)
 >>> picam2.camera_configuration()['sensor']
 {'bit_depth': 10, 'output_size': (1332, 990)}
 >>> picam2.camera_configuration()['raw']
 {'format': 'BGGR16_PISP_COMP1', 'size': (1332, 990), 'stride': 1344, 'framesize': 1330560}
  >>> config = picam2.create_preview_configuration(raw={'format': 'SBGGR10', 'size': (1332, 990)})
 >>> picam2.configure(config)
 >>> picam2.camera_configuration()['sensor'
  {'bit_depth': 10, 'output_size': (1332, 990)}
 >>> picam2.camera_configuration()['raw']
 {'format': 'SBGGR16', 'size': (1332, 990), 'stride': 2688, 'framesize': 2661120}
"""

""" Configurations and runtime camera controls"""
from picamera2 import Picamera2
picam2 = Picamera2()
picam2.create_video_configuration()["controls"]
# {'NoiseReductionMode': <NoiseReductionMode.Fast: 1>, 'FrameDurationLimits': (33333, 33333)}
from picamera2 import Picamera2
picam2 = Picamera2()
config = picam2.create_video_configuration(controls={"FrameDurationLimits": (40000, 40000)})


#Camera controls
# This time we set the controls after configuring the camera, but before starting it. For example:
from picamera2 import Picamera2
picam2 = Picamera2()
picam2.camera_controls

picam2.set_controls({"ExposureTime": 10000, "AnalogueGain": 1.0})
picam2.start()

# Here too the controls will have already been applied on the very first frame that we receive from the camera.
""" 
#  Setting controls after the camera has started
# This time, there will be a delay of several frames before the controls take effect. This is because there is perhaps quite a
# large number of requests for camera frames already in flight, and for some controls (exposure time and analogue gain
# specifically), the camera may actually take several frames to apply the updates.
"""
from picamera2 import Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()
picam2.set_controls({"ExposureTime": 10000, "AnalogueGain": 1.0})

"""Object syntax for camera controls
 We saw previously how control values can be associated with a particular camera configuration.
 There is also an embedded instance of the Controls class inside the Picamera2 object that allows controls to be set
 subsequently. For example, to set controls after configuration but before starting the camera:

"""
from picamera2 import Picamera2
picam2 = Picamera2()
picam2.configure("preview")
picam2.controls.ExposureTime = 10000
picam2.controls.AnalogueGain = 1.0
picam2.start()
#To set these controls after the camera has started we should use:
from picamera2 import Picamera2
picam2 = Picamera2()
picam2.configure("preview")
picam2.start()
with picam2.controls as controls:
    controls.ExposureTime = 10000
    controls.AnalogueGain = 1.0

""" Autofocus control
 Autofocus controls obey the same general rules as all other controls, however, some guidance will be necessary before
 they can be used effectively. These controls should work correctly so long as the version of libcamera being used (such
 as that supplied by Raspberry Pi) implements libcamera's published autofocus API correctly, and the attached camera
 module actually has autofocus (such as the Raspberry Pi Camera Module 3).
 Camera modules that do not support autofocus (including earlier Raspberry Pi camera modules and the HQ camera)
 will not advertise these options as being available (in the Picamera2.camera_controls property), and attempting to set them
 will fail.

  Autofocus Modes and State
   The autofocus (AF) state machine has 3 modes, and its activity in each of these modes can be monitored by reading the
 "AfState" metadata that is returned with each image. The 3 modes are:
 • Manual - The lens will never move spontaneously, but the "LensPosition" control can be used to move the lens
 "manually". The units for this control are dioptres (1 / distance in metres), so that zero can be used to denote
 "infinity". The "LensPosition" can be monitored in the image metadata too, and will indicate when the lens has
 reached the requested location.
 • Auto - In this mode the "AfTrigger" control can be used to start an autofocus cycle. The "AfState" metadata that is
 received with images can be inspected to determine when this finishes and whether it was successful, though we
 recommend the use of helper functions that save the user from having to implement this. In this mode too, the lens
 will never move spontaneously until it is "triggered" by the application.
 • Continuous - The autofocus algorithm will run continuously, and refocus spontaneously when necessary.
 Applications are free to switch between these modes as required.

  Continuous Autofocus
 For example, to put the camera into continuous autofocus mode:
"""
from picamera2 import Picamera2
from libcamera import controls
picam2 = Picamera2()
picam2.start(show_preview=True)
picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})

# Setting the Lens Position Manually
# To put the camera into manual mode and set the lens position to infinity:
from picamera2 import Picamera2
from libcamera import controls
picam2 = Picamera2()
picam2.start()
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 0.0})
"""The lens position control
 The lens position control (use picam2.camera_controls['LensPosition']) gives three values which are the minimum,
 maximum and default lens positions. The minimum value defines the furthest focal distance, and the maximum
 specifies the closest achieveable focal distance (by taking its reciprocal). The third value gives a "default" value, which
 is normally the hyperfocal position of the lens.
 The minimum value for the lens position is most commonly 0.0 (meaning infinity). For the maximum, a value of 10.0
 would indicate that the closest focal distance is 1 / 10 metres, or 10cm. Default values might often be around 0.5 to 1.0,
 implying a hyperfocal distance of approximately 1 to 2m.
 In general, users should expect the distance calibrations to be approximate as it will depend on the accuracy of the
 tuning and the degree of variation between the user’s module and the module for which the calibration was performed.
"""

"""Triggering an Autofocus Cycle
 For triggering an autofocus cycle in Auto mode, we recommend using a helper function that monitors the autofocus
 algorithm state for you, handles any complexities in the state transitions, and returns when the AF cycle is complete:
"""
from picamera2 import Picamera2
from libcamera import controls
picam2 = Picamera2()
picam2.start(show_preview=True)
success = picam2.autofocus_cycle()
"""
 The function returns True if the lens focused successfully, otherwise False. Should an application wish to avoid blocking
 while the autofocus cycle runs, we recommend replacing the final line (success = picam2.autofocus_cycle()) by
"""
job = picam2.autofocus_cycle(wait=False)
 # Now do some other things, and when you finally want to be sure the autofocus
 # cycle is finished:
success = picam2.wait(job)
#  This is in fact the normal method for running requests asynchronously - please see see the section on asynchronous capture for more details.

""" Other Autofocus Controls
 The other standard libcamera autofocus controls are also supported, including:
 • "AfRange" - adjust the focal distances that the algorithm searches
 • "AfSpeed" - try to run the autofocus algorithm faster or slower
 • "AfMetering" and "AfWindows" - lets the user change the area of the image used for focus.
 To find out more about these controls, please consult the appendices or the libcamera documentation and search for Af.
 Finally, there is also a Qt application that demonstrates the use of the autofocus API.

"""

"""Camera properties
 Camera properties represent information about the sensor that applications may want to know. They cannot be
 changed by the application at any time, neither at runtime nor while configuring the camera, although the value of these
 properties may change whenever the camera is configured.
 Camera properties may be inspected through the camera_properties property of the Picamera2 object:
"""
from picamera2 import Picamera2
picam2 = Picamera2()
picam2.camera_properties

"""
 Some examples of camera properties include the model of sensor and the size of the pixel array. After configuring the
 camera into a particular mode it will also report the field of view from the pixel array that the mode represents, and the
 sensitivity of this mode relative to other camera modes.
 A complete list and explanation of each property can be found in the appendices
"""
# create video configuration
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (1280, 720), "format": "RGB888"},
                                                 lores={"size": (640, 480), "format": "XBGR8888"})
picam2.configure(video_config)

# start camera
picam2.start()
time.sleep(1)

# get camera capture metadata
metadata = picam2.capture_metadata()
# set exposure time, analogue gain, and colour gains
controls = {c: metadata[c] for c in ["ExposureTime", "AnalogueGain", "ColourGains"]}
picam2.set_controls(controls)

# set auto exposure and auto white balance off
picam2.set_controls({"AwbEnable": 0, "AeEnable": 0})

# set control with with statement
with picam2.controls as ctrl:
    ctrl.AnalogueGain = 6.0
    ctrl.ExposureTime = 60000

time.sleep(2)

ctrls = Controls(picam2)
ctrls.AnalogueGain = 1.0
ctrls.ExposureTime = 10000
picam2.set_controls(ctrls)

# start recording and encoding
encoder1 = H264Encoder(10000000)
encoder2 = MJPEGEncoder(10000000)

picam2.start_recording(encoder1, 'test1.h264')
time.sleep(5)
picam2.start_encoder(encoder2, 'test2.mjpeg', name="lores")
time.sleep(5)
picam2.stop_encoder(encoder2)
time.sleep(5)
picam2.stop_recording()

# Timestamped video
from picamera2 import MappedArray, Picamera2
from picamera2.encoders import H264Encoder

picam2 = Picamera2()

# fine tune video configuration
tuning = Picamera2.load_tuning_file("imx477.json")
algo = Picamera2.find_tuning_algo(tuning, "rpi.agc")
if "channels" in algo:
    algo["channels"][0]["exposure_modes"]["normal"] = {"shutter": [100, 66666], "gain": [1.0, 8.0]}
else:
    algo["exposure_modes"]["normal"] = {"shutter": [100, 66666], "gain": [1.0, 8.0]}

picam2 = Picamera2(tuning=tuning)

picam2.configure(picam2.create_video_configuration())

colour = (0, 255, 0)
origin = (0, 30)
font = cv2.FONT_HERSHEY_SIMPLEX
scale = 1
thickness = 2


def apply_timestamp(request):
    timestamp = time.strftime("%Y-%m-%d %X")
    with MappedArray(request, "main") as m:
        cv2.putText(m.array, timestamp, origin, font, scale, colour, thickness)


picam2.pre_callback = apply_timestamp

encoder = H264Encoder(10000000)
# set title fields
picam2.title_fields = ["ExposureTime", "AnalogueGain", "DigitalGain"]
time.sleep(2)
picam2.start_recording(encoder, "test.h264")
time.sleep(5)
picam2.stop_recording()

# Example of setting controls. Here, after one second, we fix the AGC/AEC
# to the values it has reached whereafter it will no longer change.

import time

from picamera2 import Picamera2, Preview

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)

preview_config = picam2.create_preview_configuration()
picam2.configure(preview_config)

picam2.start()
time.sleep(1)

metadata = picam2.capture_metadata()
controls = {c: metadata[c] for c in ["ExposureTime", "AnalogueGain", "ColourGains"]}
print(controls)

picam2.set_controls(controls)
time.sleep(5)

# Example of setting controls using the "direct" attribute method.

import time

from picamera2 import Picamera2, Preview
from picamera2.controls import Controls

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)

preview_config = picam2.create_preview_configuration()
picam2.configure(preview_config)

picam2.start()
time.sleep(1)

with picam2.controls as ctrl:
    ctrl.AnalogueGain = 6.0
    ctrl.ExposureTime = 60000

time.sleep(2)

ctrls = Controls(picam2)
ctrls.AnalogueGain = 1.0
ctrls.ExposureTime = 10000
picam2.set_controls(ctrls)

time.sleep(2)

# Another (simpler!) way to fix the AEC/AGC and AWB.

import time

from picamera2 import Picamera2, Preview

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)

preview_config = picam2.create_preview_configuration()
picam2.configure(preview_config)

picam2.start()
time.sleep(1)

picam2.set_controls({"AwbEnable": 0, "AeEnable": 0})
time.sleep(5)

# How to do digital zoom using the "ScalerCrop" control.

import time

from picamera2 import Picamera2, Preview

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)

preview_config = picam2.create_preview_configuration()
picam2.configure(preview_config)

picam2.start()
time.sleep(2)

size = picam2.capture_metadata()['ScalerCrop'][2:]

full_res = picam2.camera_properties['PixelArraySize']

for _ in range(20):
    # This syncs us to the arrival of a new camera frame:
    picam2.capture_metadata()

    size = [int(s * 0.95) for s in size]
    offset = [(r - s) // 2 for r, s in zip(full_res, size)]
    picam2.set_controls({"ScalerCrop": offset + size})

time.sleep(2)

import time

import cv2
import numpy as np

from picamera2 import Picamera2

# Simple Mertens merge with 3 exposures. No image alignment or anything fancy.
RATIO = 3.0

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

# Run for a second to get a reasonable "middle" exposure level.
time.sleep(1)
metadata = picam2.capture_metadata()
exposure_normal = metadata["ExposureTime"]
gain = metadata["AnalogueGain"] * metadata["DigitalGain"]
picam2.stop()
controls = {"ExposureTime": exposure_normal, "AnalogueGain": gain}
capture_config = picam2.create_preview_configuration(main={"size": (1024, 768),
                                                           "format": "RGB888"},
                                                     controls=controls)
picam2.configure(capture_config)
picam2.start()
normal = picam2.capture_array()
picam2.stop()

exposure_short = int(exposure_normal / RATIO)
picam2.set_controls({"ExposureTime": exposure_short, "AnalogueGain": gain})
picam2.start()
short = picam2.capture_array()
picam2.stop()

exposure_long = int(exposure_normal * RATIO)
picam2.set_controls({"ExposureTime": exposure_long, "AnalogueGain": gain})
picam2.start()
long = picam2.capture_array()
picam2.stop()

merge = cv2.createMergeMertens()
merged = merge.process([short, normal, long])
merged = np.clip(merged * 255, 0, 255).astype(np.uint8)
cv2.imwrite("normal.jpg", normal)
cv2.imwrite("merged.jpg", merged)