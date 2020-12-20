from datetime import datetime


class Visualizer:
    def __init__(self, vkdic, nov):
        self.vkdic = vkdic
        self.nov = nov

    def output_vklause(self, kn):
        klause = self.vkdic[kn].dic
        bits = sorted(list(klause.keys()))
        bits.reverse()
        msg = f'{kn}: ' + '{'
        for b in bits:
            msg += f'{b}:' + str(klause[b]) + '  '
        msg += ' }'
        return msg

    def output_vkdic(self, seed_name):
        knames = sorted(list(self.vkdic.keys()))
        msg = ''
        for kn in knames:
            msg += self.output_vklause(kn)
            if kn == seed_name:
                msg += "  seed"
            msg += '\n'
        # msg += '-'*60 + '\n'
        return knames, msg

    def output(self, bdic, tx=None):
        fname = bdic.name.replace('@', "'")
        fname = fname.replace("1t", "t")
        filename = fname + '.txt'
        if not tx and type(bdic.conversion) != type(''):
            tx = bdic.conversion
        knames, koutput = self.output_vkdic(bdic.seed_name)
        fil = open('./verify/' + filename, 'w')
        fil.write(filename + '\n')
        fil.write('-'*60 + '\n')
        if tx:
            line = tx.output()
            fil.write(line + '\n')
        fil.write(koutput)
        line = '------ '
        for i in range(self.nov):
            line += str(self.nov - i - 1) + '--'
        fil.write(line + '\n')
        for v in range(2**self.nov):
            head = str(v).zfill(5) + ': '
            msg = '  '.join(list(bin(v)[2:].zfill(self.nov)))
            line = head + msg + ' $ '
            for kn in knames:
                if self.vkdic[kn].hit(v):
                    line += f'{kn} '
            fil.write(line + '\n')
        fil.close()

    def print_kstr(self, kn, kdic, nov):
        bns = sorted(list(kdic.keys()), reverse=True)
        m = f'"{kn}":' + '{'
        # for b in bns:
        #     L = (nov - b) * ' '
        #     m += L + str(kdic[b])
        # m += '  }'
        # m += ', #   {'
        for b in bns:
            m += ' ' + str(b) + ':' + str(kdic[b]) + ','
        m = m.strip(',') + ' },'
        return m

    def output_config_file(self, vkdic, nov, fname):
        dt_string = datetime.now().isoformat()
        kns = sorted(list(vkdic.keys()))
        lines = []
        lines.append(f'# {fname}  -  {dt_string}')
        lines.append('{')
        lines.append('  "nov": ' + str(nov) + ',')
        lines.append('  "kdic": {')
        # for kn, vk in vkdic.items():
        for kn in kns:
            lines.append('    ' + self.print_kstr(kn, vkdic[kn].dic, nov))
        lines.append('  }')
        lines.append('}')

        outf = open(f'./configs/{fname}', 'w')
        for line in lines:
            outf.write(line + '\n')
        outf.close()
        #         import pprint
        #         data = {
        #             "nov": nov,
        #             "kdic": {kn: vk.dic for kn, vk in vkdic.items()}
        #         }
        #         output_s = pprint.pformat(data)
        # #          ^^^^^^^^^^^^^^^
        #         open(f'./configs/{fname}', 'w').write(output_s)
