import docx
import time
import math
import json
import os
from os import listdir
from os.path import isfile, join
from random import shuffle

# to make this file run make sure to download the file dependencies (the imports)

#initialize some important global variables that will be used for semantic analysis of the text
subjectList = ['Biology','Math','Physics','Chemistry','Earth and Space']
questionType = ['Multiple Choice', 'Short Answer']


#Check cache in direcotory -> Save current indexes of files
#G


class qstruct:                          # Question Structure
    def __init__(self):
        self.qtype = 'none'             # TOSS-UP or BONUS
        self.form = 'none'              # MCQ or Short Answer
        self.subtype ='none'            # BIOLOGY, CHEMISTRY ...
        self.qbody ='none'              # What is 2+2?
        self.ansOption = 'none'         # W) 0      X) 1        Y) 2        Z) 3  
        self.answer = 'none'            # ANSWER: 2
        self.level = -1          # difficulty level: 0 -> middle, 1 -> highschool

class question:                         # A question has a TOSS-UP and a BONUS
    def __init__(self):              
        self.tossUp = qstruct()
        self.bonus = qstruct()
        self.bonusSwitch = False

# input question and question number to convert to JSON obj -> Output JSON 
''' 
Format:

ID                      --> QuestionNumber
difficultyLevel         --> 0 for middleSchool, 1 for highschool 
subjectType             --> one from ['Biology','Math','Physics','Chemistry','Earth and Space'] for high school

tossup_question         --> 'What is 2+2?'
tossup_isShortAns       --> False
tossup_MCQoptions       --> W) 1      X) 2        Y) 3        Z) 4 
tossup_answer           --> Z) 4
tossup_imageURL         --> None

bonus_question          
bonus_isShortAns
bonus_MCQoptions
bonus_answer
bonus_image
'''

def outjson(question, QuestionNumber, directory):
    jsonQuestion = {}
    
    if question.tossUp.subtype == 'Earth and Space':
        question.tossUp.subtype = 'Earth_and_Space'

    jsonQuestion['id']                  = QuestionNumber 
    jsonQuestion['difficultyLevel']     = question.tossUp.level 
    jsonQuestion['subjectType']         = question.tossUp.subtype  

    jsonQuestion['tossup_question']     = question.tossUp.qbody
    jsonQuestion['tossup_isShortAns']   = True if (question.tossUp.form == 'Short Answer') else False 
    jsonQuestion['tossup_MCQoptions']   = None if (question.tossUp.ansOption == 'none') else question.tossUp.ansOption 
    jsonQuestion['tossup_answer']       = question.tossUp.answer
    jsonQuestion['tossup_imageURL']     = None
    
    jsonQuestion['bonus_question']      = question.bonus.qbody
    jsonQuestion['bonus_isShortAns']    = True if (question.bonus.form == 'Short Answer') else False 
    jsonQuestion['bonus_MCQoptions']    = None if (question.bonus.ansOption == 'none') else question.bonus.ansOption
    jsonQuestion['bonus_answer']        = question.bonus.answer
    jsonQuestion['bonus_image']         = None

    if 'none' in jsonQuestion.values() or '' in jsonQuestion.values():
        print("Error: 'none' or empty string detected. Skipping question with information\n\t", jsonQuestion)
        return False

    
    # if not os.path.isdir(directory):
    #     print('Making directory ', directory)
    #     os.makedirs(dir)

    filename = question.tossUp.subtype + '_' + str(QuestionNumber) + '.json'
    with open(directory + '/' + filename,'w') as json_file:
        json.dump(jsonQuestion, json_file)
        return True

# remove everything after and including the word answer
def sanitize_ansOption(ansOption):
    lowered = ansOption.lower()
    pos = lowered.find('answer:')
    
    if pos != -1:
        return ansOption[:pos]
    else:
        return ansOption

# remove everything before the word answer
def sanitize_answer(ans):
    lowered = ans.lower()
    pos = lowered.find('answer:')
    
    if pos != -1:
        return ans[pos:]
    else:
        return ans


def chicken():
    print("      __//")
    print("    /.__.\\")
    print("    \\ \\/ /")
    print(" '__/    \\")
    print("  \\-      )")
    print("   \\_____/")
    print("_____|_|____")
    print('     " "')

def byeChicken():
    print("\t\t      __// Bye Bye")
    print("\t\t    /.__.\\")
    print("\t\t    \\ \\/ /")
    print("\t\t '__/    \\")
    print("\t\t  \\-      )")
    print("\t\t   \\_____/")
    print("\t\t_____|_|____")
    print('\t\t     " "')

