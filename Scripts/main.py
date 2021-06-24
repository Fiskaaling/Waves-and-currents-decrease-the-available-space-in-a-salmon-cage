import pandas as pd
import numpy as np
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import simpledialog, messagebox
from tkinter import filedialog
import progressbar  # Install Progressbar 2
from pathlib import Path


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        Frame.pack(self, side=BOTTOM)
        self.init_window()

    def init_window(self):
        self.master.title("Echosounder surface finder and exporter")
        self.pack(fill=BOTH, expand=1)
        main_frame = Frame(self, borderwidth=1)
        main_frame.pack(fill=BOTH, expand=False, side=TOP)

    @staticmethod
    def client_exit(self):
        exit()


def find_max(data, under):
    maxi = []
    for i in range(len(data.iloc[1, :])):
        this_row = data.iloc[:, i]
        max_c = -1000
        max_ci = -1000
        for j, col in enumerate(this_row):
            if (j > under) and not under == 0:
                continue
            if col > max_c:
                max_c = col
                max_ci = j
        maxi.append(max_ci)
    return maxi


def find_max_ranger(data, last_ok, search_range=100, under=600):
    ok_next_round = last_ok
    maxi = []
    for i in range(len(data.iloc[1, :])):
        thisrow = data.iloc[:, i]
        maxc = -1000
        maxci = -1000
        for j, col in enumerate(thisrow):
            if j > under:
                continue
            if col > maxc:
                maxc = col
                maxci = j
        if abs(maxci - ok_next_round) > search_range:
            print('Oh!, a jump')
            maxc = -1000
            maxciR = -1000
            for j, col in enumerate(thisrow.iloc[ok_next_round - search_range:ok_next_round + search_range]):
                if col > maxc:
                    maxc = col
                    maxciR = j
            if (maxciR + ok_next_round - search_range) > under:
                messagebox.showinfo("Damn!", "Range searcher failed. Look carefully before proceeding")
                if maxci < 0:
                    maxci = 0
                maxi.append(maxci)
                ok_next_round = maxci
            else:
                if maxciR + ok_next_round - search_range < 0:
                    maxi.append(0)
                else:
                    maxi.append(maxciR + ok_next_round - search_range)
            print(maxciR + ok_next_round - search_range)
            ok_next_round = maxciR + ok_next_round - search_range
        else:
            maxi.append(maxci)
            ok_next_round = maxci
    return maxi


def find_next_large_diff(data, limit=100):
    diff_data = np.diff(data)
    for i, d in enumerate(diff_data):
        if abs(d) > limit:
            return i
    return -1


def choose_file():
    global filename
    global dataign
    filename = filedialog.askopenfile(title='Choose file', filetypes=(("csv file", "*.csv"), ("all files", "*.*"))).name
    print(filename)
    print("Reading data")
    data = pd.read_csv(filename)
    data = data.iloc[::-1]
    print("Done")
    ignore_last = 50
    ignore_first = 300
    dataign = data.iloc[ignore_first:-ignore_last, :]
    dataign = pd.DataFrame(np.array(dataign))
    global fig
    global figS
    global ax
    global axS
    fig.clf()
    figS.clf()
    ax = fig.add_subplot(111)
    axS = figS.add_subplot(111)
    global max_index
    global lines
    global yNumbers
    global cursor
    cursor = 0
    max_index = find_max(dataign, 800)
    yNumbers = np.arange(len(dataign.iloc[:, 1]))
    lines = ax.plot(max_index)
    ax.imshow(dataign, cmap='plasma', vmin=-120, aspect='auto')
    ax.grid(True)
    canvas.draw()
    canvasSingle.draw()


