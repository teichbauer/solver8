from basics import *
from vklause import VKlause
from visualizer import Visualizer
from TransKlauseEngine import TxEngine
from makechoice import make_choice


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
        self.ordered_vkdic = {}  # 3 list of vdics, keyed by number of bits
        for i in range(nov):     # number_of_variables from config
            self.dic[i] = []
        self.add_vklause()
        self.vis = Visualizer(self.vkdic, self.nov)
    # ==== end of def __init__(..)

    def getbest_choice(self):
        # 1.
        # make sharebit-dic for every kn: {<kname>:{cnt-dic},...}, where each
        # cnt-dic: <kname>:{knx: 1, kny:2, knz:3,..}, meaning that the
        # vk(kname) shares 1-bit with knx, shared 2-bits with kny,
        # 3 bits with knz. if <sharebit-dic> is empty, vk(kname) has no other
        # vk that share a bit with it.
        # if bitdic has 2-bit or 1-bit vk(s) in ordered_vkdic, kname is from
        # the shortest vk-set: ordered_vkdic[1] or [2], otherwise from [3]
        # 2.
        # let makechoice pick the best among them. Return that pick.
        # -------------------------------
        sharebit_dic = {}
        shortest_bitcnt = min(list(self.ordered_vkdic.keys()))
        kns = self.ordered_vkdic[shortest_bitcnt]
        # loop thru all bits in self.dic (total: nov-bits) hi-bit -> lo-bit
        for bit in reversed(list(self.dic.keys())):
            # collect all knames that have this bit
            lst = self.dic[bit][:]
            for kn in lst:
                if kn in kns:  # only pick kn from shortest-vk's kns
                    kdic = sharebit_dic.setdefault(kn, {})
                    for knx in lst:
                        if knx != kn:
                            if knx in kdic:
                                kdic[knx] += 1
                            else:
                                kdic[knx] = 1
        # use the sharebit-dic to make the best choice. choice is a dict
        # its structure depends on shortest_bitcnt: 1,2 or 3 see makechoice.py
        kns = self.most_touched()
        self.choice = make_choice(sharebit_dic, self.vkdic, shortest_bitcnt)
        return self.choice
    # ==== end of def most_popular(self, d)

    def best_choice(self):
        # find which kn touchs the most other kns
        touchdic = {}    # {<cnt>:[kn,kn,..], <cnt>:[...]}
        candidates = {}  # {<kn>:set([kn-touched]),..}
        allknset = set(self.vkdic.keys())
        for kn, vk in self.vkdic.items():
            s = set([])
            for b in vk.bits:
                s = s.union(set(self.dic[b]))
            candidates[kn] = s
        for kn, s in candidates.items():
            touchdic.setdefault(len(s), []).append(kn)
        bestkey = max(touchdic.keys())
        kn = touchdic[bestkey][0]
        touch_set = candidates[kn]
        notouch_set = allknset - touch_set
        touch_set.remove(kn)
        return kn, touch_set, notouch_set

    def subvkd(self, bitcnt):  # bitcnt: 1,2 or 3
        # return a vkdic that contains vks with bitcnt many bits
        vkd = {}
        for kn in self.ordered_vkdic[bitcnt]:
            vkd[kn] = self.vkdic[kn]
        return vkd

    def add_vklause(self, vk=None):  # add vklause vk into bit-dict

        def add_vk(self, vkn):
            vclause = self.vkdic[vkn]
            length = len(vclause.dic)
            lst = self.ordered_vkdic.setdefault(length, [])
            if vkn not in lst:
                lst.append(vclause.kname)
            for bit in vclause.dic:
                if vkn not in self.dic[bit]:
                    self.dic[bit].append(vkn)
            return vclause
        # ---- end of def add_vk(self, vkn):

        if vk:
            return add_vk(self, vk)
        else:
            for vkn in self.vkdic:
                add_vk(self, vkn)
            return self
    # ==== end of def add_vklause(self, vk=None)

    def transfer(self, vkname):
        if type(vkname) == type(''):
            tx = TxEngine(vkname+'-1', self.vkdic[vkname], self.nov)
        else:
            tx = vkname
        nvkdic = tx.trans_vkdic(self.vkdic)
        return BitDic('new-bitdic', nvkdic, self.nov)

    def print_json(self, fname):
        print_json(self.nov, self.vkdic, fname)

    def visualize(self):
        self.vis.output(self)


if __name__ == '__main__':
    sdic = get_sdic('config1.json')
    vkdic = make_vkdic(sdic['kdic'], sdic['nov'])
    root = BitDic('n0', vkdic, sdic['nov'])
    tx = TxEngine('C002', vkdic['C002'], sdic['nov'])
    root1 = root.transfer(tx)
    root1.print_json('./configs/config1a.json')
    # res, sat, sat0 = tx.test_me(vkdic)
    x = 1
