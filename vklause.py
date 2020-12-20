from basics import get_bit, set_bit, set_bits


class VKlause:
    ''' veriable klause - klause with 1, 2 or 3 bits.
        nov is the value-space bit-count, or number-of-variables
        this vk can be a splited version from a origin vk
        the origin field refs to that (3-bits vk)
        '''
    # nov not used - remove it?

    def __init__(self, kname, dic, nov, origin=None):
        self.kname = kname    # this vk can be a partial one: len(bits) < 3)
        self.origin = origin  # ref to original vk (with 3 bits)
        self.dic = dic  # { 7:1, 3: 0, 0: 1}, or {3:0, 1:1} or {3:1}
        self.nov = nov  # number of variables (here: 8) - bits of value space
        # all bits, in descending order
        self.bits = sorted(list(dic.keys()), reverse=True)  # [7,3,0]
        # void bits of the nov-bits
        bs = list(range(nov))  # all bits 0..nov in ascending order
        # nbits are in ascending order.
        self.nbits = [b for b in bs if b not in self.bits]  # [1,2,4,5,6]
        self.nob = len(self.bits)             # 1, 2 or 3
        self.set_value_and_mask()
        self.completion = 3  # can be: p1 (1 from 3), or p2 (2 of 3)

    def set_completion(self, cmpl):
        self.completion = cmpl

    def modify_keybit(self, old_bit, new_bit):
        if old_bit in self.bits:
            v = self.dic.pop(old_bit)
            self.dic[new_bit] = v
            self.bits = sorted(list(dic.keys()), reverse=True)  # [7,3,0]

    def value_overshadow(self, vkx):
        ''' if self.dic has less bits than vkx's bits, and the vkx sits
            on every bit of self.dic with the same values, then, vkx
            is over-shadowed by self - all values covered by vkx, is already
            covered by this(self) vk.
            This is not possible if vkx has more bits than this vk.
            '''
        result = len(set(self.bits) - set(vkx.bits)) == 0
        for b in self.bits:
            result = result and vkx.dic[b] == self.dic[b]
        return result

    def clone(self, bits2b_dropped=None):
        # bits2b_dropped: list of bits to be dropped.
        # They must be the top-bits
        dic = self.dic.copy()
        new_nov = self.nov
        if bits2b_dropped and len(bits2b_dropped) > 0:
            new_nov = self.nov - len(bits2b_dropped)
            for b in bits2b_dropped:
                # drop off this bit from dic.
                # None: in case b not in dic, it will not cause key-error
                dic.pop(b, None)
        return VKlause(self.kname, dic, new_nov)

    def set_value_and_mask(self):
        ''' For the example klause { 7:1,  5:0,     2:1      }
                              BITS:   7  6  5  4  3  2  1  0
            the relevant bits:        *     *        *
                        self.mask:  1  0  1  0  0  1  0  0
            surppose v = 135 bin(v):  1  0  0  0  0  1  1  1
            x = v AND mask =        1  0  0  0  0  1  0  0
            bits of v left(rest->0):  ^     ^        ^
                  self.value(132)  :  1  0  0  0  0  1  0  0
            This method set self.mask
            '''
        mask = 0
        value = 0
        for k, v in self.dic.items():
            mask = mask | (1 << k)
            if v == 1:
                value = value | (1 << k)
        self.value = value
        self.mask = mask

    def get_topbits(self):
        # for nov == 8, nob == 3, return [7,6,5]
        # for nov == 12, nob == 2, return [11,10]
        return list(range(self.nov - 1, self.nov - 1 - self.nob, -1))

    def position_value(self):
        ''' regardless v be 0 or 1, set the bit 1
            For I am caring only the position of the bits  '''
        return self.mask

    def hit(self, v):  # hit means here: v let this klause turn False
        if type(v) == type(1):
            fv = self.mask & v
            return not bool(self.value ^ fv)
        elif type(v) == type([]):  # sat-list of [(b,v),...]
            # if self.kname == 'C004':
            #     x = 1
            lst = [(k, v) for k, v in self.dic.items()]
            in_v = True
            for p in lst:
                # one pair/p not in v will make in_v False
                in_v = in_v and (p in v)
            # in_v==True:  every pair in dic is in v
            # in_v==False: at least one p not in v
            return in_v

    def hit_valuelist(self):
        hits = []
        nbs = sorted(self.nbits, reverse=True)
        L = len(nbs)
        for x in range(2**L):
            d = {}
            for i in range(L):
                d[nbs[i]] = get_bit(x, i)
            hits.append(set_bits(self.value, d))
        return hits


def hit_values():
    d = {5: 1, 3: 0, 2: 1}
    vk = VKlause('name', d, 6)
    hits = vk.hit_valuelist()


def test_hit_valuelist():
    dics = [
        {2: 0, 1: 0, 0: 0},  # hvs: [0]
        {2: 1, 1: 0, 0: 0},  # hvs: [4]
        {2: 0, 1: 1, 0: 0},  # hvs: [2]
        {2: 0, 1: 1, 0: 1},  # hvs: [3]
        {2: 0, 1: 0},       # hvs: [0,1]
        {2: 1, 1: 0},       # hvs: [4,5]
        {2: 1, 1: 1},       # hvs: [6,7]
        {2: 0, 1: 1},       # hvs: [2,3]
        {2: 0},   # hvs: [1,2,3,4]
        {2: 1},   # hvs: [4,5,6,7]
        {1: 0},   # hvs: [1,3,5,7]
        {1: 1},   # hvs: [1,3,5,7]
        {0: 0},   # hvs: [1,3,5,7]
        {0: 1}    # hvs: [1,3,5,7]
    ]
    for dic in dics:
        vk = VKlause('test-vk', dic, 3)
        hvs = vk.hit_valuelist()
        dic_str = str(dic)
        hvs_str = str(hvs)
        print(f'dic: {dic_str}: {hvs_str}')
        x = 1
# ------- end of def test_hit_valuelist():


if __name__ == '__main__':
    # test_hit_valuelist()
    hit_values()