def main():
    
    print("Please make sure any docx file that will be written to is closed before using this program.")
    chicken()
    # Question list contains all the question objects

    # lists that help categorise questions
    global subjectList
    global questionType


    print("\n============Input Sequence============\n")
    incorrectAns = True
    while incorrectAns:
        try:
            level_sel = int(input("What level are these questions? (input 0 for middleSchool, 1 for highSchool):"))
        except ValueError:
            print("ERROR: Please input integers only.")
            continue

        if level_sel == 0:
            level = 0
            incorrectAns = False
        elif level_sel == 1:
            level = 1
            incorrectAns = False
        else:
            print("Please try again")


    # Array to append all subjects questions
    subjectArrays = {}
    for subject in subjectList:
        subjectArrays[subject] = []
    
    Cache = {}
    directory = './jsonQuestions/' 

    if (level == 0):
        directory += 'middleSchoolQuestions'
    elif (level == 1):
        directory += 'highSchoolQuestions'

    Cache['directory'] = directory

    if os.path.exists(directory+'/0cache.json'):
        with open(directory+'/0cache.json') as f:
            Cache = json.load(f)
    else:
        print("Creating cache...")
        Cache['filesRead'] = []
        for subject in subjectList:
            Cache[subject] = 5 

    if not os.path.exists(directory):
        print("Creating directory", directory)
        os.makedirs(directory)
    
    if not os.path.exists('./questionRepo'):
        print('ERROR: Folder "questionRepo" NOT FOUND.\nCreating folder... please try again after populating the folder with docx files with your questions')
        os.makedirs('./questionRepo')
        return
        

    print("Gobble gobble. Here's what I've found in folder questionRepo:")
    filesInDirectory = []


    for file in listdir('./questionRepo'):
        _, e = os.path.splitext(file)
        if e == ".docx" and file not in Cache['filesRead']:
            filesInDirectory.append(file)
    
    if (len(filesInDirectory) == 0):
        print("No new questions found, files already read include:",Cache['filesRead'])
        print("If you think this is an error, please delete 0Cache.json")
        print("WARNING: Action will reset indexes")
        return
    
    for i, file in enumerate(filesInDirectory):
        print(i,": ", file)
    
        incorrectAns = True
        while incorrectAns:
            try:
                ch_dir = int(input("Please input the number of the file you want me to eat (select index) OR input -1 to move to next sequnce: "))
                if ch_dir == -1:
                    break

                input_filename = filesInDirectory[ch_dir]

                if input_filename in Cache['filesRead']:
                    print("WARNING: You've already read this file.")
                    ch = input("Are you sure you want to continue? Input 'y' if you really want to do this:")
                    if ch == 'y' or ch == 'Y':
                        print("That's not weird at all.")
                        incorrectAns = False
                    else:
                        print("trying again")
                else:
                    incorrectAns = False
                        
            except IndexError:
                print("ERROR: Please select the an in range index.")
                continue
            except ValueError:
                print("ERROR: Please input integers only.")
                continue
            
            if ch_dir == -1:
                break
            
            Cache['filesRead'].append(input_filename)
        
    


    inDoc = docx.Document('./questionRepo/' + input_filename)
    
    tossUpEncounter = False
    
    # mcqflag = False

    for _, para in enumerate(inDoc.paragraphs):
        txt = para.text

        if 'TOSS-UP' in txt:                #  signals the start of a new question
            demo = question()
            tossUpEncounter = True           
            demo.tossUp.qtype = txt
            demo.tossUp.level = level

        if tossUpEncounter == False:
            continue
        
        elif 'BONUS' in txt:                #   initiates making bonus
            demo.bonusSwitch = True
            demo.bonus.qtype = txt
            demo.bonus.level = level

        if not demo.bonusSwitch:            #  tossUp question
            
            if 'W)' in txt and 'X)' in txt:
                demo.tossUp.ansOption = sanitize_ansOption(txt)
                #continue
            if 'ANSWER' in txt:
                demo.tossUp.answer = sanitize_answer(txt)
                #continue
            for _, sub in enumerate(subjectList):
                if sub.lower() in txt.lower():
                    demo.tossUp.subtype = sub
                    break
            for _, ques in enumerate(questionType):
                if ques.lower() in txt.lower():
                    demo.tossUp.form = ques

                    body = txt
                    body = body.replace(demo.tossUp.subtype,'', 1)
                    body = body.replace(ques,'',1)

                    demo.tossUp.qbody = body
                    break

        else:
            if 'W)' in txt and 'X)' in txt:
                demo.bonus.ansOption = sanitize_ansOption(txt)
                
            if 'ANSWER' in txt:
                demo.bonus.answer = sanitize_answer(txt)
                
                #add question to appropriate Array
                subjectArrays[demo.tossUp.subtype].append(demo)

                #continue
            for _, sub in enumerate(subjectList):
                if sub.lower() in txt.lower():
                    demo.bonus.subtype = sub
                    #print("subject found", sub)
                    break
            for _, ques in enumerate(questionType):
                if ques.lower() in txt.lower():
                    demo.bonus.form = ques
                    #print("form found", ques)

                    body = txt
                    body = body.replace(demo.bonus.subtype,'')
                    body = body.replace(ques,'')

                    demo.bonus.qbody = body
                    #print("body found", body)
                    break
    
    print("Before Output")
    total = 0
    afterCount = {}
    for subject in subjectList:
        numberofquestions = len(subjectArrays[subject])
        print("\t",subject,":", numberofquestions)
        afterCount[subject] = 0
        total += numberofquestions

    print("Total found ", total)
    


    #output to JSON while any question remain
    
    loop = True
    while loop:
        loop = False
        for subject in subjectList:
            if (subjectArrays[subject]):
                loop = True
                Cache[subject] += 1
                afterCount[subject] += 1
                if not (outjson(subjectArrays[subject].pop(), Cache[subject], directory)):
                    Cache[subject] -= 1
                    afterCount[subject] -= 1

        if loop == False:
            break



    total = 0
    print("\nAfter Output: ")
    for subject in subjectList:
        numberofquestions = afterCount[subject]
        print("\t",subject,":", numberofquestions)
        total += numberofquestions
    print("Total used ", total)

    print("\nSubject Indexes at: ")
    for subject in subjectList:
        numberofquestions = Cache[subject]
        print("\t",subject,"at", numberofquestions)


    # Save for later 
    with open(directory+'/0cache.json','w') as json_file:
        print("Saving Output in Cache")
        json.dump(Cache,json_file)
        
          
main()
