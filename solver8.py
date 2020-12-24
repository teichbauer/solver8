import sys
import time
from basics import get_sdic
from bitdic import BitDic, make_vkdic
from workbuffer import WorkBuffer
from satholder import SatHolder, Sat

# LAYERS = []
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
    verif, intv = sat.verify(bitdic)
    return verif, intv


def process(cnfname):
    global Root_bitdic
    wb = WorkBuffer()
    keyname = 'r'
    Root_bitdic = make_bitdic(keyname, cnfname)

    satslots = list(range(Root_bitdic.nov))
    sh = SatHolder(satslots)

    # make root work-buffer work-item, addi it to wb
    witem = {  # root-node
        'bitdic': Root_bitdic,
        'depth': 0,             # layer-depth
        'index': 0,             # layer-index
        'valkey': 0,
        'parent': Root_bitdic,  # parent-br. For root: bitdic
        'sh': sh
    }
    # witem = (keyname, Root_bitdic, sh)
    wb.add_item(witem)
    while not wb.empty():
        wb = wb.work_thru()
        if type(wb).__name__ == 'Sat':
            return wb
    return None


if __name__ == '__main__':
    configfilename = 'cfg100-450.json'
    # configfilename = 'cfg60-262.json'
    # configfilename = 'config1.json'
    # configfilename = 'config1.sat'
    # configfilename = 'config20_80.sat'
    # configfilename = 'cfg60-262.json'

    if len(sys.argv) > 1:
        configfilename = sys.argv[1].strip()

    if configfilename.endswith('.sat'):
        result, value = verify_satfile(configfilename)
        if result:
            print(f'Verified: {value}')
        else:
            print('Not verified')

    elif configfilename.endswith('.json'):
        start_time = time.time()
        sat = process(configfilename)
        now_time = time.time()
        if sat:
            sat.cnf_file = configfilename
            # result = sat.verify(Root_bitdic)
            # if result:
            print('saved under ' + sat.save_dir)
            sat.save()  # save to verify/<cnf>.sat
        else:
            print('No sat found')
        time_used = now_time - start_time
        print(f'Time used: {time_used}')

    x = 1
