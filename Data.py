import csv
import re
import matplotlib.pyplot as plt
import math

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
        self.Selfagreement=[[0 for x in range(5)] for y in range(self.Groupsize)]
        self.Matrix = [[0 for x in range(self.Groupsize)] for y in range(98)]
        self.InterAgreement=[[0 for x in range(98)] for y in range(self.Groupsize)]
        self.libAccuracy = 0
        self.oldLibAccuracy = 0
        self.InterReliability=0
        self.Scores = []
        self.OldScores=[]
        self.OldScoresPercentCorrect = []
        self.NewScoresPercentCorrect = []
        self.TValScores=0
        self.TValDifferences = 0
        self.libAccuracyAdvanced = 0
        self.oldLibAccuracyAdvanced = 0
        self.ScoresAsCategrory=[]
        self.OldScoresAsCategory=[]



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
                value = self.getValue(i)
                standard_value += value
                if(value!=0):
                    count+=1
        if(count ==0):
            return 0
        else:
            return (myvalue+standard_value)/count

    def analyzeOLD(self,string):
        standard_value=0
        count=0
        string = self.Strip(string).lower()
        string=self.Tokenize(string)
        for i in string:
            if(i.isalpha()):
                value = self.getValue(i)
                standard_value += value
                if(value!=0):
                    count+=1
        if(count ==0):
            return 0
        else:
            return standard_value/count

    def analyzeNEW(self,string):
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
        if(count ==0):
            return 0
        else:
            return (myvalue)/count

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
                            sum+=-4
                            self.Matrix[i-1][count]=-4
                        if(row[i]=="Negative"):
                            sum+=-2
                            self.Matrix[i-1][count]=-2
                        if(row[i]=="Positive"):
                            sum+=2
                            self.Matrix[i-1][count]=2
                        if(row[i]=="Very Positive"):
                            sum+=4
                            self.Matrix[i-1][count]=4
                        if(row[i]=="Neutral"):
                            self.Matrix[i-1][count]=0
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
                            self.Matrix[i-1][count]= -4
                        if(row[i]=="Negative"):
                            sum+=-2.5
                            self.Matrix[i-1][count]= -2
                        if(row[i]=="Positive"):
                            sum+=2.5
                            self.Matrix[i-1][count]=2
                        if(row[i]=="Very Positive"):
                            sum+=5
                            self.Matrix[i-1][count]=4
                        if(row[i]=="Neutral"):
                            self.Matrix[i-1][count]=0
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
            for values in range(47):
                sum+=self.InterAgreement[person][values]
                count+=1
            self.UserAvgInterAgreement.append(sum/count)
        for x in self.UserAvgInterAgreement:
            self.GroupAvgInterAgreement+=x
        self.GroupAvgInterAgreement=self.GroupAvgInterAgreement/len(self.UserAvgInterAgreement)
        self.CalcInterReliability()

    def CalcInterReliability(self):
        answer =0
        for question in range(self.StartTweets):
            sum = 0
            for score in range(len(self.Matrix[question])):
                for score2 in range(score+1,len(self.Matrix[question])):    
                    if(self.Matrix[question][score]==self.Matrix[question][score2]):
                        sum+=1
            # print(sum/self.Summation(len(self.Matrix[question])))
            answer += sum/self.Summation(len(self.Matrix[question]))     
        answer = answer/self.StartTweets
        self.InterReliability = answer

    def Summation(self,n):
        answer = 0
        for x in range(n):
            answer+=x
        return answer

def Test(g1,g2):
    OldScoreCorrectCount=0
    NewScoreCorrectCount=0
    OldScoreCorrectCountAdvanced=0
    NewScoreCorrectCountAdvanced=0
    # print(NewScoreCorrectCount)
    for CurrentTweet in g2.TweetValues.keys() :
        CurrentTweetScore = g2.TweetValues.get(CurrentTweet)
        # print(CurrentTweet)
        NewScore = g1.analyze(CurrentTweet)
        OldScore = g1.analyzeOLD(CurrentTweet)
        g1.Scores.append(NewScore)
        g1.OldScores.append(OldScore)
        g1.NewScoresPercentCorrect.append(1-(abs(NewScore-CurrentTweetScore)/10))
        g1.OldScoresPercentCorrect.append(1-(abs(OldScore-CurrentTweetScore)/10))
        g1.ScoresAsCategrory.append(categorize(NewScore))
        NewScoreCorrectCountAdvanced += analyzeScoreAdvanced(NewScore,CurrentTweetScore)
        OldScoreCorrectCountAdvanced += analyzeScoreAdvanced(OldScore,CurrentTweetScore)
        NewScoreCorrectCount += analyzeScore(NewScore,CurrentTweetScore)
        OldScoreCorrectCount += analyzeScore(OldScore,CurrentTweetScore)
    # print(NewScoreCorrectCount)
    # print(OldScoreCorrectCount)
    g1.libAccuracyAdvanced = NewScoreCorrectCountAdvanced/len(g2.TweetValues)*100
    g1.oldLibAccuracyAdvanced = OldScoreCorrectCountAdvanced/len(g2.TweetValues)*100
    g1.libAccuracy = NewScoreCorrectCount/len(g2.TweetValues)*100
    g1.oldLibAccuracy=OldScoreCorrectCount/len(g2.TweetValues)*100
    
