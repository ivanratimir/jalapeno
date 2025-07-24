# jalapeno

Steganography scripts for embedding and extracting secret message files within the quantized DCT coefficients of JPEG compressed images, developed as a part of an image and signal processing course project and thesis. **This is a continutation of the [piquillo ](https://codeberg.org/ijuranovic/piquillo) script, developed with the same functional flow - but for steganography in the DCT (frequency) domain.**

## Disclaimer

This software is provided for educational and research purposes only. The author is not responsible for any misuse of this software.

## Features

- loading an image of other supported type (like TIFF, BMP or PNG) and saving with JPEG 
- checking cover image capacity
- key (password) based pseudo random embedding 
- reading message file bytes directly and embedding with file name (file agnostic)
- encryption of file name, content and size using AES in CFB mode before embedding
- HMAC based verification of decrypted file before writing output at extraction
- default use of LSB +/- 1 embedding, use of syndrome coding when set binary block size *k* is > 1

## Requirements

In addition to packages used for the piquillo (`pillow` and `numpy` packages for image processing, `pycryptodome` for cryptographic operations), the script relies on [Daniel Lerch's `python-jpeg-toolbox`](https://github.com/daniellerch/python-jpeg-toolbox) for low level reading, modifying and saving JPEG quantized DCT coefficients.. These packages are listed in `requirements.txt`, which can be installed in a python virtual environment. For example, to setup an environment on Linux based systems run the following command in a terminal:

`python3 -m venv .venv`

To activate to created environment run the following command:

`source .venv/bin/activate`

To install the requirements using `pip` run:

`pip install -r requirements.txt`

## Usage

Main processing script is **`jalapeno.py`**, with CLI style inspired by *steghide* (a known steganography tool). The CLI is structured and defined using `argparse`, which allows for a simple access to helping manuals at each running point. To access the default help manual type:

**`python jalapeno.py -h`**

Presented tasks are:

- **`info`**
- **`embed`**
- **`extract`**

To access help manual for each task and to list arguments type:

`python jalapeno.py [task] -h`

Where `[task]` is replaced with one of the listed without brackets.

In order for the file to be successfuly extracted it has to use the right:
- stego image
- set passwords
- set *k* binary block size number
- set YCbCr color channel (0, 1 or 2)

**Embedding example:**

`python jalapeno.py embed -ci cover.jpg -sf message.txt -k 4 -ch 1`

*enter encryption and embedding passwords...*

*output **stego.png** (default) will be created...*

**The default YCbCr color channel for embedding and extracting is Y** (luminance component) with the highest offered embedding capacity (due to how the JPEG works), which does not have to be set directly.

**Extraction example:**

```python jalapeno.py extract -si stego.png -k 4 -ch 1```

*enter encryption and embedding passwords...*

*output **message.txt** (embedded file name) will be created...*

**Note about the *k* binary block size number:**

**The default value for k is 1** for use with LSB +/- 1 embedding, **which does not have to be specified**. IF the k is set to be higher, syndrome coding will be used. Read file when encrypted and converted to bits will be divided into equal *k* length blocks for syndrome coding. This also means it is no longer necessary to modify up to one DCT coefficient for storing a single secret bit (if the LSB doesn't match), but by modifying one coefficient LSB k bits can be stored (one binary block). This reduces the number of modifications (inserting less noise into image), but also reduces the capacity of image. 

More about *syndrome coding* (also referred to as *matrix embedding*) can be found on [Daniel Lerch's website](https://daniellerch.me/stego/codes/binary-hamming-en/), which helped me understand how this type of embedding method is applied for hiding information (together with other types). The applied method in this project is based on the interpretation of Hamming codes from [3Blue1Brown's video](https://www.youtube.com/watch?v=b3NxrZOu_CE), which allows for a more flexible (length) application and helps avoid matrix definitions.



