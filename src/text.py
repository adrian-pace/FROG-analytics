class Text:
    def __init__(self,age,name,race):
        self.age = age
        self.name = name
        self.race = race
        self.reletive = []



    def __eq__(self, other):
        return (self.age==other.age) and (self.name==other.name)


text_1 = Text(4,"xiaohai","chinese")
text_2 = Text(4,"xiaohai1","euro")
Textlist = []
Textlist.append(text_1)

print(text_2 in Textlist)
print(text_1==text_2)