FROM python:3.9

WORKDIR /app

RUN apt-get update \
    && apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        yasm \
        pkg-config \
        libswscale-dev \
        libtbb2 \
        libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libavformat-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install numpy

ENV OPENCV_VERSION="4.5.0"
RUN wget https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip \
&& unzip ${OPENCV_VERSION}.zip \
&& mkdir /app/opencv-${OPENCV_VERSION}/cmake_binary \
&& cd /app/opencv-${OPENCV_VERSION}/cmake_binary \
&& cmake -DBUILD_TIFF=ON \
  -DBUILD_opencv_java=OFF \
  -DWITH_CUDA=OFF \
  -DWITH_OPENGL=ON \
  -DWITH_OPENCL=ON \
  -DWITH_IPP=ON \
  -DWITH_TBB=ON \
  -DWITH_EIGEN=ON \
  -DWITH_V4L=ON \
  -DBUILD_TESTS=OFF \
  -DBUILD_PERF_TESTS=OFF \
  -DCMAKE_BUILD_TYPE=RELEASE \
  -DCMAKE_INSTALL_PREFIX=$(python3.9 -c "import sys; print(sys.prefix)") \
  -DPYTHON_EXECUTABLE=$(which python3.9) \
  -DPYTHON_INCLUDE_DIR=$(python3.9 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
  -DPYTHON_PACKAGES_PATH=$(python3.9 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
  .. \
&& make install \
&& rm /app/${OPENCV_VERSION}.zip \
&& rm -r /app/opencv-${OPENCV_VERSION}
RUN ln -s \
  /usr/local/python/cv2/python-3.9/cv2.cpython-37m-x86_64-linux-gnu.so \
  /usr/local/lib/python3.9/site-packages/cv2.so
RUN ln -s /usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml /app/haarcascade_frontalface_default.xml

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "analyze.py"]
