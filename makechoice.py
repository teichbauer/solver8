from vklause import VKlause, get_bit


def find_321grps(sharebit_dic, vkdic):
    choice32 = {  # return value
        3: {},  # { <tuple of kns sharing 3 bits>: {g2:[], g1:[],g0:[]}, ..}
        2: {},  # { <kn2>: {g2:[], g1:[], g0:[]}, <kn2>:{..},..}
        1: {},  # { <kn1>:{g1:[],g0:[]}, <kn1>: {},...}
        0: []}  # list of kns sharing no bit with any others
    allkns = set(vkdic.keys())
    for k, d in sharebit_dic.items():
        if len(d) == 0:
            choice32[0].append(k)
            continue
        g3 = []  # kns sharing 3 bits with k
        g2 = []  # kns sharing 2 bits with k
        g1 = []  # kns sharing 1 bits with k
        for kx, cnt in d.items():
            if cnt == 3:
                # collect the kname kx with 3 overlapping bits
                g3.append(kx)
            elif cnt == 2:
                # collect the kname kx with 2 overlapping bits
                g2.append(kx)
            elif cnt == 1:
                g1.append(kx)
        if len(g3) > 0:
            # make a dict keyed by a tuple of kns sharing 3 bits
            # value: a dict with 2 keys:
            #  g2:[list of kns sharing 2 bits with k]
            #  g1:[list of kns sharing 1 bits with k]
            g3.insert(0, k)
            k3 = tuple(sorted(g3))
            if k3 in choice32[3]:
                continue
            # choice now has an entry, keyed by k
            # with ['g3'] = g3 as the first k-v pair, where v is g3 list
            choice32[3][k3] = {}
            s0 = allkns - set(g3)
            if len(g2) > 0:
                choice32[3][k3]['g2'] = g2
                s0 = s0 - set(g2)
                g2 = []
            if len(g1) > 0:
                choice32[3][k3]['g1'] = g1
                s0 = s0 - set(g1)
                g1 = []
            choice32[3][k3]['g0'] = list(s0)
        elif len(g2) > 0:
            s0 = allkns - set(g2)
            # make a dict keyed by k. value is a dict: {g2:[], g1:[], g0:[]}
            choice32[2].setdefault(k, {})['g2'] = g2
            if len(g1) > 0:
                choice32[2][k]['g1'] = g1
                s0 = s0 - set(g1)
                g1 = []
            choice32[2][k]['g0'] = list(s0)
        elif len(g1) > 0:
            # make a dict keyed by k. value is a dict: {g1:[], g0:[]}
            choice32[1].setdefault(k, {})['g1'] = g1
            s0 = allkns - set(g1)
            s0.remove(k)
            choice32[1][k]['g0'] = list(s0)

    return choice32


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


def pseudo_value(vk, vkp=None):
    ''' inputs: vk.dic == {7:1, 5:1, 2:0}, vkp==None -> return 6 / 110
        inputs: vk.dic == {7:1, 5:1, 2:0}, vkp.dic=={7:1, 2:1}
        -> return (5, 7) / (101, 111) - middle bit-5: 0,1 generate 101/111
        '''
    bs = vk.bits    # 3 bit-positions: [high-bit,middle-bit,low-bit]
    if vkp == None:
        vkv = vk.dic[bs[0]] << 2 | vk.dic[bs[1]] << 1 | vk.dic[bs[2]]
        return vkv
    else:
        xbs = bs[:]     # taking away bits of vkp from this
        vk2d = {}       # make a 2 bits dict from vkp - dump bit not in vk
        res = []
        for b in vkp.dic:  # xbs will have 1 bit left
            if b in bs:
                xbs.remove(b)
                vk2d[b] = vkp.dic[b]
        # set mis-bit to have 0, -> d0
        d0 = vk2d.copy()
        d0[xbs[0]] = 0
        vk0 = VKlause('0', d0, vk.nov)
        v0 = pseudo_value(vk0)
        res.append(v0)

        # set mis-bit to have 1, -> d1
        d1 = vk2d.copy()
        d1[xbs[0]] = 1
        vk1 = VKlause('0', d1, vk.nov)
        v1 = pseudo_value(vk1)
        res.append(v1)

        return res


def evaluate_3grp(g3, g2, vkdic):

    def g2outerbit(bits, vk, vkdic):
        ''' if bits = [7,5,1], vk.dic:{7:0, 5:1, 1:1}
            return (5,1)
            '''
        d = vk.dic.copy()
        for b in bits:
            if b in d:
                del d[b]
        return tuple(d.items())[0]

    cnt = {}   # how many number in (0..7) are covered
    for c in g3:    # collect coverage from g3
        cnt.setdefault(pseudo_value(vkdic[c]), set([])).add(c)

    # count from g2
    vk = vkdic[g3[0]]   # take 3-bit positions from any of g3(herefrom 0-th)

    g2dic = {}
    for kn in g2:
        # get the 2 values vkdic[c]'s 2 bits, outside bit=0|1
        vs = pseudo_value(vk, vkdic[kn])
        # value(s) from vs that are/is new to cnt
        nvs = set(vs) - set(cnt.keys())
        # get outside bit/value pair
        pair = g2outerbit(vk.bits, vkdic[kn], vkdic)
        # save (<g2-value-set>   [0]-> this g2 covers these 2 vlues in top-bits
        #       <new-values-set>,[1]-> from [0], the value new to g3-values/cnt
        # <outside-bit/value-pair>[2]-> the 1 bit this g2 has outside of g3
        # )
        # under kn in g2dic
        g2dic[kn] = (vs, nvs, pair)

    # for kn in g2:
    for i in range(len(g2) - 1):    # loop thru g2, without last
        kn = g2[i]                  # collect 2 values, this g2, sitting on
        if kn in g2dic:
            for j in range(i+1, len(g2)):  # loop from kn's next to the last
                km = g2[j]
                # when
                # a: km does have new value(s) to cnt, and
                # b: it has the same value-set as kn did
                # c: its outside-bit sits on the same position as kn does, and
                # d: its outside bit-value is oppsite to that of kn's, then
                # those new value(s) will be added to cnt
                if km in g2dic:                                     # a
                    if g2dic[kn][0] == g2dic[km][0]:                # b
                        if g2dic[km][2][0] == g2dic[kn][2][0]:      # c
                            if g2dic[km][2][1] != g2dic[kn][2][1]:  # d
                                for x in g2dic[km][1]:
                                    cnt.setdefault(x, set([])).add(km)
                                    cnt[x].add(kn)
    return cnt, g2dic


