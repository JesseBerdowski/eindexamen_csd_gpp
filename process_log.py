# native imports
from datetime import datetime


class DataLog:
    def __init__(self):
        self.text = ''

    def write_line(self, s):
        t = datetime.now()
        self.text += '[{}] | {} \n'.format(t, s)

    def write_lst(self, lst):
        for i, item in enumerate(lst):
            if not i:
                self.write_line(item)
            elif i == len(lst) - 1:
                self.text += '\t \t' + '{}'.format(item) + '|' + '\n'
            else:
                self.text += '\t \t ' + '{}'.format(item) + '\n'

    def export_txt(self):
        file = open('static/out_visualisations/log.txt', 'w')
        file.writelines(self.text)
        file.close()
