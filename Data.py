import csv
import re
import matplotlib.pyplot as plt


class DataSet:
    LengthCsv = 99
    Length = 98
    StartTweetsCsv = 48
    StartTweets = 47
    DuplicatesStart = 88
    

    def __init__(self,filename,size):
        super().__init__()
        self.filename = filename
        self.Groupsize=size
        self.NGramValues=dict()
        self.TweetValues=dict()
        self.UserAvgSelfAgreement =[]
        self.GroupAvgSelfAgreement=0
        self.GroupAvgInterAgreement=0
        self.Headers = []
        self.UserAvgInterAgreement = []
        self.Selfagreement=[[0 for x in range(5)] for y in range(4)]
        self.Matrix = [[0 for x in range(4)] for y in range(98)]
        self.InterAgreement=[[0 for x in range(98)] for y in range(4)]
        self.libAccuracy = 0
        self.oldLibAccuracy = 0
        self.InterReliability=0



    #seperates string by spaces
    def Tokenize(self,string):
        return string.split(" ")

    #strinps strings of non alphanumerics, not including spaces
    def Strip(self,string):
        return ''.join(e for e in string if e.isalnum() or e==" " or e=='@')

    #gets the sentiment value of the word on the line given
    def findValue(self,string)-> int:
        return int(string[0:len(string)-1].split('\t')[1])
        
    #Looks for exact strings in a line
    def contains(self,word,line):
        temp = line[0:len(line)-3].split("\t")[0]
        # temp = re.findall("\\b"+word+"\\b",line)
        if temp == word:
            return True
        else:
            return False

    #gets the value of a given word by searching the afinn 111 text document
    def getValue(self,string) -> int:
        AFINN = open("AFINN-111.txt", "r")
        for line in AFINN:
            if self.contains(string,line):
                return self.findValue(line)
        AFINN.close()
        return 0
    #analyses the sentiment value of a given sentence. First pulls out n-grams and adds their values then goes through each individual word adding theirs.
    def analyze(self,string):
        standard_value=0
        count=0
        myvalue = 0
        string = self.Strip(string).lower()
        for key in self.NGramValues:
            if key in string:
                keylen = len(self.Tokenize(key))
                string = string.replace(key,'')
                myvalue+=(self.NGramValues[key]*keylen)
                count+=(1*keylen)
                # output[key]=(self.NGramValues[key]*keylen)
        string = self.Tokenize(string)
        for i in string:
            if(i.isalpha()):
                standard_value += self.getValue(i)
                # output[i]=self.getValue(i)
                count+=1
        return (myvalue+standard_value)/count

    def analyzeOLD(self,string):
        standard_value=0
        count=0
        string = self.Strip(string).lower()
        string=self.Tokenize(string)
        for i in string:
            if(i.isalpha()):
                standard_value += self.getValue(i)
                count+=1
        return standard_value/count

    def createlib(self):
        sum=0
        count=0
        avg =0
        start = False
        currstring = ""
        with open(self.filename, newline='',encoding="UTF-8") as f:
            reader = csv.reader(f,dialect='excel')
            for i in range(1,self.StartTweetsCsv):
                sum=0
                count=0
                start = False
                f.seek(0)
                for row in reader:
                    if start:
                        if(row[i]=="Very Negative"):
                            sum+=-5
                            self.Matrix[i-1][count]=-5
                        if(row[i]=="Negative"):
                            sum+=-2.5
                            self.Matrix[i-1][count]=-2.5
                        if(row[i]=="Positive"):
                            sum+=2.5
                            self.Matrix[i-1][count]=2.5
                        if(row[i]=="Very Positive"):
                            sum+=5
                            self.Matrix[i-1][count]=5
                        count+=1
                    else:
                        currstring=self.Strip(row[i]).lower()
                        self.Headers.append(currstring)
                        start = True
                avg=sum/count
                self.NGramValues[currstring]=avg
        self.createTweets()     

    def createTweets(self):
        sum=0
        count=0
        avg =0
        start = False
        currstring = ""
        with open(self.filename, newline='',encoding="UTF-8") as f:
            reader = csv.reader(f,dialect='excel')
            for i in range(self.StartTweetsCsv,self.Length):
                sum=0
                count=0
                start = False
                f.seek(0)
                for row in reader:
                    if start:
                        if(row[i]=="Very Negative"):
                            sum+=-5
                            self.Matrix[i-1][count]= -5
                        if(row[i]=="Negative"):
                            sum+=-2.5
                            self.Matrix[i-1][count]= -2.5
                        if(row[i]=="Positive"):
                            sum+=2.5
                            self.Matrix[i-1][count]=2.5
                        if(row[i]=="Very Positive"):
                            sum+=5
                            self.Matrix[i-1][count]=5
                        count+=1
                        
                    else:
                        currstring=self.Strip(row[i]).lower()
                        self.Headers.append(currstring)
                        start = True
                if(i<89):
                    avg=sum/count
                    self.TweetValues[currstring]=avg
        
        for k in range(self.DuplicatesStart,self.Length-1,2):
            sum = 0
            count = 0
            for i in range(0,len(self.Matrix[0])):
                sum+=(self.Matrix[k][i]+self.Matrix[k+1][i])/2
                count+=1
            self.TweetValues[self.Headers[k]]=sum/count
        self.calcSelfAgreement()

    def calcSelfAgreement(self):
        col=0
        for k in range(0,len(self.Matrix[0])):
            row=0
            for i in range(self.DuplicatesStart,self.Length-1,2):
                # print(self.Headers[i])
                agreement = 1-(abs(self.Matrix[i][k]-self.Matrix[i+1][k])/10)
                self.Selfagreement[col][row] = agreement
                row+=1
            col+=1
        for collumn in range(0,len(self.Selfagreement)):
            total=0
            count=0
            for row in range(0,len(self.Selfagreement[0])):
                total+=self.Selfagreement[collumn][row]
                count+=1
            self.UserAvgSelfAgreement.append(total/count)
        for x in self.UserAvgSelfAgreement:
            self.GroupAvgSelfAgreement+=x
        self.GroupAvgSelfAgreement=self.GroupAvgSelfAgreement/len(self.UserAvgSelfAgreement)
        self.calcInterAgreement()

    def calcInterAgreement(self):
        for person in range(0,len(self.Matrix[0])):
            dummyanswer=0
            for answer in range(0,len(self.Matrix)-1):
                
                useranswer = self.Matrix[answer][person]
                if(answer<self.StartTweets):
                    difference = useranswer-(((self.NGramValues.get(self.Headers[answer])*self.Groupsize)-useranswer)/(self.Groupsize-1))
                if(answer>=self.StartTweets and answer < self.DuplicatesStart):
                    difference = useranswer-(((self.TweetValues.get(self.Headers[answer])*self.Groupsize)-useranswer)/(self.Groupsize-1))
                if(answer>=self.DuplicatesStart):
                    useranswer= ((self.Matrix[answer][person]+self.Matrix[answer+1][person])/2)
                    difference = useranswer-(((self.TweetValues.get(self.Headers[dummyanswer])*self.Groupsize)-useranswer)/(self.Groupsize-1))
                    answer+=1

                
                self.InterAgreement[person][dummyanswer]=1-(abs(difference)/10)
                dummyanswer+=1
        for person in range(len(self.InterAgreement)):
            sum=0
            count=0
            for values in range(len(self.InterAgreement[0])):
                sum+=self.InterAgreement[person][values]
                count+=1
            self.UserAvgInterAgreement.append(sum/count)
        for x in self.UserAvgInterAgreement:
            self.GroupAvgInterAgreement+=x
        self.GroupAvgInterAgreement=self.GroupAvgInterAgreement/len(self.UserAvgInterAgreement)
        self.CalcInterReliability()

    def CalcInterReliability(self):
        answer =0
        for question in range(len(self.Matrix)):
            sum = 0
            for score in range(len(self.Matrix[question])):
                for score2 in range(score+1,len(self.Matrix[question])):    
                    if(self.Matrix[question][score]==self.Matrix[question][score2]):
                        sum+=1
            # print(sum/self.Summation(len(self.Matrix[question])))
            answer += sum/self.Summation(len(self.Matrix[question]))     
        answer = answer/len(self.Matrix)
        self.InterReliability = answer

    def Summation(self,n):
        answer = 0
        for x in range(n):
            answer+=x
        return answer

