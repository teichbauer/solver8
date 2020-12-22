from basics import topbits_coverages, get_bit, print_json
from TransKlauseEngine import TxEngine
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
            sats = list(range(2 ** bitdic.nov))
            sat = sats[0]
            # only return single sat from sats
            self.sats = self.sh.get_segment_sats(sat)
        elif bitdic.nov == 3:
            self.nov3()
        else:
            # kn, knset, notouchset = self.init_bitdic.best_choice()
            kns, touchset, notouchset, nob = self.init_bitdic.best_choice()
            if not kns:  # vk1 vks have totality of coverage
                self.name = 'finished'
                del self.parent.children[self.valkey]
                return

            self.topbits = list(
                range(bitdic.nov - 1, bitdic.nov - 1 - nob, -1))
            self.base_vk = self.init_bitdic.vkdic[list(kns)[0]]
            if self.topbits != self.base_vk.bits:
                self.tx = TxEngine(self.name, self.base_vk,
                                   self.init_bitdic.nov)
                self.name += 't'
                self.sh.transfer(self.tx)
                vkdic = self.tx.trans_vkdic(self.init_bitdic.vkdic)
                # print_json(self.init_bitdic.nov, vkdic,
                #            f'verify/{self.name}.json')
            else:
                vkdic = self.init_bitdic.vkdic
            cvrs = []
            for k in kns:
                ran, dummy = topbits_coverages(vkdic[k], self.topbits)
                cvrs.append(ran[0])
            self.spawn(cvrs, touchset, notouchset, vkdic, nob)

    def spawn(self, cvrs, touchset, notouchset, vkdic, cutn):
        new_nov = self.init_bitdic.nov - cutn
        for ind in range(2 ** cutn):
            if ind in cvrs:
                continue
            vkd = {}
            total_coverage = False
            for kn in notouchset:  # no-touches are in each child-bitdic
                vkd[kn] = vkdic[kn].clone(self.topbits)
            out1s = []       # save all leng==1 outdics, for block check
            blocked = False  # blocked:2 in out1s on the same bit, with 0 and 1
            for kn in touchset:
                vrng, outdic = topbits_coverages(vkdic[kn], self.topbits)
                if ind in vrng:
                    # save lengt==1 outdic in out1s list
                    # if any 2 outdics have the same key(bit) and
                    # opposite value: then this ind is blocked: no child
                    care = (outdic not in out1s) and (len(outdic) == 1)
                    if care:
                        for d in out1s:
                            if d.keys() == outdic.keys():
                                if d.values() != outdic.values():
                                    blocked = True
                                    break
                        out1s.append(outdic)
                    if blocked:
                        self.children.pop(ind, None)
                        break
                    else:
                        vkd[kn] = vkdic[kn].clone(self.topbits)
            if not blocked:
                self.children[ind] = (
                    BitDic(f'{self.name}{ind}', vkd, new_nov),
                    self.sh.spawn_tail(cutn)
                )

        self.sh.cut_tail(cutn)
        if len(self.children) == 0:
            self.name = 'finished'
            del self.parent.children[self.valkey]

    def nov3(self):
        vset = set(range(8))
        hitset = set([])
        for kn, vk in self.init_bitdic.vkdic.items():
            ran, out = topbits_coverages(vk, [2, 1, 0])
            vset = vset - set(ran)
        if len(vset) > 0:
            s = vset.pop()  # take first sat
            self.sats = self.sh.get_segment_sats(s)

    def get_parent_sats(self):
        lst = []
        p = self.parent
        while type(p).__name__ == Branch:
            lst += p.sh.get_segment_sats(p.valkey)
            p = p.parent
