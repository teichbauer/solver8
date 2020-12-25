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
    def __init__(self):
        self.buffer = []

    def lindex(self):
        return len(Branch.LAYERS) - 1

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

    def crunch_item(self, item):  # witem: (<key-name>, <bitdic>, <satholder>)

        nitems = []  # collect items of next layer
        # make branch ->br, on current layer. When being constructed
        # br will spawn off its children, put into nitems, return it
        br = Branch(item['bitdic'],
                    item['depth'],   # level index
                    item['index'],
                    item['valkey'],  # val-index from  parent-br
                    item['parent'],  # parent-branch
                    item['sh'])       # satholder
        if br.sats:
            print(f'Found sat on {br.name}')
            sat = self.build_sats(br)
            return sat

        if len(br.children) > 0:
            Branch.LAYERS[-1][br.name] = br

            # loop thru self.children = {<val>:<childic>,...}
            for childic in br.children.values():  # children:{<v>:<child-dic>}
                nitems.append(childic)
        else:
            x = 1
        return nitems

    def work_thru(self):
        items = []  # for to hold next layer's wb-items being made
        Branch.LAYERS.append({})
        while True:
            work_item = self.pop_item()
            if work_item:
                new_items = self.crunch_item(work_item)
                if type(new_items).__name__ == 'Sat':
                    return new_items
                else:
                    items += new_items
            else:
                # all work-items from self.buffer done
                self.buffer = items  # assign new work-items
                for index, item in enumerate(self.buffer):
                    item['index'] = index  # adding index to each

                level = len(Branch.LAYERS)
                # debugging purpose
                # debug = True
                debug = False
                if debug:
                    if level > 1:
                        last_br_count = len(Branch.LAYERS[level - 1])
                        print(f'layer[{level -1}] has {last_br_count}')
                    print(f'level {level} has {len(self.buffer)} items\n')

                return self