def Test(g1,g2):
    OldScoreCorrectCount=0
    NewScoreCorrectCount=0
    for CurrentTweet in g2.TweetValues.keys() :
        CurrentTweetScore = g2.TweetValues.get(CurrentTweet)
        # print(CurrentTweet)
        NewScore = g1.analyze(CurrentTweet)
        OldScore = g1.analyzeOLD(CurrentTweet)
        NewScoreCorrectCount += analyzeScore(NewScore,CurrentTweetScore)
        OldScoreCorrectCount += analyzeScore(OldScore,CurrentTweetScore)
    self.libAccuracy = NewScoreCorrectCount/len(g2.TweetValues)*100
    self.oldLibAccuracy = OldScoreCorrectCount/len(g2.TweetValues)*100
    

def analyzeScore(Score,TweetScore):
    if(Score==0 and TweetScore==0):
        return 1
    if(Score>0 and TweetScore>0):
        return 1
    if(TweetScore<0 and Score<0):
        return 1
    else:
        return 0

Group1 = DataSet("ResponseDataG1.csv",4)
Group1.createlib()

Group2 = DataSet("ResponseDataG2.csv",4)
Group2.createlib()

# while(1):
#     compareortest = input("Compare Libraries or test one, type both or one")
#     if(compareortest=="both"):
#         while(1):
#             graph = input("Pick an x axis Self-Agreement: SA, Inter-Agreement: IA, or InterReliability: IR, or . to go back")
#             if(graph=="."):
#                 break
#             if(graph=="SA"):
#                 plt.
#             # if(graph=="IA"):
            
#             # if(graph=="IR"):

#     if(compareortest=="one"):
#         while(1):
#             library = input("Pick a library to test G1 or G2 or . to go back: ")
#             if(input=="."):
#                 break
#             else:
#                 while(1):
#                     command = input("Pick a following ")

    
    # testtype = input("Pick a ")
# print("Headers")
# print(Group1.Headers)
# print("Matrix")
# print(Group1.Matrix)
# print("Ngram dictionary")
# print(Group1.NGramValues)
# print("Tweet Dictionary")
# print(Group1.TweetValues)
# print("Self Agreements")
#  print(Group1.Selfagreement)
# print("Avg Self Agreements")
# print(Group1.UserAvgSelfAgreement)
# print(Group1.GroupAvgSelfAgreement)
# print("Interagreements")
print(Group1.GroupAvgInterAgreement)
# print("Avg Interagreements")
# print(Group1.UserAvgInterAgreement)
# print(Group1.GroupAvgInterAgreement)
# print(Group1.Summation(4))
print(Group1.InterReliability)