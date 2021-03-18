# webcam_analyzer
Docker image to analyze my webcam images.

## What is the project about?
My webcam does have an alerting mechanism which alerts, when there are some changes in the picture. However,
this mechanism is not very reliable, so I let the camera record as many images as it can. The camera does this 
about 1-3 per second (depending on the lighting), which makes several thousand a day. In order to go through
those immense amount of images, I need a way to filter out only those, where actually some change is happening.

The algorithm to analyze the images requires a rather delicate setup. In the end it is based on OpenCV, which is
run through python. Because I would like to run the analysis on different machines (e.g. my NAS, my laptop, etc.)
I decided to write a docker container, which then can be run anywhere.

## How does it work?
Roughly speaking, the algorithm reads all files in a directory in alphabetical order. It then compares two adjacent
images and if more than 1.000 pixels have changed, it counts the image as an alert. Then a new image in a subdirectory
`check` is created, which highlights the areas, which have changed.

In the end, some more image processing tricks are done, but that are the more standard things like converting the image
to grayscale, smoothing the image, accumulated the image, etc.

The basic principle goes back on some code by [Peter Mortensen](http://stackoverflow.com/questions/3374828/how-do-i-track-motion-using-opencv-in-python),
but has been altered since and moved to a newer OpenCV version.

There is also a configuration file, with which you can mask areas, where changes should not result in an alert, and 
set up some other parameters.

## Config file

The config file is based on yaml. A sample file looks like this:

```yaml
ignore:
  - 0x0-1280x200
  - 0x950-1280x960
minsquare: 20
alert_threshold: 1000
new_image_threshold: 100000
```

With the `ignore` field you can define an array of areas in your image, which should be ignored. The areas are given
with the top left point to the bottom right point. In the first example it hides an area from the top left position (0,0)
to a position (1280,200).

The config value `minsquare` gives a minimum square size, in which changes are detected. For example if you have a bush and
the leaves move, you can have lots of small detections. With this value you can ignore those small changes.

The `alert_threshold` gives the number of pixels, which should create the alert. So only if this many pixels have
changed, an alert is thrown.

The `new_image_threshold` finally gives the number of pixels, when we consider the image as a new image. In my case,
this happens if the camera switched from day to night mode. Then a lot of pixels change and we basically restart
the detection process again.

The config file is optional.


## How to run?
Without a configuration file:
```bash
docker run -v [local path to images]:/data ghcr.io/tobehh/webcam_analyze
```

With a configuration file:
```bash
docker run -v [local path to images]:/data -v [path to local config file]:/app/config.yml ghcr.io/tobehh/webcam_analyze
```
