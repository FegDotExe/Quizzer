from os import path, write
from json import load, dumps
from random import randint,choice
from IPython.display import display, Latex, clear_output, Markdown
from datetime import datetime
from math import ceil

DIRECTORY = path.dirname(path.abspath(__file__))+"/"

COMPLETEPOOL=0
MOSTDIFFICULT=1
UNANSWERED=2
SMART=3

RANDOM=0
ORDERED=1

def jread(file) -> dict:
    """Legge un file json e ritorna il dizionario corrispondente. Il nome deve essere fornito con path relativo rispetto al file py e senza estensione"""
    with open(DIRECTORY+file+".json",encoding="utf-8") as temp_file:
        data=load(temp_file)
    return data
def jwrite(file,data):
    with open(DIRECTORY+file+".json","w") as fail:
        fail.write(dumps(data,indent=4))
        fail.close

class TestClass():
    """Rapresents a test"""
    def __init__(self,fileName:str,mode=COMPLETEPOOL) -> None:
        """Loads a test at given filename"""
        self.fileName=fileName
        self.data=jread(fileName)

        if self.data["type"]=="override":
            tempdata=jread(self.data["source"])
            for key in tempdata:
                if key not in ["type","source","stats"]:
                    if key not in self.data:
                        self.data[key]=tempdata[key]

        if self.data["type"] not in ["test","override"]:
            raise Exception("The given file is not a test")

        self.asked=0#How many questions have been asked

        self.results={"total":self.data["questions"],"right":0,"rightQuestions":[],"wrongQuestions":[]}

        self.questions=[]
        if mode==COMPLETEPOOL:
            self.questions=self.compileCompletePool()
        elif mode==MOSTDIFFICULT:
            self.questions=self.compileDifficultPool()
        elif mode==UNANSWERED:
            self.questions=self.compileUnansweredPool()
        elif mode==SMART:
            finalPool=[]
            completePool=self.compileCompletePool()
            unansweredPool=self.compileUnansweredPool()
            difficultPool=self.compileDifficultPool()

            amountWithoutAnswer=ceil((self.data["questions"]*len(unansweredPool))/len(completePool))
            for i in range(0,amountWithoutAnswer):
                element=choice(unansweredPool)
                unansweredPool.remove(element)
                try:
                    completePool.remove(element)
                except:
                    pass
                finalPool.append(element)
            
            #print(finalPool)

            difficultAmount=(self.data["questions"]-len(finalPool))//2
            
            for i in range(0,difficultAmount):
                element=choice(difficultPool)
                difficultPool.remove(element)
                try:
                    completePool.remove(element)
                except:
                    pass
                finalPool.append(element)
            
            leftAmount=self.data["questions"]-len(finalPool)
            for i in range(0,leftAmount):
                element=choice(completePool)
                completePool.remove(element)
                finalPool.append(element)

            self.questions=finalPool

    def compileCompletePool(self)->list:
        """Compiles a list with the complete pool of questions"""
        outputList=[]

        for questionFile in self.data["questionPool"]:#Loads all questions in self.questions
                questionFile=jread(questionFile)
                if questionFile["type"]=="questionList":
                    for question in questionFile["questionList"]:
                        outputList.append(question)
        return outputList
    def compileDifficultPool(self,limit=True)->list:
        """Compiles a list with a pool of the most difficult questions"""
        tempquestions=[]
        i=0
        for questionFile in self.data["questionPool"]:
            questionFile=jread(questionFile)
            if questionFile["type"]=="questionList":
                for question in questionFile["questionList"]:
                    tempquestion=question["q"]
                    if tempquestion in self.data["stats"]:
                        """if len(tempquestions)==0:
                            tempquestions.append(question)
                        elif ((self.data["stats"][tempquestion]["right"]*100)/self.data["stats"][tempquestions[len(tempquestions)-1]["q"]]["asked"])<=((self.data["stats"][tempquestions[len(tempquestions)-1]["q"]]["right"]*100)/self.data["stats"][tempquestions[len(tempquestions)-1]["q"]]["asked"]):
                            tempquestions.insert(0,question)
                        else:
                            tempquestions.append(question)"""
                        #tempquestions.append(((self.data["stats"][tempquestion]["right"]*100)/self.data["stats"][tempquestion]["asked"],question))
                        tempquestions=self.insertByValue(tempquestions,{"value":(self.data["stats"][tempquestion]["right"]*100)/self.data["stats"][tempquestion]["asked"], "question":question})
                        i=i+1
        output=[]
        if len(tempquestions)>0:#Prevents errors when no questions have been answered
            if limit:
                for i in range(0,self.data["questions"]):
                    output.append(tempquestions[i]["question"])
            else:
                for element in tempquestions:
                    output.append(element["question"])

        return output
    def compileUnansweredPool(self)->list:
        outputList=[]
        for questionFile in self.data["questionPool"]:
            questionFile=jread(questionFile)
            if questionFile["type"]=="questionList":
                for question in questionFile["questionList"]:
                    if question["q"] not in self.data["stats"]:
                        outputList.append(question)
        return outputList

    def insertByValue(self,list,element):
        #TODO: maybe this one function should be internal in compileDifficultPool()
        if len(list)==0:
            list.append(element)
        else:
            i=0
            while i<len(list):
                if i!=len(list)-1:
                    if element["value"]<list[i]["value"]:
                        list.insert(i,element)
                        break
                else:
                    list.append(element)
                    break
                i+=1
        return list

    def getUniqueQuestion(self,mode=RANDOM):
        """Returns a question which has not been extracted yet and proceeds to remove it from self.questions"""
        if self.asked<self.data["questions"]:
            if len(self.questions)>0:
                #Displays question
                if mode==RANDOM:
                    index=randint(0,len(self.questions)-1)
                elif mode==ORDERED:
                    index=0
                else:
                    index=0
                output=self.questions[index]
                del(self.questions[index])
                display(Markdown(output["q"]))

                #Waits for input and shows answer
                input(self.data["waitMessage"])
                display(Markdown(output["a"]))

                #Gets if answer was correct
                correct=" "
                while correct not in ["y","n","","Y","N"]:
                    correct=input(self.data["askCorrect"])

                clear_output()#Clears output

                #Upgrades stats
                if output["q"] not in self.data["stats"]:
                    self.data["stats"][output["q"]]={"asked":0,"right":0}

                self.data["stats"][output["q"]]["asked"]+=1

                if correct in ["y","Y"]:
                    self.data["stats"][output["q"]]["right"]+=1
                    self.results["right"]+=1
                    self.results["rightQuestions"].append(output)
                else:
                    self.results["wrongQuestions"].append(output)

                jwrite(self.fileName,self.data)
                self.asked+=1
            else:
                return 0
        else:
            return 0

    def elaborateResults(self,export=True):
        """Show results with ipython display and eventually export them to file"""
        if export:
            nowTime=datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            fileOutput=""

        clear_output()

        firstLine="{right}/{total} - {percent}%".format(right=self.results["right"],total=self.results["total"],percent=(100*self.results["right"])/self.results["total"])

        display(Latex(firstLine))

        rightTitle="# {title}".format(title=self.data["right"])
        display(Markdown(rightTitle))
        if export:
            fileOutput=firstLine+"\n"+rightTitle+"\n"

        for rightAnswer in self.results["rightQuestions"]:
            output="## "+rightAnswer["q"]
            output=output+"\n\n"+self.data["answer"]+" " + rightAnswer["a"]

            output=output+"\n\n"+self.data["statsGiven"]+" "+str(self.data["stats"][rightAnswer["q"]]["right"])+"/"+str(self.data["stats"][rightAnswer["q"]]["asked"])+" - {percent}%".format(percent=(100*self.data["stats"][rightAnswer["q"]]["right"])/self.data["stats"][rightAnswer["q"]]["asked"])

            if export:
                fileOutput=fileOutput+output+"\n"
            display(Markdown(output))


        wrongTitle="# "+self.data["wrong"]
        display(Markdown(wrongTitle))
        if export:
            fileOutput=fileOutput+"\n"+wrongTitle+"\n"

        for wrongAnswer in self.results["wrongQuestions"]:
            output="## "+wrongAnswer["q"]
            output=output+"\n\n"+self.data["answer"]+" " + wrongAnswer["a"]

            output=output+"\n\n"+self.data["statsGiven"]+" "+str(self.data["stats"][wrongAnswer["q"]]["right"])+"/"+str(self.data["stats"][wrongAnswer["q"]]["asked"])+" - {percent}%".format(percent=(100*self.data["stats"][wrongAnswer["q"]]["right"])/self.data["stats"][wrongAnswer["q"]]["asked"])

            display(Markdown(output))
            if export:
                fileOutput=fileOutput+output+"\n"

        if export:
            writeFile=open("exports/"+str(nowTime)+".md","w")
            writeFile.write(fileOutput)
            writeFile.close()
    def elaborateDifficult(self,export=True):
        """Show answer in difficulty order with ipython display and eventually export them to file"""
        difficultList=self.compileDifficultPool(limit=False)
        if export:
            nowTime=datetime.now().strftime("D - %Y-%m-%d %H-%M-%S")
            fileOutput=""

        clear_output()

        for question in difficultList:
            output="## "+question["q"]
            output=output+"\n\n"+self.data["answer"]+" " + question["a"]

            output=output+"\n\n"+self.data["statsGiven"]+" "+str(self.data["stats"][question["q"]]["right"])+"/"+str(self.data["stats"][question["q"]]["asked"])+" - {percent}%".format(percent=(100*self.data["stats"][question["q"]]["right"])/self.data["stats"][question["q"]]["asked"])

            if export:
                fileOutput=fileOutput+output+"\n"
            display(Markdown(output))

        if export:
            writeFile=open("exports/"+str(nowTime)+".md","w")
            writeFile.write(fileOutput)
            writeFile.close()

    def clearStats(self):
        """Clears stats for loaded quiz"""
        self.data["stats"]={}
        jwrite(self.fileName,self.data)

#TODO: make a function for SMART pooling
#TODO: add option for non-random questions
#TODO: add option to express percent of difficult questions