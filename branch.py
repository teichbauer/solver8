from basics import get_bit, drop_bits, print_json
from TransKlauseEngine import TxEngine
from makechoice import topbits_coverages
from bitdic import BitDic
from satholder import SatHolder


class Branch:
    def __init__(self, bitdic,  # starting bitdic
                 depth,         # depth in node-dic/search tree
                 val_key,       # value-index from parent children-keys
                 parent,        # parent-branch, if depth==0, root-bitdic)
                 satholder):    # sat slot-holder
        self.depth = depth
        self.name = bitdic.name
        self.valkey = val_key
        self.parent = parent
        self.init_bitdic = bitdic
        self.tx = None
        self.children = {}
        self.sh = satholder
        self.sats = None
        if len(bitdic.vkdic) == 0:
            # no vk exists: all values in the range are sats
            self.sats = list(range(2 ** bitdic.nov))
        elif bitdic.nov == 3:
            self.nov3()
        else:
            kn, knset, notouchset = self.init_bitdic.best_choice()
            self.base_vk = self.init_bitdic.vkdic[kn]
            if self.base_vk.get_topbits() != self.base_vk.bits:
                self.tx = TxEngine(self.name, self.base_vk,
                                   self.init_bitdic.nov)
                self.name += 't'
                self.sh.transfer(self.tx)
                vkdic = self.tx.trans_vkdic(self.init_bitdic.vkdic)
                print_json(self.init_bitdic.nov, vkdic,
                           f'verify/{self.name}.json')
            else:
                vkdic = self.init_bitdic.vkdic
            self.topbits = vkdic[self.base_vk.kname].get_topbits()
            self.spawn(knset, notouchset, vkdic)

    def spawn(self, knset, notouchset, vkdic):
        covers, dum = topbits_coverages(
            vkdic[self.base_vk.kname], self.topbits)
        self.hitvalue = covers[0]
        cutn = len(self.topbits)
        new_nov = self.init_bitdic.nov - cutn
        for ind in range(2 ** cutn):
            if ind == self.hitvalue:
                continue
            vkd = {}
            total_coverage = False
            for kn in notouchset:  # no-touches are in each child-bitdic
                vkd[kn] = vkdic[kn].clone(self.topbits)
            for kn in knset:
                vrng, outdic = topbits_coverages(vkdic[kn], self.topbits)
                if ind in vrng:         # if len(vrng)==1 and ind == vrng[0]
                    if len(vrng) == 1:  # then this kn covers all child-values
                        total_coverage = True
                    else:
                        # > 1: partially covered: into child
                        # vkd[kn].dic must be the same as outdic
                        vkd[kn] = vkdic[kn].clone(self.topbits)
            if not total_coverage:
                self.children[ind] = (
                    BitDic(f'{self.name}{ind}', vkd, new_nov),
                    self.sh.spawn_tail(cutn)
                )
        self.sh.cut_tail(cutn)
        if len(self.children) == 0:
            del self.parent.children[self.valkey]

    def nov3(self):
        vset = set(range(8))
        hitset = set([])
        for kn, vk in self.init_bitdic.vkdic.items():
            for v in range(8):
                if vk.hit(v):
                    hitset.add(v)
        sats = vset - hitset
        if len(sats) > 0:
            s = sats.pop()  # take first sat
            self.sats = self.sh.get_segment_sats(s)

    def get_parent_sats(self):
        lst = []
        p = self.parent
        while type(p).__name__ == Branch:
            lst += p.sh.get_segment_sats(p.valkey)
            p = p.parent
