import sys
from basics import get_sdic
from bitdic import BitDic, make_vkdic
from workbuffer import WorkBuffer
from satholder import SatHolder, Sat

LAYERS = []  # [{'r': {0: bitdic}}]
Root_bitdic = None


def make_bitdic(bitdic_name, cnf_fname):
    sdic = get_sdic(cnf_fname)
    vkdic = make_vkdic(sdic['kdic'], sdic['nov'])
    bitdic = BitDic(bitdic_name, vkdic, sdic['nov'])
    return bitdic


def verify_sats(sat, bitdic):
    return sat.verify(bitdic)


def verify_satfile(sat_filename):
    cnf_fname = sat_filename.split('.')[0] + '.json'
    bitdic = make_bitdic('r', cnf_fname)
    sat_dic = eval(open('verify/' + sat_filename).read())
    sat = Sat(sat_dic['end-node-name'], sat_dic['sats'])
    return sat.verify(bitdic.vkdic)


def process(cnfname):
    global Root_bitdic
    # sdic = get_sdic(cnfname)
    wb = WorkBuffer(LAYERS)
    keyname = 'r'
    Root_bitdic = make_bitdic(keyname, cnfname)
    # Root_bitdic = make_bitdic(sdic, keyname)

    satslots = list(range(Root_bitdic.nov))
    sh = SatHolder(satslots)
    Sat.nov = Root_bitdic.nov

    # make root work-buffer work-item, addi it to wb
    witem = (keyname, Root_bitdic, sh)
    wb.add_item(witem)

    while not wb.empty():
        wb = wb.work_thru()
        if type(wb).__name__ == 'Sat':
            return wb
    return None
    x = 1   # debug stop


if __name__ == '__main__':
    # configfilename = 'config20_80.json'
    configfilename = 'config1.json'
    # configfilename = 'config1.sat'

    if len(sys.argv) > 1:
        configfilename = sys.argv[1].strip()

    if configfilename.endswith('.sat'):
        result = verify_satfile(configfilename)
        if result:
            print(f'Verified.')
        else:
            print('Not verified')

    elif configfilename.endswith('.json'):
        sat = process(configfilename)
        if sat:
            result = sat.verify(Root_bitdic.vkdic)
            if result:
                fname = configfilename.split('.')[0] + '.sat'
                print(f'Found sat and verified. Save in {fname}')
                sat.save2file(f'verify/{fname}')
            else:
                print('No sat found')

    x = 1
