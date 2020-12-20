from branch import Branch
from bitdic import print_json
from satholder import SatHolder, Sat

'''
    LAYERS = [<layer-item>,...] where (see log.txt for more info) a layer-item:
    layer-item:
    {
        '<root-key>': { # root-key as in 'r','r1','r12','r501'
            # may have 1, 2, 4, 8 items under value: 0..7
            <val>: 'C0xx' | ('C0x1','C0x2',..),
            <val>: <bitdic> ->(wb.*)-> <branch inst>,
            ...
        },
        'root-key': {
            ...
        }
    }
    --------------------------------------------
    workbuffer.buffer; [<work-item>,...] where an item:
    work-item: (<key-name>, <bitdic>, <satholder)
    '''


class WorkBuffer:
    def __init__(self, layers):
        self.layers = layers
        self.buffer = []

    def lindex(self):
        return len(self.layers) - 1

    def add_item(self, item):
        self.buffer.append(item)
        index = len(self.buffer) - 1
        return index

    def empty(self):
        return len(self.buffer) == 0

    def pop_item(self):
        if not self.empty():
            return self.buffer.pop(0)
        else:
            return None

    def build_sats(self, branch):
        ''' branch has .sats. add segment-sats of all parent-brs till root
            will build the complete sats
            '''
        lst = branch.sats
        p = branch.parent
        valkey = branch.valkey
        while type(p).__name__ == 'Branch':
            plst = p.sh.get_segment_sats(valkey)
            valkey = p.valkey
            for e in plst:
                lst.append(e)
            p = p.parent
        return Sat(branch.name, lst)

    def crunch_item(self, witem):  # witem: (<key-name>, <bitdic>, <satholder>)
        itemkey, bitdic, satholder = witem
        if itemkey == 'r':      # is the very root item?
            valkey = 0
            parent_br = bitdic
        else:
            keylen = len(itemkey)
            # if itemkey == 'r21' -> 'r2', 1
            parent_node_key, valkey = itemkey[:-1], int(itemkey[-1:])
            parent_br = self.layers[self.lindex() - 1][parent_node_key]

        nitems = []  # collect items of next layer-index(lindex())
        # make branch ->br, on current layer. When being constructed
        # br will resolve some vals into its hitdic, and
        # spawn off its children
        br = Branch(bitdic,
                    self.lindex(),  # level index
                    valkey,         # val-index from  parent-br
                    parent_br,      # parent-branch
                    satholder)      # br.sh references satholder
        if br.name != 'finished':
            self.layers[-1][itemkey] = br
            if br.sats:
                print(f'Found sat on {br.name}')
                sat = self.build_sats(br)
                return sat

            # loop thru children-bitdics, key(v) being the values of br
            for v, child in br.children.items():  # child: (bitdic, sh-tail)
                nitems.append((f'{itemkey}{v}', child[0], SatHolder(child[1])))
        return nitems

    def work_thru(self):
        items = []  # for to hold next layer's wb-items being made
        self.layers.append({})
        while True:
            wb_item = self.pop_item()
            if wb_item:
                wb_items = self.crunch_item(wb_item)
                if type(wb_items).__name__ == 'Sat':
                    return wb_items
                else:
                    items += wb_items
            else:
                self.buffer = items
                return self
