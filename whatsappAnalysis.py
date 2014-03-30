from collections import defaultdict, Counter
import operator
import datetime
import re

english_dictionary=[]
groupeo=[]
member_file='' #Enter the full path of conf file that stores the group member's names
oxford_dictionary_file='' #Enter the full path of the file that stores all the list of english words
chat_transcript_file='' #Enter the full path of the file that stores the text transcript of the group chat
output_file_location='' #Enter the full path of the file where you want the output to be stored

def load_members():
    '''TODO:
        Extract member names from the chat trnascripts
        '''
    f=open(member_file,'r')
    for line in f:
        groupeo.append(line.strip())
    f.close()



def load_english_dictionary():
	for line in open(oxford_dictionary_file):
		english_dictionary.append(line.strip())

def parse():	
	interaction=defaultdict( )
	groupeo_member=defaultdict(list)
	for key in groupeo:	
		interaction[key]=[]
	f=open(chat_transcript_file,"r")
	total_lines=0
	current_member=""
	date=""
	time=""
	prev_member_flag=True
	prev_member="start"
	for line in f:
		if line.find("PM,")!=-1 or line.find("AM,")!=-1:
			line.strip("\n")
			lineSplit=line.split(",")
			data=[]
			time=lineSplit[0]
			current_time=time
			date=lineSplit[1][:lineSplit[1].find("-")]
			current_date=date
			member=lineSplit[1][lineSplit[1].find("-")+1:lineSplit[1].find(":")]
				
			current_member=member
			if prev_member_flag !=True and prev_member!=current_member:
				interaction[prev_member.strip()].append(current_member.strip())
			prev_member=current_member
			prev_member_flag=False
			message=lineSplit[1][lineSplit[1].find(":"):]
			message.strip("\n")
			data.append(time)
			data.append(date)
			data.append(message)
			groupeo_member[member].append(data)
		
		else:
			data=[]
			data.append(time)
			data.append(date)
			data.append(line)
			groupeo_member[current_member].append (data)
		total_lines+=1
	f.close()
	return groupeo_member,interaction
	
def analyze(groupeo_member, interaction):
	g=open(output_file_location,"w")
	talkative,activeness=talkativeness(groupeo_member)
	talkative_words=find_total_words(groupeo_member)
	smiley=checkSmiley(groupeo_member)
	g.write("Most Active "+str(activeness)+"\n")
	g.write("Smiley Fan "+str(smiley)+"\n")
	english=englishWords(groupeo_member)
	english_percentage=calculate_percentage(english,talkative_words)
	g.write(" English Words" + str(english_percentage)+"\n")
	office_hours=officeTime(groupeo_member)
	g.write("Office Hours "+str(office_hours)+"\n")
	office_hours_percentage=calculate_percentage(office_hours,talkative)
	g.write("Office Hours "+str(office_hours_percentage)+"\n")
	
	g.write(" Interaction---\n")
	for key in interaction:
		g.write("\n")
		g.write(key+"\t")
		c=Counter(interaction[key])
		g.write(str(c.items()))
	g.close()
	
	
def officeTime(groupeo_member):
	office_hours=defaultdict()
	office_flag=False
	month_dict={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
	for key in groupeo_member:
		count=0
		for data in groupeo_member[key]:
			time=data[0]
			date=data[1]
			date_split=date[1:].split(" ")
			month=date_split[0].strip()
			day=int(date_split[1].strip())
			month_int=month_dict[month]
			am_pm=time.strip()[-2:].strip()	
			time=time[:-2].strip()
			hour=int (time.strip()[:time.strip().find(":")])
			min=int(time.strip()[time.strip().find(":")+1:])
			if am_pm=="AM":
				if hour >8 and hour<12:
					office_flag=True
				else:
					office_flag=False
			if am_pm=="PM":
				if hour>11 and hour <5:
					office_flag=True
				else:
					office_flag=False
			if month_int<8:	
				year =2013
			else:
				year=2012
			t=datetime.datetime(year,month_int,day)
			if t.weekday() <5 and office_flag:
				count+=1
		office_hours[key]=count
	return office_hours

def find_total_words(groupeo):
	total_words=defaultdict()
	for key in groupeo:
		count=0
		for data in groupeo[key]:	
			message_body_split=data[2].split(" ")
			count+=len(message_body_split)
		total_words[key]=count
	return total_words
	
	
def calculate_percentage(english,talkative):
	english_percentage=defaultdict()
	for key in english:
		print key, english[key],talkative[key]
		english_percentage[key]=float(english[key])/float(talkative[key])*100
	return english_percentage
	
def englishWords(groupeo_member):	
	english_words=defaultdict()
	for key in groupeo_member:
		english_words[key]=0
	for key in groupeo_member:
		for data in groupeo_member[key]:
			message_body=data[2]
			message_body_split=message_body.split(" ")
			for word in message_body_split:
				word=word.strip("\n")
				word=word.strip("!@#$%^&*()_+<>?:{}|,\'./;[]")
				if word in english_dictionary:
					english_words[key]+=1
	return english_words

def talkativeness(groupeo_member):
	talkative=defaultdict()
	for key in groupeo_member:
		talkative[key]=len(groupeo_member[key])
	sorted_talkative = sorted(talkative.iteritems(), key=operator.itemgetter(1))	
	return talkative,sorted_talkative

def checkSmiley(groupeo_member):
	smileys=[":-)",":)",":-(",":(",";)",":P",":D","\xee"]
	smiley=defaultdict()
	for key in groupeo_member:
		smiley_count=0
		data=groupeo_member[key]
		for message in data:
			message_body=message[2]
			message_body=message_body.strip("\n")
			message_body_split=message_body.split(" ")
			for smile in smileys:
				found = any(smile in item for item in message_body_split)
				if found==True:
					smiley_count+=1
		smiley[key]=smiley_count
	return smiley
			
			
	
def main():
	load_english_dictionary()
	groupeo_member, interaction=parse()
	analyze(groupeo_member, interaction)

	
	
if __name__ == '__main__':
	main()