def best_vk3(dic321, vkdic):
    dic = {}
    for ks, d in dic321[3].items():
        s, g2dic = evaluate_3grp(ks, d['g2'], vkdic)
        dic.setdefault(
            len(s),              # dic keyed by number of hit-values
            []).append({         # list of dics, each as the following defs:
                'base-kns': ks,  # kns sitting on the 3 bits
                'value-dic': s,  # {<hit-value>:<set of kns covering value>,..}
                'g2dic': g2dic,  # {<g2-kn>: }
                'g1': d['g1'],   # kns that share 1 bit within the 3 bits
                'g0': d['g0']    # kns sharing no bit in 3 bits
            })
    # pick the best candidate
    maxn = max(list(dic.keys()))
    if len(dic[maxn]) == 1:
        return dic[maxn][0]
    else:
        m = dic[maxn][0]
        for d in dic[maxn][1:]:
            # cretarium-1: most cover-value
            if len(d['base-kns']) > len(m['base-kns']):
                m = d
            elif len(d['base-kns']) == len(m['base-kns']):
                # cretarium-2: most g2s
                if len(d['g2dic']) > len(m['g2dic']):
                    m = d
        return m


def best_vk2(dic321, vkdic):
    raise Exception("best-vk2 not implemented yet")
    return None


def best_vk1(dic321, vkdic):
    dic = {}
    kn1s = list(dic321[1].keys())
    if len(kn1s) == 0:       # no g1 exists, only g0(s)
        g0kn = dic321[0][0]  # first g0-kn as choice
        vk0 = vkdic[g0kn]
        return {
            'base-kns': [g0kn],
            'value-dic': vk0.dic[vk0.bits[0]],
            'g1': [],
            'g0': dic321[0]
        }
    for kn in kn1s:
        cvrs = {}
        vk = vkdic[kn]       # vk is a 1-bit vk
        vkbit = vk.bits[0]
        val = vk.dic[vkbit]  # the single bit-value of vk: 0 | 1
        # d: {g1: [], g0:[]}: kns sharing bit, kns not sharing with kv
        d = dic321[1][kn]
        sc = len(d['g1'])  # number of vks sharing 1 bit with vk
        cvrs.setdefault(val, set([])).add(kn)
        for k in kn1s:
            if k != kn and vkdic[k].nob == 1 and vk.bits == vkdic[k].bits:
                if list(vkdic[k].dic.values())[0] == val:
                    cvrs[val].add(k)
        # if a vkx in g1 (sharing vkbit with vk), has that bit value
        # equals vk[bit]/val, then this vkx is coveres by vk
        g1s = []
        for g1 in d['g1']:
            # if vkdic[g1].dic.get(vkbit, -1) == val:
            if vk.value_overshadow(vkdic[g1]):
                cvrs[val].add(g1)
            else:
                g1s.append(g1)  # left over g1 goes to g1s
        dic.setdefault(     # dic is dict of coice-list
            sc,             # keyed by number of vks having 1 bit of vk
            []).append({    # add a choice-dic to the list
                'base-kns': [kn],   # key-vk1 kname
                'value-dic': cvrs,  # cover value 0 or 1, kns keyed by it
                'g1': g1s,  # g1s that aren't covered by vkbit
                'g0': d['g0']   # list of knames not-sharing with vk
            })
    maxn = max(list(dic.keys()))  # biggest sharing kv-count
    picks = dic[maxn]           # list of choices
    pick = picks[0]
    for choice in picks[1:]:  # rest of choices, each: [kn, cvrs, g1, g0]
        # choose the one with longest g1-list/[2]
        if len(choice['g1']) > len(pick['g1']):
            pick = choice
    return pick  # return the choice-dic


def make_choice(sharebit_dic, vkdic, vkbit_cnt):
    # a choice is a list:
    # [(<base-vkname>,..), (<cover-values), g2dic, [g1-list], [g0-list]]
    dic32 = find_321grps(sharebit_dic, vkdic)
    if vkbit_cnt == 3:
        return best_vk3(dic32, vkdic)
    elif vkbit_cnt == 2:
        return best_vk2(dic32, vkdic)
    elif vkbit_cnt == 1:
        return best_vk1(dic32, vkdic)
