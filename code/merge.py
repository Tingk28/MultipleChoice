import PySimpleGUI as sg
import json


def new_window(file_list):

    layout = []
    for i in range(len(file_list)):
        layout.append([sg.Text("File {0}".format(i+1)), sg.InputText(file_list[i], readonly=True, key='-FILE{0}-'.format(i)),
                       sg.Button('Import', key='-IMPORT{0}-'.format(i))])

    layout.append([sg.Push(), sg.Button('Add File', key='-ADD-'), sg.Button("Merge")])
    result = sg.Window('Merge', layout, finalize=True)

    for i in range(len(file_list)):
        result['-FILE{0}-'.format(i)].TKEntry.configure(readonlybackground='#FFFFFF')

    return result


def merge_file():

    files = ['']
    window = new_window(files)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if 'IMPORT' in event:
            index = int(event[-2])
            loc = sg.popup_get_file('select file', no_window=True, file_types=(("Text Files", "*.json"),))
            if loc == "":
                continue
            window['-FILE{0}-'.format(index)].update(loc)
            window['-FILE{0}-'.format(index)].TKEntry.configure(readonlybackground='#FFFFFF')

            files[index] = loc

        if event == '-ADD-':
            files.append('')
            window.close()
            window = new_window(files)

        if event == 'Merge':
            output = {}
            has_error = False
            for i in range(len(files)):
                try:
                    if files[i] == "":
                        continue
                    questions = []
                    file_name = files[i].split('/')[-1]
                    if ".json" in file_name:
                        file_name = file_name[:-5]
                    with open(files[i], 'r', encoding='UTF-8') as f:
                        temp = json.load(f)
                    for lo in temp:  # for every learning objective
                        questions += temp[lo]
                    if file_name in output.keys():  # 存在一樣的檔案名稱
                        file_name += "-1"
                    output[file_name] = questions

                except Exception as e:
                    has_error = True
                    sg.popup("File{0}路徑或格式錯誤\n合併終止".format(i+1), title="ERROR")
                    break

            if output != {} and not has_error:  # there is something in output
                save_loc = sg.popup_get_file("sava as", save_as=True, no_window=True, file_types=(("Text Files", "*.json"),))
                if save_loc == "":
                    sg.popup("請選擇儲存位置")
                    continue
                else:
                    with open(save_loc, 'w', encoding='UTF-8') as f:
                        json.dump(output, f)
                    sg.popup("檔案儲存成功！\n" + save_loc)
                    window.close()

        if event == sg.WIN_CLOSED:
            break


if __name__ == '__main__':
    merge_file()
