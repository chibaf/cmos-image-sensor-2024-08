# cmos-image-sensor-2024-08
# raspberry pi camera
# interface 2024-08

<pre>
  [0:44:34.026223471] [29650]  INFO RPI vc4.cpp:621 Sensor: /base/soc/i2c0mux/i2c@1/imx708@1a - Selected sensor format: 1536x864-SBGGR10_1X10 - Selected unicam format: 1536x864-pBAA
Traceback (most recent call last):
  File "/home/pi/list1.py", line 78, in <module>
    raw = Strm2Img(stream)                              # 2æ¬¡åéåã«å¤æ
          ^^^^^^^^^^^^^^^^
  File "/home/pi/list1.py", line 61, in Strm2Img
    data = data.reshape((Shape[0], Shape[1]))[:Crop[0], :Crop[1]]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: cannot reshape array of size 0 into shape (1952,3264)

</pre>
