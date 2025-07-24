from PIL import Image
import numpy as np
from .syndrome_utils import get_syndrome


def get_im_type(path):

    ext = path.rsplit(".")[-1]

    match ext:

        case "png":
            return "PNG"
        case "bmp":
            return "BMP"
        case "jpg":
            return "JPG"
        case "jpeg":
            return "JPG"
        case "tif":
            return "TIFF"
        case "tiff":
            return "TIFF"
        case _:
            return "Unknown"


types = {"lossy": "JPG",
         "lossles": ["PNG", "BMP", "TIFF"]}        
        

def convert_to_jpeg(path, quality):

    with Image.open(path) as im:

        rgb_im = im.convert('RGB')   
        rgb_im.save(path + ".jpg", format='JPEG', quality=quality)

    # converted cover path 
    return path + ".jpg"


def match_lsb(cf):

    match cf:
        case -2047.0:
            cf += 1.0
        case  2047.0:
            cf -= 1.0
        case -1.0:
            cf -= 1.0
        case  2.0:
            cf += 1.0
        case _:
            cf += np.random.choice([-1., 1.])

    return cf


def embed_dct(array, ids, bits, k):

    # LSB +/-1 embedding method (matching)
    if k == 1:
        for b, i in zip(bits, ids):

            cf = array[i]
            if int(cf)%2 != int(b):
                    
                cf1 = match_lsb(cf)
                array[i] = cf1

    # syndrome coding method
    else:
        for b, i in zip(bits, ids):

            # DCT coefficient block
            cfs = array[i]
            # cover LSB block
            c = (cfs % 2).astype(int)
            syn = get_syndrome(c)
            err = syn ^ int(b, 2)

            if err != 0:

                mod = i[err]
                cf = array[mod]
                cf1 = match_lsb(cf)
                array[mod] = cf1

    return array


def extract_dct(array, ids, k):
        
    bits = []

    # LSB +/-1 embedding method
    if k == 1:
        for i in ids:

            cf = array[i]
            b = int(cf) % 2
            bits.append(str(b))

    # syndrome coding method
    else:
        for i in ids:

            # DCT coefficient block
            cfs = array[i]
            # stego LSB block
            s = (cfs % 2).astype(int)
            syn = get_syndrome(s)
            b = bin(syn)[2:].zfill(k)
            bits.append(b)
        
    return bits



