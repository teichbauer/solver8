
def get_bit(val, bit):
    return (val >> bit) & 1


def set_bit(val, bit_index, new_bit_value):
    """ Set the bit_index (0-based) bit of val to x (1 or 0)
        and return the new val. the input param val remains unmodified.
        """
    mask = 1 << bit_index  # mask - integer with just the chosen bit set.
    val &= ~mask           # Clear the bit indicated by the mask (if x == 0)
    if new_bit_value:
        val |= mask        # If x was True, set the bit indicated by the mask.
    return val             # Return the result, we're done.


def set_bits(val, d):
    for b, v in d.items():
        val = set_bit(val, b, v)
    return val


def get_sdic(filename):
    path = './configs/' + filename
    sdic = eval(open(path).read())
    return sdic


def print_json(nov, vkdic, fname):

    def ordered_dic_string(d):
        m = '{ '
        ks = list(sorted(list(d.keys()), reverse=True))
        for k in ks:
            m += str(k) + ': ' + str(d[k]) + ', '
        m = m.strip(', ')
        m += ' }'
        return m

    sdic = {
        'nov': nov,
        'kdic': {}
    }
    for kn, vk in vkdic.items():
        sdic['kdic'][kn] = vk.dic
    ks = sorted(list(sdic['kdic'].keys()))

    with open(fname, 'w') as f:
        f.write('{\n')
        f.write('    "nov": ' + str(sdic['nov']) + ',\n')
        f.write('    "kdic": {\n')
        # for k, d in sdic['kdic'].items():
        for k in ks:
            msg = ordered_dic_string(sdic['kdic'][k])
            line = f'        "{k}": {msg},'
            f.write(f'{line}\n')
        f.write('    }\n}')


def drop_bits(vkdic, bits):
    ''' bits=[7,5,4] - top-bits to be dropped (must be top ones in vkdic)
        loop thru every vk, if no bits left(vk empty): put into dropped;
        if 1,2 or 3 bit remaining: put into nvkdic, among these, if
        no bit touched by bits(vk.bits remains the same): 
        put into untouched
        return 3 dicts and length of bits - all together 4 values
        '''
    nvkdic = {}  # new dic with every vk dropping bits
    untouched = {}
    dropped = {}
    drop_set = set(bits)
    for vkn, vk in vkdic.items():
        s = set(vk.bits)
        remain_set = s - drop_set
        if len(remain_set) > 0:
            nvkdic[vkn] = vk.clone(bits)  # remove the bits and clone
            if s == remain_set:
                untouched[vkn] = vk.clone(bits)
        else:  # len(remain_set) == 0
            dropped[vkn] = vk
    # return nvkdic and cnt of dropped bits
    return untouched, dropped, nvkdic, len(bits)
