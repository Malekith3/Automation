from pathlib import Path
from itertools import islice
from datetime import datetime

def FindNumOfFiles(myFile):
    fileContent = myfile.readline()
    while fileContent.find("Total    Copied") == -1:
        fileContent = myfile.readline()
    for line in islice(myfile, 0, 1):
        fileContent = myfile.readline().split("   ")
    print(f'There is {fileContent[3]} files')
################################################################################
def ReadingNotStandartTime(fileContent):
    fileContent = fileContent.split("displayDate = ")
    fileContent = fileContent[1].rsplit(" ")
    fileContent = fileContent[3].split(":")
    time_in_minutes = float(fileContent[0]) * 60 + float(fileContent[1]) + float(fileContent[2]) / 60
    return time_in_minutes

#################################################################################
def RedingStandartTime(fileContent):
    fileContent = fileContent.split("INFO")
    time = fileContent[0].rsplit(" ")
    return datetime.fromisoformat(time[0] + " " + time[1])

def InLineFunc(flag,myfile):

    fileContent = myfile.readline()
    while fileContent.find(flag) == -1:
        fileContent = myfile.readline()

    if flag != "EsmaUpdaterService End":
        return ReadingNotStandartTime(fileContent)
    else:
        return RedingStandartTime(fileContent)
#################################################################################

def TakingPath():
    path_to_file = input()
    path_to_file = path_to_file.replace("\\", "\\\\")
    file_name = input("please enter file name")
    file_name+= '.txt'
    return Path(path_to_file,file_name)

################################################################################

def CalculateTime(start_proccess, end_process,info=None):
    if info == "Corrections" or info == "Validator":
        result = (end_process - start_proccess)
        print(f'{info} : {result}')
        return result
    else:
        result = (end_process - start_proccess).total_seconds()/60
        print(f'{info} : {result}')
        return result

#################################################################################

def AfterFunc(flag,myfile):

    fileContent = myfile.readline()
    while fileContent.find(flag) == -1:
        fileContent = myfile.readline()
    if flag != "correct fields 00040 and 00060" and flag!= "Validate unicost data":
        for line in islice(myfile, 9, 10):
            fileContent = myfile.readline().split("INFO")
            time = fileContent[0].rsplit(" ")
            return datetime.fromisoformat(time[0] + " " + time[1])
    elif flag ==  "Validate unicost data" :
        for line in islice(myfile, 9, 10):
            fileContent = myfile.readline().split(" ")
        fileContent = fileContent[0].split(":")
        return float(fileContent[0]) * 60 + float(fileContent[1]) + float(fileContent[2]) / 60

    else :
        for line in islice(myfile, 2, 3):
            fileContent = myfile.readline()
            return ReadingNotStandartTime(fileContent)



#################################################################################

def BeforeFunc(flag,myfile ,not_standart_reading = False):
    prev_line = myfile.readline()
    current_line = myfile.readline()

    while True:
        if current_line.find(flag)!=-1 :
            break
        prev_line = myfile.readline()

        if prev_line.find(flag)!=-1 :
            break
        current_line = myfile.readline()

    if (current_line.find(flag) == -1):

        if  not_standart_reading:
            return ReadingNotStandartTime(current_line)
        else:
            return RedingStandartTime(current_line)

    else:
        if not_standart_reading:
            return ReadingNotStandartTime(prev_line)
        else :
            return RedingStandartTime(prev_line)

##################################################################################


if __name__ == "__main__":
    print("Please enter path to SwedBank log File")
    path_to_swed = TakingPath()
    print("Please enter path to Handels log File")
    path_to_handels = TakingPath()
    print("*" * 20 + "SweedBank" + "*"*20)
    with open(path_to_swed , "r") as myfile:
            FindNumOfFiles(myfile)
            CalculateTime(AfterFunc("Populate unicost tables hub", myfile),BeforeFunc("Remove duplicates for scores",myfile) , info='Deltas to Hub')
            CalculateTime(AfterFunc("correct fields 00040 and 00060", myfile),InLineFunc("general_corrections.xml has finished running",myfile) , info='Corrections')
            CalculateTime(AfterFunc("Populate unicost tables local", myfile), BeforeFunc("Performance script", myfile) , info= 'Deltas to Local')
            CalculateTime(AfterFunc("Validate unicost data", myfile), BeforeFunc("Export from unicost", myfile ,not_standart_reading= True ),info='Validator')
            myfile.seek(0)
            CalculateTime(AfterFunc("Export from unicost", myfile), BeforeFunc("move files from output to backup", myfile) , info = 'Export EMT')
            CalculateTime(AfterFunc("Load metadata", myfile),InLineFunc("EsmaUpdaterService End", myfile), info='ESMA')
    print("*" * 20 + "Handels" + "*"*20)
    with open(path_to_handels, "r") as myfile:
            FindNumOfFiles(myfile)
            CalculateTime(AfterFunc("Populate unicost tables hub", myfile),BeforeFunc("Remove duplicates for scores", myfile), info='Deltas to Hub')
            CalculateTime(AfterFunc("Populate unicost tables local", myfile), BeforeFunc("Performance script", myfile), info='Deltas to Local')
            CalculateTime(AfterFunc("Validate unicost data", myfile), BeforeFunc("move files from output to backup", myfile,not_standart_reading=True ), info='Validator')
            myfile.seek(0)
            CalculateTime(AfterFunc("Export from unicost", myfile),BeforeFunc("Populate unicost tables local", myfile), info='Export EMT')