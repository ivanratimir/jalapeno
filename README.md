# jalapeno 🌶️

**Make juicy JPEGs embedded with secrets using `jalapeno.py`.** 

## Overview

`jalapeno.py` is a **python script able to encrypt and embed, as well as extract and decrypt hidden messages (as files) in JPEG's quantized DCT coefficients.**

## Disclaimer

This software is provided for educational and research purposes only. The author is not responsible for any misuse of this software.

While the script is inspired by concepts used in JPEG steganography, it is not a full or faithful implementation of the Outguess, F3, F5 algorithm or any other specific published steganographic method. It is built on [`piquillo.py`](https://codeberg.org/ijuranovic/piquillo) script structure and adapted for embedding in the DCT domain with selected methods, avoiding coefficients equal to 0 (as a general rule originating from the *Jsteg* algorithm) and embedding those equal to 1 with a rule for LSB +/- 1 embedding to increase embedding capacity.

## Features

- **Cover image capacity analysis**
- **Password-based pseudo-random embedding for enhanced security**
- **Encryption of file name, content, and size before embedding**
- **HMAC-based verification of decrypted data before writing output during extraction**
- **Default use of LSB +/- 1 embedding**
- **Use of syndrome coding when set binary block size *k* is > 1**

## Requirements

`jalapeno.py` additionaly relies on [`jpeglib`](https://jpeglib.readthedocs.io/en/latest/) package for low-level reading and writing of JPEG's quantized DCT coefficients.

All packages are listed in `requirements.txt`, which can be installed in a python virtual environment.

## Usage

The CLI is structured and defined using `argparse`, which allows for a simple access to helping manuals. To access the default help manual type:

**`python jalapeno.py -h`**

Presented tasks are:

- **`check`**
- **`embed`**
- **`extract`**

To access help manual for each task and to list arguments type:

`python jalapeno.py [task] -h`

Where `[task]` is replaced with one of the listed without brackets.

Default value for `k` is 1 and for `ch` is 0 (*Y* or *luminance* channel of *YCbCr* color space), unless set differently with one of possible choices.

**Embedding example (*Cb* channel):**

`python jalapeno.py embed -ci cover.jpg -mf message.txt -k 4 -ch 1`

*enter encryption (1) and embedding (2) passwords, following with stego image name (e.g. stego.jpg)...*

**Extraction example (*Cb* channel):**

`python jalapeno.py extract -si stego.jpg -k 4 -ch 1 `

*enter extraction (2) and decryption (1) passwords...*

**Note about the *k* binary block size number:**

Secret message file is encrypted and converted to bits, which are divided into equal *k* length blocks for syndrome coding with LSB +/- 1 embedding.

*Syndrome coding* (also referred to as *matrix embedding*) is an efficient method of embedding k bits of data by modifying a single pixel value. More about this method of embedding can be found on [Daniel Lerch's website](https://daniellerch.me/stego/codes/binary-hamming-en/), which explains in greater detail how it's applied for hiding information. The applied method in this project is based on the interpretation of Hamming codes from [3Blue1Brown's video](https://www.youtube.com/watch?v=b3NxrZOu_CE), which allows for a more flexible (length) application and helps avoid matrix definitions. 

## Acknowledgements
Main CLI structure is inspired by [`steghide`](https://steghide.sourceforge.net/) (a known piece of steganography software), as well as by aesthetics of [`tomato.py`](https://github.com/itsKaspar/tomato) (itsKaspar's python script to glitch AVI files). 