from math import ceil

def dec2bin_int(x):
    return int(bin(x)[2:])

def str2bin_str(message):
    return ''.join(format(ord(i), '08b') for i in message)

def bin_len(x):
    return len(bin(x)) - 2

# Numbers must be in a string format. "011010" -> 0b011010
def right_rotate(num, bits):
    bin_number_len = 32

    num = int(num, 2)
    right = (num >> bits)|(num << (bin_number_len - bits)) & (2**bin_number_len - 1)
    return right


def SHA256(message):
    # Followed the steps from https://qvault.io/cryptography/how-sha-2-works-step-by-step-sha-256/

    # Step 1 – Pre-Processing
    message = str2bin_str(message)

    original_size = len(message)

    message += "1"

    my_size = ceil(len(message) / 512) * 512 - 64

    message += "0" * (my_size - (original_size + 1))

    bin_original_size = dec2bin_int(original_size)
    size_bin_original_size = sum(1 for i in bin(original_size)) - 2
    message += "0" * (64 - size_bin_original_size)
    message += str(bin_original_size)

    # Step 2 - initialize Hash Values (h)
    h0 = 0x6a09e667
    h1 = 0xbb67ae85
    h2 = 0x3c6ef372
    h3 = 0xa54ff53a
    h4 = 0x510e527f
    h5 = 0x9b05688c
    h6 = 0x1f83d9ab
    h7 = 0x5be0cd19

    # Step 3 - Initialize Round Constants (k)
    k = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

    # Step 4 - Chunk Loops
    count = 0
    for j in range(int(len(message)/512)):
        # Step 5 – Create Message Schedule (w)
        w = []

        for i in range(16):
            word = ""
            for j in range(count, count + 32):
                word += message[j]
            w.append(word)
            count += 32

        for i in range(48):
            w.append("0"*32)

        for i in range(16, 64):
            s0 = (right_rotate(w[i - 15], 7)) ^ (right_rotate(w[i - 15], 18)) ^ (int(w[i - 15], 2) >> 3)
            s1 = (right_rotate(w[i - 2], 17)) ^ (right_rotate(w[i - 2], 19)) ^ (int(w[i - 2], 2) >> 10)
            w[i] = int(w[i - 16], 2) + s0 + int(w[i - 7], 2) + s1

            w[i] = w[i] % 0x100000000

            w[i] = bin(w[i])[2:]


        # Step 6 - Compression
        a = h0
        b = h1
        c = h2
        d = h3
        e = h4
        f = h5
        g = h6
        h = h7

        for i in range(64):
            S1 = (right_rotate(bin(e), 6)) ^ (right_rotate(bin(e), 11)) ^ (right_rotate(bin(e), 25))
            ch = (e & f) ^ ((~e) & g)
            temp1 = h + S1 + ch + k[i] + int(w[i], 2)
            temp1 = temp1 % 0x100000000

            S0 = (right_rotate(bin(a), 2)) ^ (right_rotate(bin(a), 13)) ^ (right_rotate(bin(a), 22))
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = S0 + maj
            temp2 = temp2 % 0x100000000

            h = g
            g = f
            f = e
            e = d + temp1
            e = e % 0x100000000

            d = c
            c = b
            b = a
            a = temp1 + temp2
            a = a % 0x100000000

        # Step 7 - Modify Final Values
        h0 += a
        h0 = h0 % 0x100000000

        h1 += b
        h1 = h1 % 0x100000000

        h2 += c
        h2 = h2 % 0x100000000

        h3 += d
        h3 = h3 % 0x100000000

        h4 += e
        h4 = h4 % 0x100000000

        h5 += f
        h5 = h5 % 0x100000000

        h6 += g
        h6 = h6 % 0x100000000

        h7 += h
        h7 = h7 % 0x100000000

    return format(h0, '#010x')[2:] + format(h1, '#010x')[2:] + format(h2, '#010x')[2:] + format(h3, '#010x')[2:] + format(h4, '#010x')[2:] + format(h5, '#010x')[2:] + format(h6, '#010x')[2:] + format(h7, '#010x')[2:]


if __name__ == "__main__":
    print(SHA256("In the case of an infinitesimally small elastic sphere, the effect of a tidal force is to distort the shape of the body without any change in volume. The sphere becomes an ellipsoid with two bulges, pointing towards and away from the other body. Larger objects distort into an ovoid, and are slightly compressed, which is what happens to the Earth's oceans under the action of the Moon. The Earth and Moon rotate about their common center of mass or barycenter, and their gravitational attraction provides the centripetal force necessary to maintain this motion. To an observer on the Earth, very close to this barycenter, the situation is one of the Earth as body 1 acted upon by the gravity of the Moon as body 2. All parts of the Earth are subject to the Moon's gravitational forces, causing the water in the oceans to redistribute, forming bulges on the sides near the Moon and far from the Moon."))