
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


def topbits_coverages(vk, topbits):
    ''' example: vk.dic: {7:1, 4:1, 1:0}, topbits:[7,6]. for the 2 bits
        allvalues: [00,01,10,11]/[0,1,2,3] vk only hit 10/2,11/3, 
        {4:1, 1:0} lying outside of topbits - outdic: {4:1, 1:0}
        return [2,3], {4:1, 1:0}
        '''
    outdic = {}
    L = len(topbits)
    allvalues = list(range(2**L))
    coverage_range = allvalues[:]
    new_nov = vk.nov - len(topbits)

    dic = {}
    for b in vk.dic:
        if b in topbits:
            dic[b - new_nov] = vk.dic[b]
        else:
            outdic[b] = vk.dic[b]
    for x in allvalues:
        conflict = False
        for bit, v in dic.items():
            if get_bit(x, bit) != v:
                conflict = True
                break
        if conflict:
            coverage_range.remove(x)
    return coverage_range, outdic
