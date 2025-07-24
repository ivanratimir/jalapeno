def get_syndrome(bits):
    
    syn = 0
    for i, bit in enumerate(bits):
        if bit:
            syn ^= i
            
    return syn


# for embedding with syndrome coding
def calculate_points_dir(k, n_b1, n_b2):

    b_len = 2 ** k

    n_pts1 = n_b1 * b_len
    n_pts2 = n_b2 * b_len

    shape_ids1 = (n_b1, b_len)
    shape_ids2 = (n_b2, b_len)

    return [n_pts1, n_pts2, shape_ids1, shape_ids2]


# for extraction with coded syndrome
def calculate_points_inv(k, size):

    b_len = 2 ** k
    n_b = (size*8//k + int(size*8%k !=0))

    n_pts = b_len * n_b
    shape_ids = (n_b, b_len)
    
    return [n_pts, shape_ids]