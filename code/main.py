import PySimpleGUI as sg
import json
import random
import os
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
import merge


def get_center_position(window):
    screen_width, screen_height = window.get_screen_dimensions()
    win_width, win_height = window.size
    return (screen_width - win_width) // 2, (screen_height - win_height) // 2  # x, y


def new_window(LOs, fontsize, size, location=(None, None)):
    layout = [[sg.Menu(menu_layout, key="-MENU-")],
              [sg.Text("請選擇檔案", key="-FILE-", grab=True)],
              [sg.OptionMenu(LOs, key="-LOS-", size=(10, 2)), sg.Button("Change LO"), sg.CBox("跳過是非", key="-SKIPTF-"),
               sg.CBox("順序隨機", key="-SHUFFLE-"), sg.Push(), sg.Text('進度:--/--', key="-PROGRESS-"),
               sg.Text("correct:0/wrong:0  score:0.00", key="-SCORE-")],
              [sg.Multiline("請選擇LO再開始作答\n選擇題：1 2 3 4 為ABCD\n是非題：1為False  2為True\n按下enter可以跳到下一題\n\
              有關使用說明與操作方式，請到下列網址了解更多\nhttps://github.com/Tingk28/MultipleChoice", key="-QUESTIONS-",
                            auto_size_text=True, font=('Arial', fontsize)
                            , expand_x=True, expand_y=True, border_width=2, disabled=True,
                            right_click_menu=['&Right', ['翻譯']])],
              [sg.Button('A', key="-A-", expand_x=True, expand_y=False, font=('Arial', fontsize)),
               sg.Button('B', key="-B-", expand_x=True, expand_y=False, font=('Arial', fontsize))],
              [sg.Button('C', key="-C-", expand_x=True, expand_y=False, font=('Arial', fontsize)),
               sg.Button('D', key="-D-", expand_x=True, expand_y=False, font=('Arial', fontsize))],
              [sg.Button('Redo', key="-REDO-", font=('Arial', fontsize)), sg.Push(),
               sg.Button('Previous', key="-PREVIOUS-", font=('Arial', fontsize)),
               sg.Button('Next', key="-NEXT-", font=('Arial', fontsize))],
              [sg.Sizegrip()]
              ]

    window = sg.Window('選擇題刷題', layout, icon='icon.ico', return_keyboard_events=True, size=size, resizable=True,
                       finalize=True, location=location)
    if location == (None, None):
        location = get_center_position(window)
        window.move(location[0], location[1])
    return window


def new_translate(window):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=%s" % "720,780")
        driver = webdriver.Chrome(r'chromedriver.exe', options=options)
        driver.get(r'https://translate.google.com.tw/?hl=zh-TW')  # 連線至google翻譯
        return [True, driver]

    except Exception as e:
        window['-QUESTIONS-'].update(
            "Web Driver已過期或不存在，請至 https://chromedriver.chromium.org/downloads 下載對應版本\n或選擇檔案直接開始")
        return [False, None]


def translate(string, driver):
    driver.find_element(By.TAG_NAME, "textarea").clear()
    driver.find_element(By.TAG_NAME, "textarea").send_keys(string.replace('\t', ' ').replace('\n\n', '\n'))


file_list = ['load from...']
file_list.extend(os.listdir("multi json"))

menu_layout = [
    ['File', [['Open', file_list], '---', 'Save as', 'Merge']],
    ['Text Size', ['9', '10', '12', '14', '16', '18', '20', '24', '28']],
    ['Timeout', ['500', '1000', '1500', '2000']],
    ['About', ['Info']]
]

file = ''
LOs = []

LOs.append("所有章節")

open_translate = sg.popup_yes_no("是否開啟翻譯功能？")

fontsize = 16
size = (600, 570)
window = new_window(LOs, fontsize, size)
buttonlist = [window["-A-"], window["-B-"], window["-C-"], window["-D-"]]
all = []
choice_list = ["A", "B", "C", "D"]
trans = ''
timeout = 1000

if open_translate == 'Yes':
    driver_result = new_translate(window)
    driver_exist = driver_result[0]
    driver = driver_result[1] if driver_exist else None

    if driver_exist is False:  # 如果開啟瀏覽器失敗
        open_translate = 'No'

if open_translate == "No" or open_translate is None:
    menu_layout = [
        ['File', [['Open', file_list], '---', 'Save as', 'Merge']],
        ['Text Size', ['9', '10', '12', '14', '16', '18', '20', '24', '28']],
        ['About', ['Info']]]
    window["-MENU-"].update(menu_layout)
    driver_exist = False
    timeout = 100000

