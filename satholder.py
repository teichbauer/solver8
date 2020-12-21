from basics import get_bit, get_sdic, set_bits
from datetime import datetime


class Sat:
    def __init__(self, end_node_name, pairs):
        pairs.sort(reverse=True)  # for vk.bits is reverse-sorted
        self.pairs = pairs
        self.end_node_name = end_node_name
        self.cnf_file = ''
        self.save_dir = 'verify'

    def get_intv(self):
        d = {}
        for p in self.pairs:
            d[p[0]] = p[1]
        v = set_bits(0, d)
        return v

    def verify(self, root_bitdic, sats=None):
        if not sats:
            sats = self.pairs
        if not sats:  # if there is no pair, return True
            return True
        hit = False
        for kn, vk in root_bitdic.vkdic.items():
            assert(root_bitdic.nov > vk.bits[0])
            hit = vk.hit(self.pairs)
            if hit:  # when hit, it contains a tuple, otherwise it is False
                print(f'{kn} hits')
                return False, None
        v = self.get_intv()
        return True, v

    def save(self, fname=None):
        now = datetime.now()
        timestamp = now.isoformat()
        if not fname:
            fname = self.save_dir + '/' + self.cnf_file.split('.')[0] + '.sat'
        nov = len(self.pairs)
        intv = self.get_intv()
        with open(fname, 'w') as ofile:
            ofile.write(f'# {timestamp}\n')
            ofile.write('{\n')
            ofile.write(f'    "configure-name": "{self.cnf_file}",\n')
            ofile.write(f'    "end-node-name": "{self.end_node_name}",\n')
            ofile.write(f'    "number-of-variables": "{nov}",\n')
            ofile.write(f'    "sats": [\n')
            for sat_tuple in self.pairs:
                m = str(sat_tuple)
                ofile.write(f'        {m},\n')
            ofile.write('    ],\n')
            ofile.write(f'    "integer": {intv}\n')
            ofile.write('}')


class SatHolder:
    ''' Manages original variable names. Originally: [0,1,2,..<nov-1>]
        Instance owned by every branch as .sh. At the very beginning, 
        br0.sh's array is nov long. br0 has 3 bit-cut, and has 
        a tx :[(4,7,(2,6),(1,5),...]. br0.sh will call transfer(br0.tx), 
        then cut its tail([0,1,...<nov-4>]) for giving it to br0's every child. 
        Afterwards, br0.sh only keeps 3 [4,2,1]
        when br0 has children[1], children[5] (1,5 are sat-values for them),
        the part of sats for this 3-bit will be
        <sat0-1>: {4:0, 2:0, 1:0}  reflecting sat-value 001(1), and
        <sat0-5>: {4:1, 2:0, 1:1}  reflecting sat-value 101(5)
        if eventually r1 gets its sats (of length nov - 3), the total sats-set
        will then include this <sat0-1>, to have complete sats-set.
        This process is true for every child down the tree. So each br-m is done
        it will have a sh of length 1,2 or max:3, containing the variable-names
        for its 1,3 or 7 (2-1, 4-1,8-1) sat-values, and be one part of the
        whole sat-set (chain)
        '''

    def __init__(self, varray):
        self.varray = varray

    def spawn_tail(self, cutcnt):
        return self.varray[:-cutcnt]

    def transfer(self, txe):
        self.varray = txe.trans_varray(self.varray)

    def cut_tail(self, cutcnt):
        self.varray = self.varray[-cutcnt:]

    def get_segment_sats(self, chil_keyvalue):
        ''' assert check: 
               varray length can be 1, 2 or 3, where sat-value can be:
               (0,1), (0,1,2,3) or (0,1,2,3,4,5,6,7)
            operational example: 
                varray: [231, 8]: names of two variables,
                varray[0] == 231, varray[1] == 8
                And sat chil_keyvalue: 2 == bin( 10 )
                output: 
            return value is a list of tuples, as like:
                [(231,0), (8,1)]:
                variable-231 has boolean chil_keyvalue 0
                variable-8   has boolean chil_keyvalue 1
            '''
        assert(chil_keyvalue < (2 ** len(self.varray)))
        lst = []
        for ind, v in enumerate(self.varray):
            # every bit in varray represent a variable(original name)
            lst.append((v, get_bit(chil_keyvalue, ind)))
        return lst
