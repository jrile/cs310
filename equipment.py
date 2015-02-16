# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 22:29:48 2013

@author: ben
"""
metal="metal"
plastic="plastic"
glass="glass"



class Equipment(object):
    def __init__(self):
        self.contents=[]
        self.material=None
        self.temp=70
    def cook(self, temp):
        if self.temp<100:
            raise not_preheated()
        for item in self.contents:
            item.cook(temp)
    def longprint(self, recurs=0):
        keys=self.__dict__.keys()
        keys.remove('contents')
        print('  '*recurs+self.__class__.__name__)
        for key in keys:
            print('  '*recurs+key+': '+self.__dict__[key].__str__())
        print('contents:')
        if self.__dict__['contents']!=None:
            for item in self.__dict__['contents']:
                item.longprint(recurs+1)
        print('')
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

            
class not_preheated(Exception):
    pass
        
class Pan(Equipment):
    def __init__(self):
        super(Pan,self).__init__()  
        self.material=metal
    def preheat(self, temp):
        self.temp=temp
        
class Pot(Equipment):
    def __init__(self):
        super(Pot,self).__init__()  
        self.material=metal
    def preheat(self, temp):
        self.temp=temp

class Toaster(Equipment):
    def __init__(self):
        super(Waffle_Iron,self).__init__()  
        self.material=metal
        self.temp=400
        
class Waffle_Iron(Equipment):
    def __init__(self):
        super(Pan,self).__init__()  
        self.material=metal
        self.temp=300
        
class Baking_Dish(Equipment):
    def __init__(self):
        super(Baking_Dish,self).__init__()  
        self.material=glass

class Plate(Equipment):
    def __init__(self):
        super(Plate,self).__init__()  
        self.material=glass
        
class Cup(Equipment):
    def __init__(self):
        super(Cup,self).__init__()  
        self.material=glass

class Bowl(Equipment):
    def __init__(self):
        super(Bowl,self).__init__()  
        self.material=glass        
        
class Oven(Equipment):
    def __init__(self):
        super(BakingDish,self).__init__()
    def preheat(self, temp):
        self.temp=temp
