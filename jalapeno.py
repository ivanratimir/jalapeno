import sys
import argparse
import numpy as np
import jpeg_toolbox as jt
from Crypto.Hash import HMAC, SHA256
from utils.image_utils import *
from utils.file_processing_utils import *
from utils.syndrome_utils import calculate_points_dir, calculate_points_inv


def main():

    parser = argparse.ArgumentParser(description="jalapeno: JPEG steganography in the DCT domain")
    subparsers = parser.add_subparsers(dest="task")
                     
    info = subparsers.add_parser('info', help='prints image capacity')
    info.add_argument('-ci', type=str, help='cover image path', required=True)
    info.add_argument('-k', type=int, help='binary block size', default=1)
    info.add_argument('-ch', type=int, help='YCbCr channel', choices=[0,1,2], default=0)
        
    embed = subparsers.add_parser('embed', help='embed a secret file')
    embed.add_argument('-sf', type=str, help='secret file path', required=True)
    embed.add_argument('-ci', type=str, help='cover image path', required=True)
    embed.add_argument('-k', type=int, help='binary block size', default=1)
    embed.add_argument('-ch', type=int, help='YCbCr channel', choices=[0,1,2], default=0)

    extract = subparsers.add_parser('extract', help='extract a secret file')
    extract.add_argument('-si', type=str, help='stego image path', required=True)
    extract.add_argument('-k', type=int, help='binary block size', default=1)
    extract.add_argument('-ch', type=int, help='YCbCr channel', choices=[0,1,2], default=0)

    args = parser.parse_args()


    match args.task:

        case 'info':

            k = np.abs(args.k)
            ch = args.ch
            im_path = args.ci
            im_type = get_im_type(im_path)

            if im_type in types["lossles"]:

                q = quality_prompt()
                im_path = convert_to_jpeg(im_path, q)
                im_type = "JPG"

            if im_type not in types["lossy"]:

                print("unsupported cover")
                sys.exit(1)

            # load cover DCT coefficients
            im = jt.load(im_path)
            c_cfs = im["coef_arrays"][ch]
            c_cfs1 = c_cfs.flatten()

            # embedding conditions
            cond0 = (c_cfs1 != 0)
            cond1 = (c_cfs1 != 1)
            ids_arr0 = np.where(cond0 & cond1)[0]
            n_pts = len(ids_arr0)

            if k == 1:
                byte_cap = n_pts // 8
            
            else:
                b_len = 2 ** k
                # cap in n of blocks
                n_b = n_pts // b_len
                byte_cap = k*n_b // 8

            print(f"\ncover -capacity: {byte_cap} B\n")

    
        case 'embed':

            sf_path = args.sf
            im_path = args.ci
            ch = args.ch
            k = np.abs(args.k)

            if not os.path.exists(sf_path):
                print(f"error: {sf_path} doesn't exist!")
                sys.exit(1)

            im_type = get_im_type(im_path)

            if im_type in types["lossles"]:

                q = quality_prompt()
                im_path = convert_to_jpeg(im_path, q)
                im_type = "JPG"

            if im_type not in types["lossy"]:

                print("unsupported cover")
                sys.exit(1)
        
            aes_passw = input("\nenter file encryption password: ")
            p1_b, p2_b = process_file_to_binary(sf_path, k, aes_passw)

            # k=1: n of bits (=embedding pts); k>1: n of bin blocks
            n1_b = len(p1_b)
            n2_b = len(p2_b)

            # for LSB method
            if k == 1:
                n_pts1 = n1_b
                n_pts2 = n2_b

            # for syndrome coding method
            else:
                out = calculate_points_dir(k, n1_b, n2_b)
                n_pts1 = out[0]
                n_pts2 = out[1]
                shape_ids1 = out[2]
                shape_ids2 = out[3]

            # load cover DCT coefficients
            im = jt.load(im_path)
            c_cfs = im["coef_arrays"][ch]
            # flat cover coeffs array
            c_cfs1 = c_cfs.flatten()

            # embedding conditions
            cond0 = (c_cfs1 != 0)
            cond1 = (c_cfs1 != 1)
            ids_arr0 = np.where(cond0 & cond1)[0]

            if (n_pts1+n_pts2) > len(ids_arr0):
                print("error: exceeded image embedding capacity")
                sys.exit(1)

            rng_passw = input("enter image embedding password: ")
            key = hash_digest(rng_passw)
            seed = int.from_bytes(key)
            rng = np.random.default_rng(seed)

            # indices selection for p1_b and p2_b embedding
            sel1 = rng.choice(ids_arr0, n_pts1, 0)
            mask = ~np.isin(ids_arr0, sel1)
            ids_arr1 = ids_arr0[mask]
            sel2 = rng.choice(ids_arr1, n_pts2, 0)

            # for syndrome coding method
            if k > 1:
                sel1 = np.reshape(sel1, shape_ids1)
                sel2 = np.reshape(sel2, shape_ids2)

            # flat stego coefficients array s_arr1
            s_cfs1 = embed_dct(c_cfs1, sel1, p1_b, k)
            s_cfs1 = embed_dct(c_cfs1, sel2, p2_b, k)

            shape = im["coef_arrays"][ch].shape
            s_cfs = s_cfs1.reshape(shape)
            im["coef_arrays"][ch] = s_cfs

            print("\nsaving stego image...")
            jt.save(im, 'stego.jpg')
    

        case 'extract':

            k = np.abs(args.k)
            ch = args.ch

            # load stego DCT coefficients
            im = jt.load(args.si)
            s_cfs = im["coef_arrays"][ch]
            s_cfs1 = s_cfs.flatten()

            # embedding conditions
            cond0 = (s_cfs1 != 0)
            cond1 = (s_cfs1 != 1)
            ids_arr0 = np.where(cond0 & cond1)[0]

            rng_passw = input("enter image embedding password: ")
            key = hash_digest(rng_passw)
            seed = int.from_bytes(key)
            rng = np.random.default_rng(seed)

            # part 1: 19 bytes = 16 B (iv) + 3 B (encrypted size)
            # for LSB method
            if k == 1:
                n_pts1 = 19 * 8
            # for syndrome coding method
            else:
                n_pts1, shape_ids1 = calculate_points_inv(k, 19)

            # indices selection with embedded p1_b
            sel1 = rng.choice(ids_arr0, n_pts1, 0)

            if k > 1:
                sel1 = np.reshape(sel1, shape_ids1)

            p1_b = extract_dct(s_cfs1, sel1, k)
            p1_B = bits_to_bytes(merge_unpad(p1_b))

            iv = p1_B[:16]
        
            aes_passw = input("enter file encryption password: ")
            key = hash_digest(aes_passw)

            ciphertext = p1_B[16:]
            size = decrypt(iv, ciphertext, key)
            size = int.from_bytes(size)

            # part 2: excracted "size" number of B + 32 B (for mac)
            if k == 1:
                n_pts2 = (size+32) * 8
            else:
                n_pts2, shape_ids2 = calculate_points_inv(k, size+32)

            if n_pts2 > (len(ids_arr0)-n_pts1):
                print("error: extracted size exceeded capacity")
                sys.exit(1)

            # indices selection with embedded p2_b
            mask = ~np.isin(ids_arr0, sel1)
            ids_arr1 = ids_arr0[mask]
            sel2 = rng.choice(ids_arr1, n_pts2, 0)

            if k > 1:
                sel2 = np.reshape(sel2, shape_ids2)

            p2_b = extract_dct(s_cfs1, sel2, k)
            p2_B = bits_to_bytes(merge_unpad(p2_b))

            ciphertext += p2_B[:-32]
            mac = p2_B[-32:]

            print("")
            plaintext = decrypt(iv, ciphertext, key)
            try:
                HMAC.new(key, plaintext, SHA256).verify(mac)

                data = plaintext[3:]

                f_name = data[1:1+data[0]].decode()
                f_data = data[1+data[0]: ]
        

                print(f"saving exctracted {f_name} file...")
                with open(f_name, "wb") as f:
    
                    f.write(f_data)
            except:
                print("error: plaintext failed authentication!")
                sys.exit(1)
                

        case _:

            parser.print_help()


def quality_prompt():

    q = 0
    print("cover image will be converted to a JPEG format!")
    while not (0 < q <= 100):
        q = int(input("input JPEG cover quality (0-100): "))
            
    return q


if __name__ == '__main__':

    welcome_ascii = r"""
   _       _                                           
  (_) __ _| | __ _ _ __   ___ _ __   ___   _ __  _   _ 
  | |/ _` | |/ _` | '_ \ / _ \ '_ \ / _ \ | '_ \| | | |
  | | (_| | | (_| | |_) |  __/ | | | (_) || |_) | |_| |
 _/ |\__,_|_|\__,_| .__/ \___|_| |_|\___(_) .__/ \__, |
|__/              |_|                     |_|    |___/ 

        """
    print(welcome_ascii)

    main()

