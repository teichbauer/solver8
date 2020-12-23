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
        self.txs = {}
        self.setup_tx()

    def setup_tx(self):
        # clone of vk.bits (they are in descending order from VKlause)
        bits = self.start_vklause.bits[:]
        # all bits 0..nov in ascending order.
        # later, the topbits removed, will be nbit's target-bits
        L = len(bits)                           # number of target-bits
        allbits = list(range(self.nov))
        lefts = allbits[:]

        # target/left-most bits(names)
        hi_bits = list(reversed(allbits))[:L]   # target-bits

        # transfer for bits to high-bits
        new_dic = {}
        while len(bits) > 0:
            b = bits.pop(0)
            h = hi_bits.pop(0)
            self.txs[b] = h
            new_dic[h] = self.start_vklause.dic[b]
            allbits.remove(h)  # target-bit consumed/removed
            lefts.remove(b)

        nblen = self.nov - L
        assert(len(allbits) == nblen)
        for i in range(nblen):
            self.txs[lefts[i]] = allbits[i]

        # now tx the start_vklause to be self.vklause
        self.vklause = VKlause(
            self.start_vklause.kname, new_dic, self.nov)
    # ----- end of def setup_tx(self, hi_bits=None)

    def trans_varray(self, varray):
        assert(self.nov == len(varray))
        lst = varray[:]
        for fr, to in self.txs.items():
            lst[to] = varray[fr]
        return lst

    def trans_klause(self, vklause):
        # transfered vk still have the same kname
        tdic = {}
        for b, v in vklause.dic.items():
            tdic[self.txs[b]] = v
        return VKlause(vklause.kname, tdic, self.nov)

    # ----- end of trans_klause

    def trans_vkdic(self, vkdic):
        vdic = {}
        for kn, vk in vkdic.items():
            if kn == self.vklause.kname:
                vdic[kn] = self.vklause.clone()
            else:
                vdic[kn] = self.trans_klause(vk)
        return vdic

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


if __name__ == '__main__':
    x = 1
