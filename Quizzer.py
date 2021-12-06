from os import path, write
from json import load, dumps
from random import randint
from IPython.display import display, Latex, clear_output, Markdown
from datetime import datetime

DIRECTORY = path.dirname(path.abspath(__file__))+"/"

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
    def __init__(self,fileName:str) -> None:
        """Loads a test at given filename"""
        self.fileName=fileName
        self.data=jread(fileName)

        self.asked=0#How many questions have been asked

        self.results={"total":self.data["questions"],"right":0,"rightQuestions":[],"wrongQuestions":[]}

        if self.data["type"]!="test":
            raise Exception("The given file is not a test")

        self.questions=[]
        for questionFile in self.data["questionPool"]:#Loads all questions in self.questions
            questionFile=jread(questionFile)
            if questionFile["type"]=="questionList":
                for question in questionFile["questionList"]:
                    self.questions.append(question)

    def getUniqueQuestion(self):
        """Returns a question which has not been extracted yet and proceeds to remove it from self.questions"""
        if self.asked<self.data["questions"]:
            if len(self.questions)>0:
                #Displays question
                index=randint(0,len(self.questions)-1)
                output=self.questions[index]
                del(self.questions[index])
                display(Latex(output["q"]))

                #Waits for input and shows answer
                input(self.data["waitMessage"])
                display(Latex(output["a"]))

                #Gets if answer was correct
                correct=" "
                while correct not in ["y","n",""]:
                    correct=input(self.data["askCorrect"])

                clear_output()#Clears output

                #Upgrades stats
                if output["q"] not in self.data["stats"]:
                    self.data["stats"][output["q"]]={"asked":0,"right":0}

                self.data["stats"][output["q"]]["asked"]+=1

                if correct=="y":
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
        """Show results with ipython display"""
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
    def clearStats(self):
        """Clears stats for loaded quiz"""
        self.data["stats"]={}
        jwrite(self.fileName,self.data)