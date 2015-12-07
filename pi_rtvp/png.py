from array import array
import itertools
import numpy as np
import png
import subprocess
import pi_rtvp.camera as camera
import pi_rtvp.util as util

class PNGImage(object):
    def __init__(self, infile, width = 0, height = 0, data = None, info = None):
        try:
            self.file = infile
            if (infile != None):
                image = png.Reader(infile).asDirect()
                self.width = image[0]
                self.height = image[1]
                self.data = np.vstack(map(np.uint8, image[2]))
                self.info = image[3]
            else:
                self.width = width
                self.height = height
                self.data = data
                self.info = info
            self.planes = self.info.get("planes", 3) # assume RGB if planes is missing
            self.greyscale = self.info.get("greyscale", False)
        except FileNotFoundError:
            raise

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return "{}({!r}, {!r}, {!r}, {!r}, {!r})".format(util.fullname(self),
                                                         self.file, self.width,
                                                         self.height, self.data,
                                                         self.info)

    def __str__(self):
        return "{}: {}x{} {}".format(self.file, self.width, self.height, self.info)

    def write(self, outfile):
        writer = png.Writer(self.width, self.height, **self.info)
        if isinstance(outfile, str):
            with open(outfile, "wb") as f:
                writer.write(f, self.data)
        else:
            writer.write(outfile, self.data)

    def to_greyscale(self):
        return convert_to_greyscale(self)

    def is_matrix_in_bounds(self, y, x, size, median):
        return (y - median >= 0 and x - median >= 0 and
                y + median <= self.height - 1 and x + median <= self.width - 1)

    def get_matrix_at(self, y, x, size):
        median = int(size / 2)
        if not self.is_matrix_in_bounds(y, x, size, median):
            if is_corner(self, y, x, size):
                return corner_matrix(self, y, x, size)
            else:
                return edge_matrix(self, y, x, size)
        else:
            yl = y - median
            xl = x - median
            data = np.empty((size,size))
            data = self[yl:yl+size,xl:xl+size]
            return data

class PNGImageStream(object):
    def __init__(self):
        self.data = b''
        self.image = None

    def write(self, s):
        self.data += s

    def flush(self):
        a = array("B")
        a.frombytes(self.data)
        self.image = PNGImage(a)

def capture_picam(picamera):
    stream = PNGImageStream()
    picamera.capture(stream, format="png")
    return stream.image()

def capture_usbcam(usbcamera):
    cap = usbcamera.capture("-", stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    data = array('B')
    data.frombytes(cap.stdout)
    return PNGImage(data)

def convert_to_greyscale(image):
    data = []
    info = image.info.copy();
    r_coeff = 0.2126
    g_coeff = 0.7152
    b_coeff = 0.0722
    for row in image:
        for i in range(0, image.width*image.planes, image.planes):
            grey = round(r_coeff*row[i]+g_coeff*row[i+1]+b_coeff*row[i+2])
            data.append(grey)
    data = np.array(data, dtype=np.uint8).reshape(image.height, image.width)
    info["planes"] = 1
    info["greyscale"] = True
    info["alpha"] = False
    if "background" in info:
        info["background"] = (255)
    return PNGImage(None, image.width, image.height, data, info)

def is_corner(image, y, x, size):
    median = int(size / 2)
    return (x - median <= 0 and y - median <= 0 or
            x - median <= 0 and y + median >= image.height - 1 or
            x + median >= image.width - 1 and y - median <= 0 or
            x + median >= image.width - 1 and y + median >= image.height - 1)

# This stuff is tricky to think about - is there an easier way?
def corner_matrix(image, y, x, size):
    data = []
    median = int(size / 2)
    if x - median <= 0 and y - median <= 0:
        # top left - outs first, extend starts
        for i in range(0, median+1):
            extend_corner(data, image, y, x, -median)
            for j in range(0, median+1):
                data.append(image[y, x+j])
        for i in range(median+1, size):
            extend_corner(data, image, y+i, x, -median)
            for j in range(0, median+1):
                data.append(image[y+i, x+j])
    elif x - median <= 0 and y + median >= image.height - 1:
        # bottom left - ins first, extend starts
        for i in range(size, median+1, -1):
            imidx = i - 1
            extend_corner(data, image, y-imidx, x, -median)
            for j in range(0, median+1):
                data.append(image[y-imidx, x+j])
        for i in range(median+1, 0, -1):
            extend_corner(data, image, y, x, -median)
            for j in range(0, median+1):
                data.append(image[y, x+j])
    elif x + median >= image.width - 1 and y - median <= 0:
        # top right - outs first, extend ends
        for i in range(0, median+1):
            for j in range(median, -1, -1):
                data.append(image[y, x-j])
            extend_corner(data, image, y, x, median)
        for i in range (median+1, size):
            for j in range(median, -1, -1):
                data.append(image[y+i, x-j])
            extend_corner(data, image, y+i, x, median)
    elif x + median >= image.width - 1 and y + median >= image.height - 1:
        # bottom right - ins first, extend ends
        for i in range(size, median+1, -1):
            imidx = i - 1
            for j in range(median, -1, -1):
                data.append(image[y-imidx, x-j])
            extend_corner(data, image, y-imidx, x, median)
        for i in range(median+1, 0, -1):
            idx = size - i
            for j in range(median, -1, -1):
                data.append(image[y, x-j])
            extend_corner(data, image, y, x, median)
    return np.array(data).reshape(size, size)

def extend_corner(data, image, y, x, median):
    if median > 0:
        for i in range(0, median):
            try:
                data.append(image[y, x+median-i])
            except IndexError:
                data.append(image[y, x])
    else:
        for i in range(0, median, -1):
            try:
                # python treats negative list indices as list[len(list)-n]
                if x+median-i < 0:
                    raise IndexError
                data.append(image[y, x+median-i])
            except IndexError:
                data.append(image[y, x])

def edge_matrix(image, y, x, size):
    data = []
    median = int(size / 2)
    if y - median <= 0:
        # top row, outs first
        for (i, j) in itertools.product(range(0, median+1), range(0, size)):
            jdx = j - median
            try:
                if y - median - i < 0:
                    raise IndexError
                data.append(image[y-median+i, x+jdx])
            except IndexError:
                data.append(image[y, x+jdx])
        for (i, j) in itertools.product(range(median+1, size), range(0, size)):
            jdx = j - median
            data.append(image[y+i, x+jdx])
    elif y + median >= image.height - 1:
        # bottom row, outs last
        for (i, j) in itertools.product(range(size, median+1, -1), range(0, size)):
            idx = size - i
            imidx = i - 1
            jdx = j - median
            data.append(image[y-imidx, x+jdx])
        for (i, j) in itertools.product(range(median+1, 0, -1), range(0, size)):
            idx = size - i
            jdx = j - median
            try:
                data.append(image[y+idx-median, x+jdx])
            except IndexError:
                data.append(image[y, x+jdx])
    elif x - median <= 0:
        # left side, extend first
        for (i, j) in itertools.product(range(0, size), range(0, size)):
            idx = i - median
            jdx = j - median
            try:
                if x+jdx < 0:
                    raise IndexError
                data.append(image[y+idx, x+jdx])
            except IndexError:
                data.append(image[y+idx, x])
    elif x + median >= image.width - 1:
        # right side, extend last
        for (i, j) in itertools.product(range(0,size), range(0, size)):
            idx = i - median
            jdx = j - median
            try:
                data.append(image[y+idx, x+jdx])
            except IndexError:
                data.append(image[y+idx, x])
    return np.array(data).reshape(size, size)
