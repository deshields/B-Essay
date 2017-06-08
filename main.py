# Main functions
#Python 2.7
import json
import unirest
from StringIO import StringIO
from flask import Flask
app = Flask(__name__)

f = open('female.txt', 'r')
f1 = f.read()
flist = f1.splitlines()
m = open('male.txt', 'r')
m1 = m.read()
mlist = m1.splitlines()
names = flist + mlist
punctuation = ["!", "?", ".", "!?", "?!", ","]

@app.route('/')
class makeNewEssay(object):
    """makes a really silly essay"""
    def __init__(self, essay, word_target):
        self.essay = essay.split()
        self.new_essay = ""
        self.final_essay = ""
        self.word_target = word_target
        # TODO: fully implement word target
        # TODO: implement punctuation recognition for synonym
        # TODO: make a new separate function that appends punctuation
        # TODO: Maybe move the API call so that it doesn't run too many times, dunno if it'll make much difference though

        placeholder = []
        for z in self.essay:
            if(z[-1] in punctuation):
                placeholder.append(z[:-1])
                placeholder.append(z[-1])
            else:
                placeholder.append(z)
        self.essay = placeholder
    #KEEP IN MIND THAT "?!" AND "!?" ARE MORE THAN THE INDEX OF -1; NEED TO MAKE ANOTHER CASE FOR THIS

    def pickLongestSynonym(self):
        """ goes through each word in the essay to find a longer synonym and appends
        it to the new Essay """
        for x in self.essay:
            print("Running: " + x)
            print(self.new_essay)
            if(x in punctuation):
                #self.essay[self.essay.index(x)-1] += x
                self.new_essay = self.new_essay[:-1] + x + " "
                self.essay.remove(x)
                continue

            elif(x not in names):
                ret = unirest.get("https://wordsapiv1.p.mashape.com/words/" +str(x) +"/synonyms",
                    headers={
                        "X-Mashape-Key": "o4BB4YatyVmshNlvtMFsZNXCDPcmp1u8RNQjsnb2RscDXVMK0f",
                        "Accept": "application/json"
                    }
                )
                try:
                    response = json.loads(ret._raw_body)
                except ValueError:
                    continue

                if(len(response['synonyms']) != 0):
                    new_word = response['synonyms'][0]
                    if(len(response['synonyms']) > 1):
                        longest = new_word
                        for y in response['synonyms']:
                            if(len(y) >= longest):
                                longest = y
                        self.new_essay = self.new_essay + longest + " "
                    else:
                        self.new_essay = self.new_essay + new_word + " "
                else:
                    self.new_essay = self.new_essay + x + " "
            else:
                self.new_essay = self.new_essay + x + " "

        self.essay = self.new_essay.split()
        print(self.new_essay)

    def extendByDefinition(self):
        """ extends the word count of the essay by finding a rare-enough word and adding the definition """
        temp = ""
        ignore = []
        print("Initial: ", self.essay)

        for x in range(len(self.essay)):
            print("Running: ", self.essay[x])

            if(self.essay[x] in punctuation):
                self.essay[x-1] += self.essay[x]
                self.essay[x] = ''
                continue

            pun = ""
            print(self.essay)

            if(self.essay[x][:-1] not in ignore or self.essay[x] not in names):
                if(self.essay[x][-1] in punctuation):
                    pun = self.essay[x][-1]
                    #print("pun: ", pun)
                    self.essay[x] = self.essay[x][:-1]

                ret1 = unirest.get("https://wordsapiv1.p.mashape.com/words/" +str(self.essay[x]) + "/frequency",
                    headers={
                        "X-Mashape-Key": "o4BB4YatyVmshNlvtMFsZNXCDPcmp1u8RNQjsnb2RscDXVMK0f",
                        "Accept": "application/json"
                    }
                )

                try:
                    freq = json.loads(ret1._raw_body)
                except ValueError:
                    continue

                if('frequency' in freq.keys() and freq['frequency']['zipf'] <= 2.5):
                    ret2 = unirest.get("https://wordsapiv1.p.mashape.com/words/" +str(self.essay[x]),
                        headers={
                            "X-Mashape-Key": "o4BB4YatyVmshNlvtMFsZNXCDPcmp1u8RNQjsnb2RscDXVMK0f",
                            "Accept": "application/json"
                        }
                    )

                    defin = json.loads(ret2._raw_body)

                    if('definition' in defin.keys()):
                        longest = ""
                        for y in defin['results']:
                            if(len(y['definition']) >= len(longest)):
                                longest = y['definition']

                        if(self.essay[x+1] in punctuation):
                            temp = longest + self.essay[x+1]
                        else:
                            temp = longest +", "

                        ignore.append(longest)

                        self.essay[x] += ", or"
                        self.essay.insert(x+1, temp)
                        self.essay.remove(self.essay[x+2])
                        #print("inner test", self.essay)

        print(self.essay)
    
    def joinEssay(self):
        for word in essay:
            if word in punctuation:
                self.final_essay = self.final_essay[:-1] + word + " "
            else:
                self.final_essay += word + " "

    def createEssay(self):
        self.pickLongestSynonym()
        #self.extendByDefinition()
        return_essay = ' '.join(self.essay)
        return return_essay



test = makeNewEssay("King Henry won the throne when his force defeated King Richard III at the Battle of Bosworth Field, the culmination of the Wars of Roses.", 6)
#test = makeNewEssay("The quick brown fox jumps over the lazy dog", 6)
print(test.createEssay())
#print(test.testingKey())
