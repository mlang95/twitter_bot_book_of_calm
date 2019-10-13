import random
import tweepy
from datetime import datetime
from datetime import timedelta
from time import sleep

#from PIL import Image
#from selenium import webdriver
#from selenium.webdriver.chrome.options import Options

class Time():
	def __init__(self,file):
		self.file = file
	def Get_Time(self):
		Time = open(self.file,"w")
		Time.readlines()
		Time.close()
		return Time[-1]
	def Replace_Time(self):
		Time = open(self.file,"w")
		Time.readlines()
		Time.write(datetime.now())
		Time.close()
		
def Time_Check(break_time, activity):
	if abs(datetime.now() - activity).seconds  > break_time:
		return True
	else:
		return False
		
class Poem():
    def __init__(self,title,text,number):
        self.title = title
        self.text = text
        self.number = number
        self.printpoem = ''
        self.topline = ''
        
    def Center_Alignment(self):
        x = len(str(self.number)) +2
        spaces = ' '*x
        self.title = spaces + self.title
        Title_Length = len(self.title)
        Broken_Text = self.text.split("\\n")
        Max_Length = len(max(Broken_Text,key=len))
        if Title_Length > Max_Length:
            Max_Length = Title_Length
        Centered_List = []
        for line in Broken_Text:
            x = int(round((Max_Length-len(line))/2,0))
            line = ' '*x + line
            Centered_List.append(line)
        Centered_Text = ''
        for line in Centered_List:
            Centered_Text += line + "\n"
        #print(Centered_Text)
        self.text = Centered_Text
        Amount_To_Add_To_Title = round((Max_Length-Title_Length)/2,0)
        Spaces = ''
        return self
    def Print_Poem(self):
        x = len(str(self.number))
        self.topline = str(self.number) + '- '+ self.title[x+2:]
        self.printpoem = self.topline +'\n\n\n'+self.text
        return self
    
def Read_The_Lines(txt): #txt = "BookofCalm.txt" for example
    Poems = []
    file = open(txt,"r")
    page = 1
    for line in file:
        Title_Poem_Split = line.split("+")
        Poems.append(Poem(Title_Poem_Split[0],Title_Poem_Split[1],page))
        page +=1
    file.close()
    return Poems #list of objects
def Check_Recents(txt,poemnumber):
	file = open(txt,"r")
	try:
		PoemNumbers = file.readline().split(" ")
	except:
		print("can't read")
	if str(poemnumber) in PoemNumbers:
		print("%s is already in recents!!" % str(poemnumber))
		file.close()
		return True
	elif poemnumber not in PoemNumbers:
		while len(PoemNumbers) >= 50:
			print("Removing %s from recents" % PoemNumbers[0])
			del PoemNumbers[0]
		PoemNumbers.append(poemnumber)
		print("Adding %s to recents" % (poemnumber))
		file = open(txt,"w")
		for number in PoemNumbers:
			file.write(str(number)+ " ")
		file.close()
		return False
def Check_Time(txt):
	f = open(txt,"r")
	time = datetime.strptime(f.readline(),'%Y-%m-%d %H:%M:%S.%f')
	if time == '':
		Update_Time(txt)
		Check_Time(txt)
		f.close()
	f.close()
	return time
def Update_Time(txt):
	f = open(txt,"r")
	time =  datetime.strptime(f.readline(),'%Y-%m-%d %H:%M:%S.%f')
	f = open(txt,"w+")
	f.write(str(datetime.now()))
	f.close()
	
def Check_For_Keywords(Poems,tweet):
	tweet = tweet.split(" ")
	for poem in Poems:
		intersection = set((poem.text).split(" ")).intersection(set(tweet))
		if len(intersection) != 0:
			print("found keyword(s) %s" % intersection)
			return poem
		else:
			return random.choice(Poems)
	
def Pick_A_Poem(Poems):
    Poem_To_Print = random.choice(Poems)
    return Poem_To_Print.Center_Alignment().Print_Poem()

def Tweet_Poem(Poems,str,keyword_flag):
	Cant_Tweet = True
	attempt = 0
	while Cant_Tweet is True:
		if keyword_flag != "" and attempt == 0:
			Poem = Check_For_Keywords( Poems, tweet.text)
			attempt = 1
		else:
			Poem = random.choice(Poems)
		if len(Poem.Center_Alignment().Print_Poem().printpoem) +len(str) > 280:
			if len(Poem.Print_Poem().printpoem) +len(str) > 280:
				Cant_Tweet = True
			elif Check_Recents("Recents.txt",Poem.number) is False:
				return Poem.Print_Poem().printpoem
		elif Check_Recents("Recents.txt",Poem.number) is False:
			return Poem.Center_Alignment().Print_Poem().printpoem
	
	
auth = tweepy.OAuthHandler("","")
auth.set_access_token("","")
api = tweepy.API(auth)
try:
	api.verify_credentials()
	print("Authentication OK")
	
except:
	print("Error during authentication")
#Start_Time = Time("StartTime.txt")
Keep_Tweeting = True
while Keep_Tweeting is True:
	if Time_Check(60*60*4,Check_Time("ActivityTime.txt")):
		Poems = Read_The_Lines("BookofCalm.txt")
		Tweet = Tweet_Poem(Poems,"","")
		api.update_status(Tweet)
		Update_Time("ActivityTime.txt")
		print("tweet sent to main")
	if Time_Check(60*60*1,Check_Time("MentionTime.txt")):
		for tweet in api.search(q="stressed",lang="en", count=10):
			if tweet.retweeted is False:
				Already_Favorite = False
				try:
					api.create_favorite(tweet.id)
				except:
					Already_Favorite = True #This will stop us from sending tweets to same tweet multiple times 
					print("can't favourite!")#if our scanner doesn't produce new results
				if Already_Favorite is False:
					Poems = Read_The_Lines("BookofCalm.txt")
					mention = "@"+str(tweet.author.screen_name)
					Tweet = Tweet_Poem(Poems,mention,tweet)
					api.update_status(status = Tweet,in_reply_to_status_id = tweet.id,auto_populate_reply_metadata=True)
					print("tweet sent to %s!" % tweet.user.name)
					Update_Time("MentionTime.txt")
				sleep(6)
		print("Finished")
	sleep(600)

