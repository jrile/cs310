# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 19:18:54 2013

@author: ben
    
food for thought (LOL)
    should flour, sugar, salt, pepper, spices be solid or powder?
"""

solid="solid"
liquid="liquid"

"""
THE SCRIPT TO UNPICKLE THE DEFINITIONS DICTIONARY GOES HERE
"""

class Food(object):
    def __init__(self):
        self.state_of_matter=solid
        self.shape=""
        self.contents=None #if it can have contents, this must be a list (even if empty)
        self.cooked=0
    def cook(self, percent):
        self.cooked+=percent
        if self.contents!=None:
            for item in self.contents:
                item.cook(percent)
    def remove(self, class_to_be_removed): #only removes lowest class i.e. remove(Food) will not remove an Egg
        if self.contents!=None:
            self.contents.remove([i for i in self.contents if i.__class__==class_to_be_removed])
    def longprint(self, recurs=0):
        keys=self.__dict__.keys()
        keys.remove('contents')
        print('  '*recurs+self.__class__.__name__)
        for key in keys:
            print('  '*recurs+key+': '+self.__dict__[key].__str__())
        
        if self.__dict__['contents']!=None and self.__dict__['contents']!=[]:
            print('  '*recurs+'contents:')
            for item in self.__dict__['contents']:
                item.longprint(recurs+1)
        else:
            print('  '*recurs+'contents: None')
                
        print('')

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class Prepared_Food(Food):
    def __init__(self, name, ingredients):
        self.name=name
        self.contents=ingredients
        self.original_ingredients=tuple(ingredients) #for immutability
    def __repr__(self):
        if self.contents==list(self.original_ingredients):
            return "masterfuly prepared %s" % self.name
        else:
            return "botched %s" % self.name
    def __str__(self):
        return self.__repr__()
        
class cant_do_that(Exception):
    def __init__(self, message):
        self.message=message
    def __str__(self):
        return self.message

class wasted_food(Exception):
    def __init__(self, food):
        self.food=food
    def __str__(self):
        return self.food.__class__.__name__

class Water(Food):
    def __init__(self):
        super(Water,self).__init__()
        self.state_of_matter=liquid
        self.contents=[]
    
class Bread(Food):
    def __init__(self):
        super(Bread,self).__init__()
        self.cooked=100
    def slice(self):
        self.shape="sliced"
	def toast(self, percent):
		self.toasted+=percent
        def flip(self):
            if(self.flipped == False):
                self.flipped = True
            
        
class Bagel(Bread):
    def __init__(self):
        super(Bagel,self).__init__()
        
class EnglishMuffin(Bread):
    def __init__(self):
        super(EnglishMuffin,self).__init__()

class Egg(Food):
    def __init__(self):
        super(Egg,self).__init__()
        self.state_of_matter=liquid
        self.shell=True
        self.beaten=False
        self.contents=[]
    def crack(self):
        if self.shell==True:
            self.shell=False
        else:
            raise cant_do_that("re-crack an egg")
    def peel(self):
        if self.cooked>=70 and self.shell:
            self.crack()
        elif self.cooked<70:
            raise wasted_food(self)
        else:
            raise cant_do_that("re-peel an egg")
    def beat(self):
        if self.state_of_matter==liquid and not self.shell:
            self.beaten=True
        elif self.shell:
            raise wasted_food(self)
    def flip(self):
        if self.shape!="folded":
	    self.shape="flipped"
    def fold(self):
        if self.state_of_matter=="solid":
            self.shape="folded"
        else:
            raise cant_do_that("Flip a runny egg")  
    def cook(self, percent):
        self.cooked+=percent
        if self.contents!=None:
            for item in self.contents:
                item.cook(percent)
        if self.cooked>40:
            self.state_of_matter=solid
	def poach(self):
		if self.shape!="poached":
			self.shape="poached"
			
             

class Potato(Food):
    def __init__(self):
        super(Potato,self).__init__()
    def grate(self):
        if self.shape=="" or self.shape=="peeled":
            self.shape="grated"
        else:
            raise cant_do_that("re-grating a potato")
    def peel(self):
        if self.shape=="":
            self.shape="peeled"
        else:
            raise cant_do_that("re-peeling a potato")
	def cut(self, size):
		self.size = size

class Milk(Food):
    def __int__(self):
        super(Milk,self).__init__()
        self.state_of_matter=liquid

class Mandarine_Oranges(Food):
    def __init__(self):
        super(Mandarine_Oranges).__init__()

class Olive_Oil(Food):
    def __init__(self):
        super(Olive_Oil,self).__init__()
        self.state_of_matter=liquid

class Butter(Food):
    def __init__(self):
        super(Butter,self).__init__()
    def melt(self):
        self.state_of_matter=liquid
        #this needs to be used when butter is applies to a preheated equipment

class White_Vinegar(Food):
    def __init__(self):
        super(White_Vinegar,self).__init__()
        self.state_of_matter=liquid

class Flour(Food):
    def __init__(self):
        super(Flour, self).__init__()

def Sugar(Food):
    def __init__(self):
        super(Sugar,self).__init__()

def Salt(Food):
    def __init__(self):
        super(Salt,self).__init__()

def Baking_Powder(Food):
    def __init__(self):
        super(Baking_Powder,self).__init__()

def Baking_Soda(Food):
    def __init__(self):
        super(Baking_Soda,self).__init__()

def Bacon(Food):
    def __init__(self):
        super(Bacon, self).__init__()
	def flip(self):
		if self.flipped==False:
			self.flipped = True

def Onion(Food):
    def __int__(self):
        super(Onion,self).__int__()
    def dice(self):
        if self.diced==False:
            self.diced=True
        else:
            raise cant_do_that("you can't redice an onion")

def Shredded_Cheddar(Food):
    def __int__(self):
        super(Shredded_Cheddar,self).__int__()

def Oats(Food):
    def __int__(self):
        super(Oats,self).__int__()

def Chopped_Apples(Food):
    def __int__(self):
        super(Chopped_Apples,self).__int__()

def Chopped_Bananas(Food):
    def __int__(self):
        super(Chopped_Bananas,self).__int__()

def Chopped_Walnuts(Food):
    def __int__(self):
        super(Chopped_Walnuts,self).__int__()

def Raisins(Food):
    def __int__(self):
        super(Raisins,self).__int__()

def Yogurt(Food):
    def __int__(self):
        super(Yogurt,self).__int__()
        self.state_of_matter=liquid

def Grapes(Food):
    def __int__(self):
        super(Grapes,self).__int__()

def Holed_Bread(Food):
    def __int__(self):
        super(Holed_Bread,self).__int__()
	def flipped(self):
		if(self.flipped == False):
			self.flipped = True

def Vegetable_Oil(Food):
    def __init__(self):
        super(Vegetable_Oil,self).__init__()
        self.state_of_matter-liquid

def Vanilla_Extract(Food):
    def __init__(self):
        super(Vanilla_Extract,self).__init__()
        self.state_of_matter=liquid

def Hash_Brown(Food):
    def __init__(self):
        super(Hash_Brown,self).__init__()

def Black_Pepper(Food):
    def __init__(self):
        super(Black_Pepper,self).__init__()

def Garlic_Powder(Food):
    def __init__(self):
        super(Garlic_Powder,self).__init__()

def Brown_Sugar(Food):
    def __init__(self):
        super(Brown_Sugar,self).__init__()

def Cinnamin(Food):
    def __init__(self):
        super(Cinnamin,self).__init__()



"""
#Some examples
test_food=Water()
test_food.contents.append(Potato())
test2=Egg()
test2.crack()
test2.beat()
test_food.contents.append(test2)
print ["Food: "+i.__class__.__name__+" state: "+i.state_of_matter for i in test_food.contents]
"""            
