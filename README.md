# RealSense
# realsense D435 on RaspberryPi-3 B+
- Spec  
  RaspberryPi-3 Model B+  
  Rasbian strech  
  32GB SDCard  
  
- Initial Status as of insertion  
```
  # lsusb
    Bus 001 Device 003: ID 8086:0ad6 Intel Corp. 
    Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
  # dmesg | tail
    [   27.144227] random: crng init done
    [   87.431432] usb 1-1: reset high-speed USB device number 2 using dwc2
    [   87.671574] usb 1-1: device firmware changed
    [   87.671618] usb 1-1: USB disconnect, device number 2
    [   87.961433] usb 1-1: new high-speed USB device number 3 using dwc2
    [   88.213666] uvcvideo: Unknown video format 00000050-0000-0010-8000-00aa00389b71
    [   88.213680] uvcvideo: Unknown video format 00000032-0000-0010-8000-00aa00389b71
    [   88.214374] uvcvideo: Found UVC 1.50 device Intel(R) RealSense(TM) 430 (8086:0ad6)
    [   88.215664] uvcvideo: Unable to create debugfs 1-3 directory.
    [   88.215996] input: Intel(R) RealSense(TM) 430 as /devices/platform/sopc@0/ffb00000.usb/usb1/1-1/1-1:1.0/input/input1
  # ls /dev/video*
    /dev/video0  /dev/video1
```

### [RaspberryPi3 + Raspbian Stretch環境への導入](https://qiita.com/PINTO/items/2ad10526f9b2e1c8cdf3)  

- Check **prerequisites**  

Permitt **trusted-host**,  
```
$ vi .pip/pip.conf
[global]
trusted-host = pypi.python.org
               pypi.org
               files.pythonhosted.org
               www.piwheels.org

$ git config --global http.sslVerify false
```

```  
# apt update;apt upgrade
# reboot
$ uname -a
Linux raspberrypi 4.19.42-v7+ #1219 SMP Tue May 14 21:20:58 BST 2019 armv7l GNU/Linux

$ gcc -v
gcc (Raspbian 6.3.0-18+rpi1+deb9u1) 6.3.0 20170516

$ cmake --version
cmake version 3.7.2
```

**Dilate swap area**.  
```
# vi /etc/dphys-swapfile
CONF_SWAPSIZE=2048

# /etc/init.d/dphys-swapfile restart swapon -s
```
**In below work, make uses -j1 and -i.  -j1 means to avoid memory overflow, -i means ignore make errors.**  

Install depended packages.  
```
  # apt-get install libxml2-dev libxslt-dev python-dev
  # pip3 install pillow lxml matplotlib cython
```

Upgrade **cmake**.  
```
  $ wget https://cmake.org/files/v3.11/cmake-3.11.4.tar.gz
  $ tar -zxvf cmake-3.11.4.tar.gz;rm cmake-3.11.4.tar.gz
  $ cd cmake-3.11.4
  $ ./configure --prefix=/home/pi/cmake-3.11.4
  $ make -j1
  $ sudo make install
  $ export PATH=/home/pi/cmake-3.11.4/bin:$PATH
  $ source ~/.bashrc
  $ cmake --version
    cmake version 3.11.4
  $ export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

Install **protobuf**  
```
  $ git clone --depth=1 -b v3.5.1 https://github.com/google/protobuf.git
  $ cd protobuf
  $ ./autogen.sh
  $ ./configure
  $ make
  # make install
  $ cd python
  $ export LD_LIBRARY_PATH=../src/.libs
  $ python3 setup.py build --cpp_implementation 
  $ python3 setup.py test --cpp_implementation
  # python3 setup.py install --cpp_implementation
  $ export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
  $ export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION=3
  # ldconfig
  $ protoc --version
    libprotoc 3.5.1
```

Needs **gtk+, opengl** for python  
```
  # apt-get install build-essential libgtk-3-dev libgtk-2.0-dev
  # apt-get install freeglut3-dev libgl2.0-dev libglext1-dev
  # apt-get install python-opengl
  # pip3 install pyopengl
  # pip3 install pyopengl_accelerate
  # raspi-config
    "7.Advanced Options" - "A7 GL Driver" - "G2 GL (Fake KMS)"
  # reboot
```

Needs **TBB**.  
```
  $ cd ~
  $ wget https://github.com/PINTO0309/TBBonARMv7/raw/master/libtbb-dev_2018U2_armhf.deb
  # dpkg -i ~/libtbb-dev_2018U2_armhf.deb
  # ldconfig
  $ rm libtbb-dev_2018U2_armhf.deb
```

Needs i**mage format** supporting lib.  
```
  # apt install libjpeg-dev libtiff5-dev libpng12-dev libjasper-dev libavcodec-dev libavformat-dev libswscale-dev
  # apt install libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev
```

**librealsense** from git.  
```
  $ git clone https://github.com/IntelRealSense/librealsense
  # cp librealsense/config/99-realsense-libusb.rules /etc/udev/rules.d
  # udevadm control --reload-rules && udevadm trigger

```

Make **librealsense**.  
```
  # apt install libglext1 libglext1-dev
  $ cd ~/librealsense;mkdir build;cd build
  $ cmake .. -DBUILD_EXAMPLES=true
  or
  $ cmake ../ -DFORCE_LIBUVC=true -DBUILD_PYTHON_BINDINGS=true
  $ make -j1 -i   # -i means ignore error
  # make install
```
Make **OpenCV** with TBB and OpenGL.  
```
  # apt install libavresample-dev libv4l-dev
  # apt install mesa-utils* libglu1* libgles2-mesa-dev
  $ wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.4.1.zip
  $ unzip opencv.zip;rm opencv.zip
  $ wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.4.1.zip
  $ unzip opencv_contrib.zip;rm opencv_contrib.zip
  $ cd ~/opencv-3.4.1/;mkdir build;cd build
  $ cmake -D CMAKE_CXX_FLAGS="-DTBB_USE_GCC_BUILTINS=1 -D__TBB_64BIT_ATOMICS=0" \
          -D CMAKE_BUILD_TYPE=RELEASE \
          -D CMAKE_INSTALL_PREFIX=/usr/local \
          -D INSTALL_PYTHON_EXAMPLES=OFF \
          -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.4.1/modules \
          -D BUILD_EXAMPLES=OFF \
          -D PYTHON_DEFAULT_EXECUTABLE=$(which python3) \
          -D INSTALL_PYTHON_EXAMPLES=OFF \
          -D BUILD_opencv_python2=ON \
          -D BUILD_opencv_python3=ON \
          -D WITH_OPENCL=OFF \
          -D WITH_OPENGL=ON \
          -D WITH_TBB=ON \
          -D BUILD_TBB=OFF \
          -D WITH_CUDA=OFF \
          -D ENABLE_NEON:BOOL=ON \
          -D WITH_QT=OFF \
          -D WITH_OPENGL=ON \
          -D BUILD_TESTS=OFF ..
  $ make -j1
  $ sudo make install
  $ sudo ldconfig
```
