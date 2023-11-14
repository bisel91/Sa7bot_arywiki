from textblob.en import Spelling
pathToFile = "train.txt"
spelling = Spelling(path = pathToFile)
text = " "

with open("test.txt", "r") as f:
    text = f.read()
words = text.split()
corrected = " "
for i in words :
    corrected = corrected +" "+ spelling.suggest(i)[0][0] # Spell checking word by word
print(corrected)
