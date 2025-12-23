import math
import ctypes
import random
import re
import os
import pathlib
import json

# Взял с интернета
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

class TheRandomizer:
    def __init__(self):
        self.itemlistList = []
        self.keyListRunner = {}
        self.keyList = []

        self.Console = ConsoleTemplate()

    # major function for program
    def PushRandom(self, keyNameFile, count):
        currentDir = pathlib.Path(__file__).parent
        items_input = ""

        with open(f"lists/{keyNameFile}", encoding='utf-8') as file:
            strings = file.readlines()
            items_input = ' '.join(strings)

        def RandomItem(count):
            def parse_item(line):
                pattern = r"([\d.]+)\s+(\w+)\s+(.+?)\s+х(\d+)"
                match = re.match(pattern, line.strip())
                if match:
                    chance = float(match.group(1))
                    rarity = match.group(2)
                    name = match.group(3)
                    quantity = int(match.group(4))
                    return {'chance': chance, 'rarity': rarity, 'name': name, 'quantity': quantity}
                else:
                    return None

            items_list = []
            for line in items_input.strip().splitlines():
                parsed = parse_item(line)
                if parsed:
                    items_list.append(parsed)

            spins = count

            items_list_sorted = sorted(items_list, key=lambda x: x['chance'])

            results = {}

            for _ in range(spins):
                rand_num = random.uniform(0, 100)
                selected_items = {}
                selected_item = None
                duplicates = {}
                for item in items_list_sorted:
                    if rand_num <= item['chance']:
                        for duplicate in items_list_sorted:
                            if duplicate['rarity'] == item['rarity'] and duplicate['chance'] == item['chance']:
                                k = (duplicate['chance'], duplicate['rarity'], duplicate['name'], duplicate['quantity'])
                                if k in duplicates:
                                    duplicates[k] += 1
                                else:
                                    duplicates[k] = 1
                        random_item_list = list(duplicates.keys())
                        selected_item = random.choice(random_item_list)
                        remove_parentheses = str(selected_item).replace('(','').replace(')','')
                        remove_other = remove_parentheses.replace("'", "")
                        arr = remove_other.split(', ')
                        selected_items.update(({'chance': float(arr[0]), 'rarity': arr[1], 'name': arr[2], 'quantity': int(arr[3])}))
                        break
                if selected_item:
                    key = (selected_items['rarity'], selected_items['name'])
                    if key in results:
                        results[key] += selected_items['quantity']
                    else:
                        results[key] = 1 * selected_items['quantity']

            print(f"---------------------------------------------------")
            for (rarity, name), count in results.items():

                pre = f"{name} x{count}"
                print(f"{self.Console.Colored(f'| {rarity}', rarity)}: {self.Console.Colored(pre, 0)}")
            print(f"--------------------------------------------------- OPENED: {spins} \n")
        RandomItem(count=int(count))

class ConsoleTemplate:

    def __init__(self):
        self.mod = []
        self.commandListInfo = "• Структура ключей листа: «название файла листа» «количество»\n• Очистить консоль: cls\n"
        self.keyShortCutList = {}
        self.firstOutContent = "Инструмент быстрых действий (частное использование). \nПосмотреть все команды: help. \nКоманды писать раздельно пробелом! \nv1.0.0\n"

    #Outs colorized text to console
    #text: string, color: string | int, printable: print to console
    def Colored(self, text: str, color, printable=False):
        out = ""

        if color == "white" or color == 0:
            out = "\033[0;37m{}".format(text)

        if color == "gray" or color == "common" or color == 1:
            out = str(("\033[1;30m{}".format(text)) + ("\033[0;37m{}".format("")))

        if color == "green" or color == "uncommon" or color == 2:
            out = str(("\033[1;32m{}".format(text)) + ("\033[0;37m{}".format("")))

        if color == "blue" or color == "rare" or color == 3:
            out = str(("\033[1;34m{}".format(text)) + ("\033[0;37m{}".format("")))

        if color == "purple" or color == "epic" or color == 4:
            out = str(("\033[1;35m{}".format(text)) + ("\033[0;37m{}".format("")))

        if color == "yellow" or color == "legendary" or color == 5:
            out = str(("\033[0;33m{}".format(text)) + ("\033[0;37m{}".format("")))
        
        if color == "red" or color == "exotic" or color == 6:
            out = str(("\033[1;31m{}".format(text)) + ("\033[0;37m{}".format("")))

        if printable: print(out)
        return out
    
    def UnpackDatas(self, current="all", argument=None):

        #Directory name
        currentDir = pathlib.Path(__file__).parent

        if current == "fileKeyNames" or current == "all":
            keyList = []
            
            for file in pathlib.Path(f"{currentDir}/lists").glob('*.txt'):
                if file.is_file():
                    keyList.append(file.name)
            return keyList

        if current == "itemsListFiles" or current == "all":
            itemlistList = []

            try:
                if not pathlib.Path(f"{currentDir}/lists").exists() or len(list(pathlib.Path(f"{currentDir}/lists").glob("*.txt"))) < 1:
                    raise FileNotFoundError

                for file in pathlib.Path(f"{currentDir}/lists").glob('*.txt'):
                    if file.is_file():
                        itemlistList.append(file.name)
            except FileNotFoundError:
                self.Colored("Папка «lists» не найдена, или она пуста.", "red", True)
            else:
                return itemlistList
        
        if current == "keyShortCuts" or current == "all":
            try:
                with open("key_shortCuts.json", 'r', encoding='utf-8') as file:
                    self.keyShortCutList = json.load(file)
            except FileNotFoundError:
                self.Colored(f"Файл «key_shortCuts.json» не найден.", "yellow", True)

        if current == "keyListRunner" or current == "all":
            keyListRunner = []

            if len(argument) > 0:
                for i in argument:
                    keyListRunner.append(str(i).split('.')[0])
            return keyListRunner

    #Copies content into clipboard
    def Copy(self, content):
        command = 'echo | set /p nul=' + content.strip() + '| clip'
        os.system(command)

    #Return TRUE, if text = content of element from list[index], else: returns FALSE
    def Is(self, text="", shortCutted=True, indexator=0, rule=[None, None]):
        userContent = self.mod[indexator]

        if rule == [None, None]:
            if len(self.mod) > 0 and len(self.mod) >= indexator:
                if userContent == text or (userContent == self.keyShortCutList.get(text) and shortCutted):
                    return True
        
        elif rule[0] == "key":
            if userContent in rule[1]:
                return True
        
        return False
    
    def GetUserInput(self, position=0):
        return self.mod[position]
        


###################################################################################################


#First out on program start
C = ConsoleTemplate()
Rand = TheRandomizer()
def Start():
    C.UnpackDatas("keyShortCuts")
    Rand.keyList = C.UnpackDatas("fileKeyNames")
    Rand.itemlistList = C.UnpackDatas("itemsListFiles")
    Rand.keyListRunner = C.UnpackDatas("keyListRunner", Rand.itemlistList)

    print(ConsoleTemplate().firstOutContent)

Start()

while True:

    userInputContent = input("> ")
    C.mod = userInputContent.split(' ')

    ############################################

    #Cleane console
    if C.Is("cls"):
        os.system('cls')
        Start()

    #Help
    if C.Is("help"):
        print(C.commandListInfo)

    #Showkeys
    if C.Is("showkeys"):
        print(*[f"{_}\n" for _ in Rand.keyList])

    #Run keys
    if C.Is(rule=["key", Rand.keyListRunner]):
        Rand.PushRandom(f"{C.GetUserInput()}.txt", C.GetUserInput(1))
