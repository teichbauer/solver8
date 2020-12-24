from basics import *
from vklause import VKlause
from TransKlauseEngine import TxEngine


def make_vkdic(kdic, nov):
    vkdic = {}
    for kn, klause in kdic.items():
        vkdic[kn] = VKlause(kn, klause, nov)
    return vkdic


class BitDic:
    ''' maintain a bit-dict:
        self.dic: { 7:[C1,C6], -- 7-th bit, these Clauses have bit-7
                    6:[],      -- 6-th bit, these Clauses have bit-6, ... }
        '''

    def __init__(self, name, vkdic, nov):   # O(m)
        self.name = name
        self.nov = nov
        self.dic = {}            # keyed by bits {<bit>: [kns,..]}
        self.vkdic = vkdic
        self.parent = None       # the parent that generated / tx-to self
        self.done = False
        # 3 list of vk-names
        self.ordered_vkdic = {1: [], 2: [], 3: []}
        for i in range(nov):     # number_of_variables from config
            self.dic[i] = []
        self.add_vklause()
    # ==== end of def __init__(..)

    def minlength(self):
        if len(self.ordered_vkdic[1]) > 0:
            return 1
        if len(self.ordered_vkdic[2]) > 0:
            return 2
        if len(self.ordered_vkdic[3]) > 0:
            return 3

    def vk1_totality(self, kn1s):  # vkdic1: a vkdic with all 1-bit vks
        for ind, kn in enumerate(kn1s):
            bit = self.vkdic[kn].bits[0]
            # loop thru the rest of kns(k), compare kn and k
            # if both sit on the same bit(bit == b), and values are opposite
            # then return this pair -> this ch is done:
            # remove this child-branch, add it to self.hitdic
            if ind < (len(kn1s) - 1):
                for k in kn1s[ind+1:]:
                    b = self.vkdic[k].bits[0]
                    if bit == b and \
                            self.vkdic[kn].dic[bit] != self.vkdic[k].dic[b]:
                        return [kn, k]
        return None  # no pair of total cover

    def get_choice(self, nob, candikns):
        # choice: ([<list of kns of total share>],[<list of touched kns>])
        # a total share kn(of vk)/tsvk: vk shared all its bits with the others
        # a touched kn(of vk)/tcvk vk that share at least 1 bit with tsvk
        # return the best: longest tsvk/tcvk
        best_choice = None
        max_tsleng = -1
        max_tcleng = -1
        for kn in candikns:
            vk = self.vkdic[kn]
            # <nob>-many sets. each has kns sharing 1 bit of vk
            # {<bit>:<set of kns sharing this bit>,..}
            sh_sets = {}
            for b in vk.bits:
                sh_sets[b] = set(self.dic[b])
            # pop a value of sh_sets: a set of kns
            if len(sh_sets) == 0:
                raise Exception("444")

            tsvk = set(sh_sets.popitem()[1])
            tcvk = tsvk.copy()
            for s in sh_sets.values():
                tsvk = tsvk.intersection(s)
                tcvk = tcvk.union(s)

            # all kn in tsvk with diff nob: remove it from tsvk
            if nob < 3:
                tmp = tsvk.copy()
                for k in tmp:
                    if self.vkdic[k].nob != nob:
                        tsvk.remove(k)

            # ( {<share-all>}, {<share-any>} )
            # {<share-all>}: set of kname: vk shares all kn's bits
            #      all vk in here must have <nob> bits
            # {<share-any>}: knames of vk sharing at least 1 bit with kn
            #       it is super-set of tsvk
            chc = (tsvk, tcvk)
            ltsvk = len(tsvk)
            if ltsvk < max_tsleng:
                continue
            ltcvk = len(tcvk)
            # insert into choices list: bigger front
            # if equal: dont insert
            # 1: find index of insertion
            if not best_choice:
                best_choice = chc
                max_tsleng = ltsvk
                max_tcleng = ltcvk
            else:
                if best_choice[0] == tsvk:
                    continue
                # see if to replace the best_choice?
                replace = False
                if max_tsleng < ltsvk:
                    replace = True
                elif max_tsleng == ltsvk:
                    if max_tcleng < ltcvk:
                        replace = True
                if replace:
                    best_choice = chc
                    max_tsleng = ltsvk
                    max_tcleng = ltcvk
        return best_choice
    # end of def get_choice(self, nob, candikns):

    def best_choice(self):
        # find which kn touchs the most other kns
        touchdic = {}    # {<cnt>:[kn,kn,..], <cnt>:[...]}
        candidates = {}  # {<kn>:set([kn-touched]),..}
        allknset = set(self.vkdic.keys())

        shortest_bitcnt = self.minlength()
        choices = self.ordered_vkdic[shortest_bitcnt]
        if shortest_bitcnt == 1:
            totality = self.vk1_totality(choices)
            if totality:
                return None, None, None, None

        choice = self.get_choice(shortest_bitcnt, choices)

        kns, touch_set = choice
        notouch_set = allknset - touch_set
        touch_set = touch_set - kns
        return kns, touch_set, notouch_set, shortest_bitcnt
    # end of def best_choice(self):

    def subvkd(self, bitcnt):  # bitcnt: 1,2 or 3
        # return a vkdic that contains vks with bitcnt many bits
        vkd = {}
        for kn in self.ordered_vkdic[bitcnt]:
            vkd[kn] = self.vkdic[kn]
        return vkd

    def add_vk(self, vkn):
        vk = self.vkdic[vkn]
        # assert(vk.nob > 0), f'{vk.kname} has no bit'
        if vk.bits == []:
            raise Exception("333")

        if vkn not in self.ordered_vkdic[vk.nob]:
            self.ordered_vkdic[vk.nob].append(vk.kname)
        for bit in vk.dic:
            if vkn not in self.dic[bit]:
                self.dic[bit].append(vkn)
        return vk
    # ---- end of def add_vk(self, vkn):

    def add_vklause(self, vk=None):  # add vklause vk into bit-dict
        if vk:
            return self.add_vk(vk)
        else:
            for vkn in self.vkdic:
                self.add_vk(vkn)
            return self
    # ==== end of def add_vklause(self, vk=None)

    def print_json(self, fname):
        print_json(self.nov, self.vkdic, fname)

    def visualize(self):
        self.vis.output(self)


if __name__ == '__main__':
    sdic = get_sdic('config1.json')
    vkdic = make_vkdic(sdic['kdic'], sdic['nov'])
    root = BitDic('n0', vkdic, sdic['nov'])
    tx = TxEngine('C002', vkdic['C002'], sdic['nov'])
    root1 = tx.trans_bitdic(root)
    root1.print_json('./configs/config1a.json')
    # res, sat, sat0 = tx.test_me(vkdic)
    x = 1