def analyzeScoreAdvanced(Score,TweetScore):
    if((Score<-1 and Score>=-3) and (TweetScore<-1 and TweetScore>=-3)):
        return 1
    if((Score>1 and Score<=3) and (TweetScore>1 and TweetScore<=3)):
        return 1
    if((TweetScore<=1 and TweetScore >=-1) and (Score<=1 and Score >=-1)):
        return 1
    if(TweetScore>3 and Score>3):
        return 1
    if(TweetScore<-3 and Score<-3):
        return 1
    else:
        return 0

def categorize(Score):
    if(Score<-1 and Score>=-3):
        return "Negative"
    if(Score>1 and Score<=3):
        return "Positive"
    if(Score<=1 and Score >=-1):
        return "Neutral"
    if(Score>3):
        return "Very Positive"
    if(Score<-3):
        return "Very Negative"
    

def analyzeScore(Score,TweetScore):
    if((Score<=1 and Score>=-1) and (TweetScore<=1 and TweetScore>=-1)):
        return 1
    if(Score>1 and TweetScore>1):
        return 1
    if(TweetScore<-1 and Score<-1):
        return 1
    else:
        return 0
               
def Ttest(g1scores,g2scores):
    g1Sum = getSum(g1scores)
    g2Sum = getSum(g2scores)
    # print(g1Sum)
    g1SquaredSum = g1Sum*g1Sum
    g2SquaredSum = g2Sum*g2Sum
    # print(g1SquaredSum)
    g1Mean = g1Sum/len(g1scores)
    g2Mean = g2Sum/len(g2scores)
    # print(g1Mean)
    g1SumofSquares = sumofsquares(g1scores)
    g2SumofSquares = sumofsquares(g2scores)
    # print(g1SumofSquares)
    T = (g1Mean-g2Mean)/math.sqrt((((g1SumofSquares-(g1SquaredSum/len(g1scores)))+(g2SumofSquares-(g2SquaredSum/len(g2scores))))/(len(g1scores)+len(g2scores)-2))*(1/len(g1scores)+1/len(g2scores)))   
    return T
    
def getSum(array):
    sum=0
    for score in array:
        sum+=score
    return sum

def sumofsquares(array):
    sum=0
    for score in array:
        sum+=(score*score)
    return sum

Group1 = DataSet("ResponseDataG1.csv",5)
Group1.createlib()

Group2 = DataSet("ResponseDataG2.csv",4)
Group2.createlib()

print("Testing Group1 Library on Group2 Tweets")
Test(Group1,Group2)
print("Testing Group2 Library on Group1 Tweets")
Test(Group2,Group1)

Group1.TValScores=Ttest(Group1.Scores,Group1.OldScores)
Group2.TValScores=Ttest(Group2.Scores,Group2.OldScores)
Group1.TValDifferences = Ttest(Group1.NewScoresPercentCorrect,Group1.OldScoresPercentCorrect)
Group2.TValDifferences = Ttest(Group2.NewScoresPercentCorrect,Group2.OldScoresPercentCorrect)

plt.plot([Group1.libAccuracy,Group2.libAccuracy],[Group1.InterReliability,Group2.InterReliability],label='Inter-Reliability',marker='o')
plt.plot([Group1.libAccuracy,Group2.libAccuracy],[Group1.GroupAvgSelfAgreement,Group2.GroupAvgSelfAgreement],label='Self-Agreement',marker='o')
plt.plot([Group1.libAccuracy,Group2.libAccuracy],[Group1.GroupAvgInterAgreement,Group2.GroupAvgInterAgreement],label='Inter-Agreement',marker='o')
plt.xlabel("Library Accuracy")
plt.title("Accuracy vs Inter-Reliability, Self-Agreement, and Inter-Agreement")
plt.legend()
plt.show()

print(Group1.TweetValues)

print("Avg Self Agreements")
print(Group1.GroupAvgSelfAgreement)
print(Group2.GroupAvgSelfAgreement)

print("Avg Interagreements")
print(Group1.GroupAvgInterAgreement)
print(Group2.GroupAvgInterAgreement)

print("Group Inter Reliability")
print(Group1.InterReliability)
print(Group2.InterReliability)

print("Group accuracy")
print(Group1.libAccuracy)
print(Group2.libAccuracy)

print("Old Library Accurracy on Group2 Tweets and on Group1 Tweets")
print(Group1.oldLibAccuracy)
print(Group2.oldLibAccuracy)

print("Group accuracy Advanced")
print(Group1.libAccuracyAdvanced)
print(Group2.libAccuracyAdvanced)

print("Old Library Accurracy on Group2 Tweets and on Group1 Tweets (Advanced)")
print(Group1.oldLibAccuracyAdvanced)
print(Group2.oldLibAccuracyAdvanced)

print(len(Group1.NewScoresPercentCorrect)+len(Group1.OldScoresPercentCorrect)-2)
print("T vals for accuracy")
print(Group1.TValDifferences)
print(Group2.TValDifferences)

print(Group1.analyze("sorry i'm trash"))
print(Group1.analyze("sorry"))
print(Group1.analyze("i'm"))
print(Group1.analyze("trash"))
print(Group1.analyzeOLD("trash"))