def split_file():
    filename = filedialog.askopenfile(title='Choose file', filetypes=(("csv file", "*.csv"), ("all files", "*.*"))).name
    data = pd.read_csv(filename)
    pings_per_file = 8000
    pings_left = len(data.iloc[1, :])
    counter = 0
    while pings_left > 0:
        if pings_left > pings_per_file:
            df_toWrite = data.iloc[:,
                         len(data.iloc[1, :]) - pings_left:len(data.iloc[1, :]) - pings_left + pings_per_file]
        else:
            df_toWrite = data.iloc[:, len(data.iloc[1, :]) - pings_left:]
        print('Writing file: ' + filename[:-4] + '_' + str(counter) + '.csv')
        pd.DataFrame.to_csv(df_toWrite, filename[:-4] + '_' + str(counter) + '.csv', index=False)
        pings_left -= pings_per_file
        print('Job Done!')
        counter += 1

    print(data)
    print(len(data.iloc[:, 1]))
    print(len(data.iloc[1, :]))


def export_stuff():
    SPEEDOFSOUND = 1500  # m/s
    SAMPLETIME = 0.00002  # s
    DISTANCEPERSAMPLE = SPEEDOFSOUND * SAMPLETIME / 2
    IGNORE_LAST = 50
    main_file = Path(filedialog.askopenfile(
        title='Choose _0 file',
        filetypes=(("csv files", "*.csv"), ("all files", "*.*"))).name
                     )

    # ------------------Finding all files---------------------------------------

    if not '_0' in main_file.name:
        print('This is not a "_0" file')
        exit()

    folder = main_file.parent
    rootname = main_file.name.split('_0')[0]

    data_files = [main_file]
    maxi_files = [(folder / (rootname + '_0maxi.csv'))]

    if not (folder / (rootname + '_0maxi.csv')).is_file():
        print(f'Found no {maxi_files[0].name} file')
        exit()
    i = 0

    while True:
        i += 1
        if (folder / (rootname + f'_{i}.csv')).is_file() \
                and (folder / (rootname + f'_{i}maxi.csv')).is_file():
            data_files.append(folder / (rootname + f'_{i}.csv'))
            maxi_files.append(folder / (rootname + f'_{i}maxi.csv'))
            continue
        break

    time_Filename = (folder / (rootname[:-1] + '-T.csv'))

    if not time_Filename.is_file():
        print(f'Found no {time_Filename.name()} file')
        exit()

    # ------------------fixa tíðar fílin-----------------------------------------

    timeData = pd.read_csv(time_Filename, header=None)[0].values

    if timeData[0] == 'x':
        timeData = timeData[1:]

    if '\t' in timeData[0]:
        timeData = [x.split('\t')[1] for x in timeData]

    # ------------------fixa tíðar fílin-----------------------------------------
    print('Found following datafiles:')
    for x in data_files:
        print(x.name)
    print('And corresponding surface distance files:')
    for x in maxi_files:
        print(x.name)
    print('And time file')
    print(time_Filename.name)

    stuff_to_export = pd.DataFrame(columns=['time', 'depth', 'Sv'])
    tel_ping = 0
    timestep_mat = np.array([])
    time_row = 0

    for datafil, maxifil in zip(data_files, maxi_files):

        print('Processing: ' + datafil.name)

        disMaxi = pd.read_csv(maxifil)
        disData = pd.read_csv(datafil).values
        disData = disData[::-1, :]

        print('Trimming data')
        processed = disData.copy()
        for i in progressbar.progressbar(range(len(disData[1, :]))):
            tmp = disData[disMaxi.iloc[i, 1] + 300:-IGNORE_LAST, i]
            variabulTilAsu = 300  # Her Ása!! Broyt hetta! So burdi tað rigga
            tmp = np.append(tmp, list(np.ones([disMaxi.iloc[i, 1] + IGNORE_LAST + 300]) * -variabulTilAsu))
            processed[:, i] = tmp

        disData = processed
        tel_ping += disData.shape[1]

        first_col = 0

        print('Averaging\n')
        for first_col in progressbar.progressbar(range(0, disData.shape[1], 75)):
            if disData.shape[1] < first_col + 75:

                timestep_mat = disData[:, first_col:]
                break

            elif timestep_mat.shape[0] > 0:

                caryover_cols = timestep_mat.shape[0]

                timestep_mat = np.concatenate(
                    (
                        timestep_mat,
                        disData[:, first_col: first_col + (75 - caryover_cols)]
                    ), axis=1)
                first_col += 75 - caryover_cols

            else:
                timestep_mat = disData[:, first_col:first_col + 75]
                first_col += 75

            disTid = timeData[time_row]
            time_row += 75

            for first_row in range(0, timestep_mat.shape[0] - 11, 11):

                if timestep_mat.shape[0] < first_row + 11:
                    break

                working_mat = np.power(10, timestep_mat[first_row:first_row + 11, :] / 10)
                mean = np.mean(working_mat)

                if np.isnan(mean).any():
                    temp_list = [x for x in working_mat.flatten() if not np.isnan(x)]
                    if temp_list:
                        mean = np.mean(temp_list)
                    else:
                        mean = -201

                meanSvSubDepthTime = 10 * np.log10(mean)

                if not np.isnan(meanSvSubDepthTime):
                    stuff_to_export = stuff_to_export.append(
                        {
                            'time': disTid.split('.')[0],
                            'depth': first_row * DISTANCEPERSAMPLE,
                            'Sv': meanSvSubDepthTime,
                        },
                        ignore_index=True)

            timestep_mat = np.array([])

    stuff_to_export.to_csv(folder / f'{rootname}_Export.csv', index=False, na_rep='NaN')
    print('Done!')
    print(len(disTid))
    print(time_row)
    print(tel_ping)