while True:
    event, values = window.read(timeout=timeout)
    # print(event)
    if event in ['MouseWheel:Up', 'MouseWheel:Down', 'Up:38', 'Down:40']:
        continue

    if driver_exist:
        try:
            if event == '翻譯':
                translate(window['-QUESTIONS-'].get(), driver)
            else:
                temp_trans = window['-QUESTIONS-'].widget.selection_get()
                if trans != temp_trans or event != '__TIMEOUT__':
                    trans = temp_trans
                    translate(trans, driver)

        except WebDriverException as error:
            sg.popup("網頁出現問題，將關閉翻譯功能", title="")
            menu_layout = [
                ['File', [['Open', file_list], '---', 'Save as', 'Merge']],
                ['Text Size', ['9', '10', '12', '14', '16', '18', '20', '24', '28']],
                ['About', ['Info']]]
            window["-MENU-"].update(menu_layout)
            driver_exist = False
            timeout = 100000

        except Exception as e:
            trans = ''
            if event == '__TIMEOUT__':
                continue

    if event == sg.WIN_CLOSED:  # 關閉視窗
        break

    if event in ['9', '10', '12', '14', '16', '18', '20', '24', '28', '32']:  # 更換字體大小
        window['-QUESTIONS-'].update(font=('Arial', int(event)))
        fontsize = int(event)

    if event in ['500', '1000', '1500', '2000']:
        timeout = int(event)

    if event in file_list:  # 更換檔案
        file = event
        try:
            if event != 'load from...':
                with open(os.path.join("multi json", file), 'r', encoding='UTF-8')as f:
                    Questions = json.load(f)
            else:
                file = sg.popup_get_file('load question', no_window=True, file_types=(("Text Files", "*.json"),))
                if file == '':  # 沒有選擇檔案
                    sg.popup("請選擇檔案！")
                    continue
                with open(file, 'r', encoding='UTF-8')as f:
                    Questions = json.load(f)
            LOs = []
            for key in Questions.keys():
                LOs.append(key)
            LOs.append("所有章節")

            # reset all parameter
            all = []
            question_number = len(all)  # 總題目數
            current = 0  # 當前題號
            correct = 0  # 答對次數
            wrong = 0  # 答錯次數
            # restart the system
            size = window.size
            location = window.CurrentLocation()
            window.close()
            window = new_window(LOs, fontsize, size, location=location)
            file = file.split('/')[-1]
            window["-FILE-"].update(file)
            buttonlist = [window["-A-"], window["-B-"], window["-C-"], window["-D-"]]

            continue

        except Exception as e:
            window["-QUESTIONS-"].update(value="匯入的檔案格式錯誤\n請重新選擇")
            sg.popup("匯入的檔案格式錯誤\n請重新選擇")

    if event == "Change LO":  # 選擇LO
        if values['-LOS-'] == '' or file == '':
            continue
        practice_range = LOs.index(values['-LOS-'])
        all = []
        if practice_range == len(Questions.keys()):  # load questions
            for key in Questions.keys():
                for i in Questions[key]:
                    i['shuffled'] = False  # 選項是否被打亂
                    i['student_ans'] = -1  # 是否作答過
                    all.append(i)
        else:
            for i in Questions[list(Questions.keys())[practice_range]]:
                i['shuffled'] = False
                i['student_ans'] = -1
                all.append(i)
        # 移除是非
        del_list = []
        for i in all:
            if 'choice' not in i.keys() and values['-SKIPTF-']:
                del_list.append(i)
        for i in del_list:
            all.remove(i)
        # 題目隨機順序
        if values['-SHUFFLE-']:
            random.shuffle(all)
        question_number = len(all)  # 總題目數
        current = 0  # 當前題號
        correct = 0  # 答對次數
        wrong = 0  # 答錯次數
        window["-QUESTIONS-"].update(text_color="#000000")
        if question_number == 0:
            window["-QUESTIONS-"].update("檔案為空或該章節沒有題目")

    if event == 'Info':
        sg.popup("本專案僅提供軟體本身，並未提供題目內容。請使用者自行創建、匯入", title="關於")

    if event == 'Merge':  # 合併檔案
        window.disappear()
        window['-MENU-'].update(visible=False)  # mac版需要隱藏左上選單列
        merge.merge_file()
        window['-MENU-'].update(visible=True)
        window.reappear()
        continue

    if len(all) == 0:  # 還沒讀到任何題目
        window["-QUESTIONS-"].update(text_color="#FF0000")
        continue

    if event in ['1', '2', '3', '4']:  # user 按下1 2 3 4
        student_ans = int(event[0]) - 1
        buttonlist[student_ans].click()

    if event == "\r" or event == "Right:39":  # user 按下enter 鍵或右邊方向鍵（下一題）
        window["-NEXT-"].click()

    if event == "Left:37":  # user 按下左邊方向鍵（上一題）
        window["-PREVIOUS-"].click()

    if event in ["-A-", "-B-", "-C-", "-D-"]:  # 選擇選項
        student_ans = event[1]
        student_ans = choice_list.index(student_ans)
        all[current]['student_ans'] = student_ans
        if student_ans == all[current]['ans']:
            correct += 1
        else:
            wrong += 1

    if event == "-PREVIOUS-":  # 上一題
        if current > 0:
            current -= 1
        else:
            sg.Popup("已經是第一題")
    if event == "-NEXT-":  # 下一題
        if current < len(all) - 1:
            current += 1
        else:
            sg.Popup("已經是最後一題")

    if event == "-REDO-":  # 重做此題
        if all[current]['student_ans'] == -1:
            pass
        elif all[current]['student_ans'] != all[current]['ans']:
            wrong -= 1
        elif all[current]['student_ans'] == all[current]['ans']:
            correct -= 1

        all[current]['shuffled'] = False
        all[current]['student_ans'] = -1

    if event == 'Save as':  # 存錯誤的題目
        file = sg.popup_get_file("sava as", save_as=True, no_window=True, file_types=(("Text Files", "*.json"),))
        # print(file)
        if file != '':
            output = {'LO1': []}
            for i in all:
                if i['student_ans'] != i['ans'] and i['student_ans'] != -1:
                    output['LO1'].append(i)

            with open(file, 'w', encoding='UTF-8')as f:
                json.dump(output, f)
            sg.popup("檔案儲存成功！\n" + file)

    # 顯示區域
    question_str = all[current]['question'] + "\n"

    # 選擇題
    if 'choice' in all[current].keys():  # 選擇題
        window["-A-"].update(text="A")
        window["-B-"].update(text="B")
        window["-C-"].update(disabled=False)
        window["-D-"].update(disabled=False)
        q_type = 0
        ##打亂選項
        if not all[current]['shuffled']:
            ans = all[current]['choice'][all[current]['ans']]
            random.shuffle(all[current]['choice'])
            ans = all[current]['choice'].index(ans)
            all[current]['shuffled'] = True
            all[current]['ans'] = ans
        for c in range(4):
            question_str += choice_list[c] + ") " + all[current]['choice'][c]
    else:  # 是非題
        TF = {"F": 0, "T": 1, 1: 1, 0: 0}
        all[current]['ans'] = TF[all[current]['ans']]
        window["-A-"].update(text="F")
        window["-B-"].update(text="T")

    if all[current]['student_ans'] == -1:  # 還沒作答過
        for i in buttonlist:
            i.update(disabled=False, button_color=('white', "#283b5b"))

        if 'choice' not in all[current].keys():  # 若為是非題，禁用CD選項
            window["-C-"].update(disabled=True)
            window["-D-"].update(disabled=True)
    else:  # 達過的題目
        for i in buttonlist:
            i.update(disabled=True, button_color=('white', "#283b5b"))  # 禁用所有選項

        buttonlist[all[current]['ans']].update(button_color="#00FF00")  # 答案標示綠色
        if all[current]['student_ans'] != all[current]['ans']:  # 錯的顯示紅色
            buttonlist[all[current]['student_ans']].update(button_color="#FF5050")

    # question_str=all[current]['question']+"".join(all[current]['choice'])
    window["-QUESTIONS-"].update(question_str)
    window["-PROGRESS-"].update(f"進度:{current + 1}/{question_number}")
    score = round(0 if correct + wrong == 0 else 100 * correct / (correct + wrong), 2)
    window["-SCORE-"].update(f"correct:{correct}/wrong:{wrong}  score:{score}")

    if event in ["-A-", "-B-", "-C-", "-D-"] and wrong + correct == question_number:
        sg.Popup(f"已經完成作答\n得分：{score}")

window.close()
if driver_exist:
    try:
        driver.quit()
    except:
        pass

