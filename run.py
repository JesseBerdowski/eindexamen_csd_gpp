from hparams import HyperParameters
from process_log import DataLog
from statistical_analysis import Bootstrapping, PlaceboTreatment
from tkinter import Button, Tk, filedialog, Label, messagebox
import threading
import time


class UI:
    def __init__(self):
        self.root = Tk()
        self.root.title('')
        self.revenue_file = ''
        self.hparam_file = ''

        label_height = 1
        label_width = 60

        b_width = 20

        hparam_b = Button(self.root, text="select hparam data", command=self.select_hparams, height=label_height, width=b_width)
        self.hparam_l = Label(self.root, text='<-- selected hparam data', bg="white", height=label_height, width=label_width)

        data_b = Button(self.root, text='select revenue data', command=self.select_data, height=label_height, width=b_width)
        self.data_l = Label(self.root, text='<-- selected revenue data', bg="white", height=label_height, width=label_width)

        run_b = Button(self.root, text='run', command=lambda: [self._run(), self._run_l()], height=label_height, width=b_width)
        self.run_l = Label(self.root, text='waiting for calculation..', bg="grey", height=label_height, width=label_width)

        hparam_b.grid(row=1, column=2)
        self.hparam_l.grid(row=1, column=5)

        data_b.grid(row=2, column=2)
        self.data_l.grid(row=2, column=5)

        run_b.grid(row=3, column=2)
        self.run_l.grid(row=3, column=5)

        while True:
            self.root.update_idletasks()
            self.root.update()

    def _run_l(self):
        self.run_l.configure(text='started calculation...')
        self.root.update_idletasks()

    def select_hparams(self):
        hparam_file = filedialog.askopenfile(title='Select hparam .csv file')
        filename = hparam_file.name.split('/')[-1]
        self.hparam_file = hparam_file.name
        self.hparam_l.configure(text='hparam data selected with name `{}`'.format(filename))

    def select_data(self):
        revenue_file = filedialog.askopenfile(title='Select Revenue Data')
        filename = revenue_file.name.split('/')[-1]
        self.revenue_file = revenue_file.name
        self.data_l.configure(text='revenue data selected with name `{}`'.format(filename))

    def _run(self):
        self.run_l.configure(text='started calculation')
        self.root.update_idletasks()
        self.root.update()
        time.sleep(1)
        threading.Thread(run(r_file=self.revenue_file, h_file=self.hparam_file)).start()

        self.run_l.configure(text='finished calculation')
        self.root.update_idletasks()
        self.root.update()

        messagebox.showinfo("", 'Completed the calculations succesfully')
        exit()


def run(r_file, h_file):
    # print('started calculations...')
    dl = DataLog()
    hpms = HyperParameters(data_log=dl, h_file=h_file)

    bs = Bootstrapping(hparams=hpms, data_log=dl, r_file=r_file)

    # results is a list of dicts containing relevant statistical results
    results_bs = bs.analyze()
    dl.write_lst(results_bs)

    # pb = PlaceboTreatment(hparams=hpms, data_log=dl, r_file=r_file)

    # results dict with p-val of coeff
    # results_pt = pb.analyze(True, results_bs)
    # print(results_pt)
    # dl.write_lst(results_pt)
    #
    dl.export_txt()


user_interface = UI()