root = Tk()
root.geometry("1200x800")
app = Window(root)

menu_frame = Frame(app)
menu_frame.pack(side=TOP, anchor=N)
velMappuBtn = Button(menu_frame, text='Choose file', command=lambda: choose_file())
velMappuBtn.pack(side=LEFT)

Label(menu_frame, text='Cursor position: ').pack(side=LEFT)
cLabel = Label(menu_frame, text='0')
cLabel.pack(side=LEFT)

exportStuffBtn = Button(menu_frame, text='Export processed files', command=lambda: export_stuff())
exportStuffBtn.pack(side=RIGHT)

splittaFilarBtn = Button(menu_frame, text='Split files', command=lambda: split_file())
splittaFilarBtn.pack(side=RIGHT, anchor=E)
fig = Figure(figsize=(12, 8), dpi=100)
figS = Figure(figsize=(8, 8), dpi=100)
singlePlot_frame = Frame(app, borderwidth=1, width=50)
singlePlot_frame.pack(fill=Y, expand=False, side=LEFT, anchor=N)
plot_frame = Frame(app, borderwidth=1, width=100)
plot_frame.pack(fill=BOTH, expand=True, side=LEFT, anchor=N)
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvasSingle = FigureCanvasTkAgg(figS, master=singlePlot_frame)
fig.clf()
figS.clf()
ax = fig.add_subplot(111)
axS = figS.add_subplot(111)
axS.plot([1, 2, 3, 2, 6]) # Just to draw something on the screen

global max_index
global lines
global filename
filename = "/home/johannus/Documents/data/Echolodd/D20200224-T1112321.csv"

print("Reading data")

ax.grid(True)
canvas.draw()
canvas.get_tk_widget().pack(fill=BOTH, expand=1)
canvasSingle.draw()
canvasSingle.get_tk_widget().pack(fill=BOTH, expand=1)
print('done')

scatters = ax.scatter(0, 100, c='white')

# yNumbers = np.arange(len(dataign.iloc[:, 1]))
global yNumbers
yNumbers = np.arange(10)

answer = 0
max_ping_index = 0
thisPing = (1, 2, 3)
save_changes = False

visible_min = 0
visible_max = 1500
visible_range = visible_max - visible_min
ax.set_xlim([visible_min, visible_max])
ax.set_xticks(np.arange(visible_min, visible_max, 100))
okValues = []


def draws(figS, dataign, yNumbers, bl_index, cursor, answer):
    figS.clf()
    axS = figS.add_subplot(111)
    axS.plot(dataign.iloc[:, cursor], yNumbers * -1)
    axS.axhline(y=-bl_index, c='k')
    axS.axhline(y=-float(answer), c='red')
    canvasSingle.draw()


