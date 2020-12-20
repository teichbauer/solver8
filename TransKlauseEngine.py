from visualizer import Visualizer
from vklause import VKlause
from basics import get_bit, set_bit


class TxEngine:
    """ move base_klause's bits to the left-most top positions, 
        assign the transfered klause to self.klause. 
        While doing this, set up operators so that any 
        klause will be transfered to a new klause compatible to 
        self.klause
        """

    def __init__(self,
                 name,          # (1) name of the tx
                 base_vklause,  # (2) inst of VKlause 2b transfered to lm
                 nov):          # (3) number of bits in value-space
        self.ame = name
        self.start_vklause = base_vklause
        self.nov = nov
        self.txs = []   # list of exchange-tuple(pairs)
        self.setup_tx()

    def setup_tx(self):
        # clone of vk.bits (they are in descending order from VKlause)
        bits = self.start_vklause.bits[:]
        # all bits 0..nov in ascending order.
        # later, the topbits removed, will be nbit's target-bits
        allbits = [b for b in range(self.nov)]

        # target/left-most bits(names)
        L = len(bits)                           # number of target-bits
        hi_bits = list(reversed(allbits))[:L]   # target-bits

        # transfer for bits to high-bits
        new_dic = {}
        while len(bits) > 0:
            b = bits.pop(0)
            h = hi_bits.pop(0)
            self.txs.append((b, h))
            new_dic[h] = self.start_vklause.dic[b]
            allbits.remove(h)  # target-bit consumed/removed

        # setup the transfer-tuples for start_vklause.nbits
        vk = self.start_vklause
        # safty check: vk.nbits are the not-used bits from vk
        # there should be the same many as in allbits, with tops bits removed.
        if len(allbits) != len(vk.nbits):
            assert(False), "bits-length wrong"
        for i in range(len(vk.nbits)):
            self.txs.append((vk.nbits[i], allbits[i]))

        # now tx the start_vklause to be self.vklause
        self.vklause = VKlause(
            self.start_vklause.kname, new_dic, self.nov)
    # ----- end of def setup_tx(self, hi_bits=None)

    def trans_varray(self, varray):
        assert(self.nov == len(varray))
        lst = list(range(self.nov))
        for ts in self.txs:
            lst[ts[1]] = varray[ts[0]]
        return lst

    def trans_klause(self, vklause):
        # transfered vk still have the same kname
        tdic = {}
        for t in self.txs:
            if t[0] in vklause.dic:
                tdic[t[1]] = vklause.dic[t[0]]
        return VKlause(vklause.kname, tdic, self.nov)

    # ----- end of trans_klause

    def trans_value(self, v):
        new_v = v
        for t in self.txs:
            fb, tb = t  # get from-bit, to-bit from t
            bv = get_bit(v, fb)
            new_v = set_bit(new_v, tb, bv)
        return new_v

    def trans_vkdic(self, vkdic):
        vdic = {}
        for kn, vk in vkdic.items():
            if kn == self.vklause.kname:
                vdic[kn] = self.vklause.clone()
            else:
                vdic[kn] = self.trans_klause(vk)
        return vdic

    def reverse_value(self, v):
        # v -> new_v
        new_v = v
        for t in self.txs:
            fb, tb = t  # get from-bit, to-bit from t
            bv = get_bit(v, tb)
            new_v = set_bit(new_v, fb, bv)
        return new_v

    def reverse_values(self, vs):
        res = []
        for v in vs:
            res.append(self.reverse_value(v))
        return res

    def trans_values(self, vs):
        res = []
        for v in vs:
            res.append(self.trans_value(v))
        return res

    def trans_bitdic(self, bitdic):
        new_vkdic = self.trans_vkdic(bitdic.vkdic)
        # turn "19'1" -> "19't"
        name = bitdic.name + '-t'
        # new_bitdic = BitDic(self.name, name, new_vkdic, bitdic.nov)
        new_bitdic = bitdic.__class__(
            name,
            new_vkdic,
            bitdic.nov)
        return new_bitdic

    def output(self):
        msg = self.name + ': '+str(self.start_vklause.dic) + ', '
        msg += 'txn: ' + str(self.txs) + ', '
        msg += '-'*60
        return msg

    def test_me(self, vkdic):
        ''' 1. transfer vkdic -> nvkdic
            2. for v in v-range,
               if v is hit for some clauses cset, then
               tx(v must be hit for tx(cset))
            '''
        nvkdic = self.trans_vkdic(vkdic)

        vdic = {}
        vhit_dic = {}
        sat = []
        sat0 = []
        N = 2 ** self.nov
        for v in range(N):
            nv = self.trans_value(v)
            hit = False
            hit0 = False

            hset0 = set([])
            for kn, vk in vkdic.items():
                if vk.hit(v):
                    hset0.add(kn)
                    hit0 = True
            if not hit0:
                sat0.append(v)

            hset = set([])
            for kn, vk in nvkdic.items():
                if vk.hit(nv):
                    hset.add(kn)
                    hit = True
            if not hit:
                sat.append(nv)

            if hset0 != hset:
                debug = 1
                print(f'Tx test failed on: {v}')
                return False
        return True, sat, sat0


if __name__ == '__main__':
    x = 1