def key(event):
    global max_ping_index
    global answer
    global lines
    global scatters
    global cursor
    global figS
    global save_changes
    global axS
    global thisPing
    global okValues
    print(event.keysym)
    if event.keysym == '1':
        okValues.append(cursor)
        ax.scatter(cursor, 0, c='g')
    if event.keysym == 'onehalf':
        cursor = int(simpledialog.askstring("Input", "Move cursor to", parent=app))
        visible_min = cursor - 20
        if visible_min < 0:
            visible_min = 0
        visible_max = cursor + 520
        ax.set_xlim([visible_min, visible_max])
        ax.set_xticks(np.arange(visible_min, visible_max, 100))
    if event.keysym == 'KP_0' or event.keysym == '0':
        cursor = 0
    if event.keysym == 'Right':
        cursor = cursor + 1
        draws(figS, dataign, yNumbers, max_index[cursor], cursor, answer)
    if event.keysym == 'Left':
        cursor = cursor - 1
        draws(figS, dataign, yNumbers, max_index[cursor], cursor, answer)
    if event.keysym == 'Up':
        max_ping_index += 1
        save_changes = True
        draws(figS, dataign, yNumbers, max_ping_index, cursor, answer)
        axS.plot(thisPing, yNumbers * -1)
        # axS.axhline(y=-max_ping_index, c='k')
        axS.axhline(y=-float(answer), c='red')
    if event.keysym == 's':
        toSave = pd.DataFrame(max_index)
        print('Saving....')
        toSave.to_csv(filename[:-4] + 'maxi.csv')
        print('Done!')
        bad_joke = np.floor(np.random.random() * 16)
        joke = "text"
        if bad_joke == 0:
            joke = "How do you spell Canda? C,eh,N,eh,D,eh"
        elif bad_joke == 1:
            joke = "I saw a French rifle on eBay today It's never been fired but I heard it was dropped once."
        elif bad_joke == 2:
            joke = "A Mexican fireman had twin boys He named them Jose and Hose B"
        elif bad_joke == 3:
            joke = "My ex-wife still misses me... But her aim is gettin better."
        elif bad_joke == 4:
            joke = "If you have a parrot and you don't teach it to say,\"Help, they've turned me into a parrot.\" you are wasting everybody's time."
        elif bad_joke == 5:
            joke = " What do you call a fish with a tie? soFISHticated"
        elif bad_joke == 6:
            joke = " What do sea monsters eat? Fish and ships."
        elif bad_joke == 7:
            joke = " What party game do fish like to play? Salmon Says."
        elif bad_joke == 8:
            joke = " How does an octopus go to war? Well-armed!"
        elif bad_joke == 9:
            joke = " What do you call a big fish who makes you an offer you can't refuse? The Codfather!"
        elif bad_joke == 10:
            joke = "What’s a pirate’s favorite letter? \n R? \n No. It be the C!"
        elif bad_joke == 11:
            joke = "Have you heard any good pirate jokes? Well, neither have ayyyye"
        elif bad_joke == 12:
            joke = "Why does it take pirates so long to learn the alphabet? Because they can spend years at C."
        elif bad_joke == 13:
            joke = "How do pirates prefer to communicate? A: Aye to aye!"
        elif bad_joke == 14:
            joke = " Why did nobody want to play cards with the pirate? Because he was standing on the deck."
        elif bad_joke == 15:
            joke = "Why is pirating so addictive? They say once ye lose yer first hand, ye get hooked!"
        messagebox.showinfo("Finished", joke)
    if event.keysym == 'KP_Decimal' or event.keysym == 'comma':
        answer = simpledialog.askstring("Input", "Surface is above?", parent=app)
        visible_max = cursor + 500
        max_index[cursor:visible_max] = find_max(dataign.iloc[:, cursor:visible_max], float(answer))
        l = lines[0]
        l.remove()
        lines = ax.plot(max_index, c='lime', linewidth=0.5)
    if event.keysym == '3':
        visible_max = cursor + 500
        max_index[cursor:visible_max] = find_max_ranger(dataign.iloc[:, cursor:visible_max], max_index[cursor],
                                                        search_range=20, under=float(answer))
        l = lines[0]
        l.remove()
        lines = ax.plot(max_index, c='lime', linewidth=0.5)

    elif event.keysym == 'Tab':
        if save_changes:
            print('Do something')
            print(max_index[cursor])
            max_index[cursor] = max_ping_index
            print(max_index[cursor])
            save_changes = False
            l = lines[0]
            l.remove()
            lines = ax.plot(max_index, c='lime', linewidth=0.5)
        last_cursorPos = cursor
        cursor = cursor + find_next_large_diff(max_index[last_cursorPos:]) + 1
        while cursor in okValues:  # If the value is ok, continue to the next
            cursor = cursor + find_next_large_diff(max_index[last_cursorPos:]) + 1
        scatters.remove()
        scatters = ax.scatter(cursor, 100, c='white')

        draws(figS, dataign, yNumbers, max_index[cursor], cursor, answer)

        visible_min = cursor - 20
        if visible_min < 0:
            visible_min = 0
        visible_max = cursor + 520

        ax.set_xlim([visible_min, visible_max])
        ax.set_xticks(np.arange(visible_min, visible_max, 100))
        canvasSingle.draw()

    elif event.keysym == 'Delete':
        figS.clf()
        axS = figS.add_subplot(111)
        if not save_changes:
            save_changes = True
            thisPing = dataign.iloc[:, cursor]
            if max_index[cursor] > 5:
                thisPing[max_index[cursor] - 1] = -120
                thisPing[max_index[cursor] - 2] = -120
                thisPing[max_index[cursor] - 3] = -120
                thisPing[max_index[cursor] - 4] = -120
                thisPing[max_index[cursor] - 5] = -120
            thisPing[max_index[cursor]] = -120
            thisPing[max_index[cursor] + 1] = -120
            thisPing[max_index[cursor] + 2] = -120
            thisPing[max_index[cursor] + 3] = -120
            thisPing[max_index[cursor] + 4] = -120
            thisPing[max_index[cursor] + 5] = -120
            max_ping_index = 0
            max_value = -5000
            for i, amp in enumerate(thisPing):
                if amp > max_value and (i < float(answer)):
                    max_value = amp
                    max_ping_index = i
            axS.axhline(y=-max_ping_index, c='k', linewidth=1)
        else:
            thisPing[max_ping_index] = -120
            if max_ping_index > 2:
                thisPing[max_ping_index - 1] = -120
                thisPing[max_ping_index - 2] = -120
                thisPing[max_ping_index - 3] = -120
                thisPing[max_ping_index - 4] = -120
                thisPing[max_ping_index - 5] = -120
            thisPing[max_ping_index + 1] = -120
            thisPing[max_ping_index + 2] = -120
            thisPing[max_ping_index + 3] = -120
            thisPing[max_ping_index + 4] = -120
            thisPing[max_ping_index + 5] = -120
            max_ping_index = 0
            max_value = -5000
            for i, amp in enumerate(thisPing):
                if amp > max_value and (i < float(answer)):
                    max_value = amp
                    max_ping_index = i
            axS.axhline(y=-max_ping_index, c='k')
        axS.plot(thisPing, yNumbers * -1)
        # axS.axhline(y=-max_ping_index, c='k')
        axS.axhline(y=-float(answer), c='red')

        canvasSingle.draw()
    elif event.keysym == 'KP_Subtract' or event.keysym == 'minus':
        ax.set_xlim([0, len(dataign.iloc[1, :])])
        ax.set_xticks(np.arange(visible_min, visible_max, 100))
    elif event.keysym == 'KP_Add' or event.keysym == 'plus':
        visible_min = cursor - 500
        if visible_min < 0:
            visible_min = 0
        visible_max = cursor + 500
        ax.set_xlim([visible_min, visible_max])
        ax.set_xticks(np.arange(visible_min, visible_max, 100))
    ax.grid(True)
    canvas.draw()


root.bind('<Key>', key)
root.mainloop()
