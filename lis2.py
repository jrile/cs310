'''
    written by Joseph Craig, 2013
    
    The only rights reserved are that this comment must not be changed, regardless
    of how else you use or modify this file, and that the following rights of others
    be respected.
    
    This is a hacky extension of Peter Norvig's Lispy, which can be found at
    http://norvig.com/lispy.html.  As such, there is plenty of code in here that he
    wrote and I did not change; he naturally retains the copyright to that code.
    
    Furthermore, I am aware that he also wrote an article for a Lispy 2.  I have not
    read that article, but I pass along the copyright of any code that could be
    deemed a modification of that project to him as well.
    '''

################################### Imports ####################################
from __future__ import division

import sys
sys.dont_write_bytecode = True

import parse as ParseModule # I use Richard Jones's "parse" module as-is
import random
import re
from food import *
from equipment import *

################################## Exceptions ##################################
class ShortCircuitReturn(Exception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

class SymbolNotFound(Exception):
    def __init__(self, symbol):
        Exception.__init__(self)
        self.symbol = symbol

################################### Classes ####################################
class Symbol(str): pass

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms,args))
        self.outer = outer
    
    def find(self, var):
        "Find the innermost Env where var appears."
        if var in self:
            return self
        elif self.outer is not None:
            return self.outer.find(var)
        else:
            raise SymbolNotFound(var)


    def trace(self, function):
        if function in self.trace:
            trace.remove(function)
        else:
            trace.append(function)
    
    def isTraced(self, function):
        if function in self.trace:
            return True
        return False

##################### Lispy Built-in Function Definitions ######################
def extractFromString(pattern, string, values):
    '''Extracts portions of a string and translates them into different types as
        specified by the pattern.  Returns whichever values are requested.
        
        This function wraps the "parse" function from the "parse" module, so its
        documentation ( http://goo.gl/ZcqZb ) should be read to know how to use it.
        
        Returns a single value if only one value is requested and a list of values
        otherwise.'''
    result = ParseModule.parse(pattern, string)
    if isa(values, list):
        return [getFromParseResult(result, x) for x in values]
    else:
        return getFromParseResult(result, values)

def getFromParseResult(result, value):
    'Extracts the requested named or indexed value from the passed result object.'
    if isa(value, str):
        return result.named[value]
    else:
        return result.fixed[value]

def functionalShuffle(sequence):
    'Returns a shuffled copy of the passed list.'
    toReturn = list(sequence)
    random.shuffle(toReturn)
    return toReturn

def lispyPrint(*values):
    'Prints all the passed values to the console.'
    for value in values:
        print to_string(value, False),
    print

def load(filename):
    'Loads and evaluates all the Lispy statements in the requested file.'
    with open(filename) as program:
        code = program.read()
    returnValue = None
    for part in parse(code):
        try:
            returnValue = eval(part)
        except ShortCircuitReturn as e:
            returnValue = e.value
    return returnValue

def returnValue(x):
    'Exits the nearest enclosing loop, returning a value.'
    raise ShortCircuitReturn(x)
    
def recursiveJoin(x,top=False):
    if isa(x,list):
        xstr= "("+" ".join(recursiveJoin(i) for i in x)+")"
        if top:
            return xstr[1:-1]
        else:
            return xstr
    else:
        try: xstr=x.__str__()
        except Exception: xstr="<unavalilable>"
        return xstr

########################### Lispy Global Environment ###########################
def add_globals(env):
    "Add some Scheme standard procedures to an environment."
    # The following code was supplied by Norvig (with a modification to "append"
    # by me).  Do no change.
    import math, operator as op
    env.update(vars(math)) # sin, sqrt, ...
    
    env.update(
               {'+':op.add, '-':op.sub, '*':op.mul, '/':op.div, 'not':op.not_,
               '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
               'equal?':op.eq, 'eq?':op.is_, 'length':len, 'cons':lambda x,y:[x]+y,
               'car':lambda x:x[0],'cdr':lambda x:x[1:], 'append':lambda x,y:x+[y],
               'list':lambda *x:list(x), 'list?': lambda x:isa(x,list),
               'null?':lambda x:x==[], 'symbol?':lambda x: isa(x, Symbol)})
    
    env.update({'sunnysideup':60, 'overeasy':25, 'overmedium':50, 'overhard':100,
               'softboiled':80, 'mediumboiled':90, 'hardboiled':100, 'poached':80,
               'low':170, 'medium':250, 'high':350})
    
    
    
    # The following code was added by me to make your life easier.  Do not change.
    env.update(vars(random))
    
    env.update({
               'extract-from-string': extractFromString,
               'filter': filter,
               'load': load,
               'print': lispyPrint,
               'range': range,
               'return': returnValue,
               'shuffle': functionalShuffle # this overrides the shuffle from above.
               })
    
    return env


global_env = add_globals(Env())
counts=dict()
isa = isinstance
definately_dont_check_trace=False

################################ Lispy Reading #################################
def parse(string):
    '''Constructs a tuple of items that are understandable by "eval" using the
        passed string.'''
    index = 0
    code = string.strip()
    parsed = []
    
    while index < len(code):
        newlyParsed, index = recursiveParse(code, index)
        
        if newlyParsed == None:
            raise SyntaxError('malformed form')
        elif newlyParsed == ')':
            raise SyntaxError('unexpected )')
        
        parsed.append(newlyParsed)
    
    return tuple(parsed)

def recursiveParse(string, index):
    '''Produces an intelligible value by translating as much as possible from
        "string" starting at character "index".  Returns whatever was parsed and
        the index of the character after the translated portion.'''
    global functionToCall
    
    parsed = None
    
    if index < len(string):
        if string[index] in functionToCall:
            parsed, index = functionToCall[string[index]](string, index)
        else:
            parsed, index = handleLiteral(string, index)
        index = getIndexAfterTrailingWhitespace(string, index)
    
    return (parsed, index)

def handleCloseParens(string, index):
    return (string[index], index + 1)

def handleOpenParens(string, index):
    parsed = []
    innerResult = None
    index += 1
    
    while index < len(string):
        innerResult, index = recursiveParse(string, index)
        if innerResult == ')':
            break
        parsed.append(innerResult)
    
    if innerResult != ')':
        raise SyntaxError('unmatched (')
    
    return parsed, index

def handleString(string, index):
    global endQuote
    
    nextQuote = endQuote.search(string, index + 1)
    if nextQuote is None:
        raise SyntaxError('unmatched "')
    
    parsed = string[index + 1 : nextQuote.start()]
    return parsed.decode('string_escape'), nextQuote.end()

def handleQuote(string, index):
    quotedTerm, index = recursiveParse(string, index + 1)
    if quotedTerm in [')', None]:
        raise SyntaxError("misplaced '")
    return ["quote", quotedTerm], index

def handleLiteral(string, index):
    global literalTermination
    
    isTerminatedAt = literalTermination.search(string, index)
    if isTerminatedAt is None:
        parsed = atom(string[index:])
        index = len(string)
    else:
        parsed = atom(string[index:isTerminatedAt.start()])
        index = isTerminatedAt.start()
    
    return parsed, index

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

def getIndexAfterTrailingWhitespace(string, index):
    global whitespace
    
    isThereTrailingWhitespace = whitespace.match(string, index)
    if isThereTrailingWhitespace is not None:
        index = isThereTrailingWhitespace.end()
    
    return index

functionToCall = {
    ')': handleCloseParens,
    '(': handleOpenParens,
    '"': handleString,
    "'": handleQuote
}
endQuote = re.compile(r'(?<!\\)(")')
literalTermination = re.compile(r'((?:\s)|(?:\)))')
whitespace = re.compile(r'(\s+)')

############################### Lispy Evaluating ###############################

tracelist=[]
depth=0

def eval(x, env=global_env, check_trace=True):
    "Evaluate an expression in an environment."
    global tracelist
    global depth
    global couts
    global definately_dont_check_trace
    
    if definately_dont_check_trace:
        check_trace=False
    
    try: xstr=x[0].__str__()
    except Exception: xstr=False
    
    if xstr and counts.has_key(xstr) and check_trace:
        counts[xstr]+=1
    elif xstr and check_trace:
        counts.update({xstr:1})
        
    # Symbols --------------------------------------------------------------------
    # There are two "built-in" symbols, "nil" and "t".  "nil" is the empty list,
    # but also means "false". "t" means "true".
    if isa(x, Symbol):
        if x == 'nil':
            return list()
        elif x == 't':
            return True
        else:
            return env.find(x)[x] # This can raise a SymbolNotFound exception.
    
    # Strings --------------------------------------------------------------------
    # Note that this test has to come after the test for Symbols, because Symbol
    # is a subclass of str.
    elif isa(x, str):
        return x
    
    # Constant Literals ----------------------------------------------------------
    # In Lis.py, you either have macros (defined further down), forms, or literal
    # data.  Forms are wrapped in parentheses, and are parsed as lists.
    elif not isa(x, list):
        return x

    elif tracelist.__contains__(x[0]) and check_trace:
        #traced function
        white=" "*depth
        definately_dont_check_trace=True
        print "%s%i: (%s %s)"%(white, depth, x[0], ' '.join(eval(i, env).__str__() for i in x[1:]))
        definately_dont_check_trace=False
        depth+=1
        ret=eval(x, env, False)
        depth-=1
        print "%s%i: returned %s"%(white, depth, ret.__str__())
        return ret
    
    # Macros ---------------------------------------------------------------------
    # Macros are Lis.py commands that look like function calls but require special
    # processing to work.  They should be defined here so that function calls can
    # be the base case.
    elif x[0] == 'quote':
        # (quote x) returns x without processing it.  It allows for forms to be
        # literal lists, among other things.
        (_, exp) = x
        return exp
    
    elif x[0] == 'if':
        # (if test conseq [alt]) first evaluates "test" to see whether it evaluates
        # to "nil" (false).  If not, it evaluates "conseq" and returns that value.
        # If so, it evaluates "alt" and returns that value.
        #
        # Note that "if" has been modified to allow the "alt" argument to be
        # ignored.  In such a case, "nil" is returned when the "test" evaluates to
        # "nil".
        test = eval(x[1], env)
        if not isNil(test):
            return eval(x[2], env)
        elif len(x) == 3:
            return []
        else:
            return eval(x[3], env)
    
    elif x[0] == 'set!':
        # (set! var exp) evaluates an expression and stores its result in the
        # variable.
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    
    elif x[0] == 'define':
        # (define var exp) adds a variable in the global environment named "var" and
        # assigns it the value determined by evaluating the expression.
        #
        # Note that "define" has been modified.  It used to be that "define" was
        # used to create variables in the local scope.  However, this did not allow
        # for robust closures.  Now the macro "let" is used for introducing local
        # variables, and "define" can be used to define global variables anywhere in
        # the code.
        (_, var, exp) = x
        global_env[var] = eval(exp, env)
    
    elif x[0] == 'lambda':
        # (lambda (var*) exp) returns a lambda body that receives "var" arguments to
        # evaluate "exp".  It is how functions are made in Lispy.
        (_, vars, exp) = x
        return lambda *args: eval(exp, Env(vars, args, env))
    
    elif x[0] == 'begin':
        # (begin exp*) evaluates an arbitrary number of expressions in order, then
        # returns the value of the last one.
        for exp in x[1:]:
            val = eval(exp, env)
        return val
    
    # The above macros were defined by Norvig.  The rest are new.
    elif x[0] == 'let':
        # (let (decls*) form) declares local variables that exist for the evluation
        # of the passed form.  It returns whatever "form" evaluates to.
        #
        # A decl has one of two forms:
        #   decl -> var
        #   decl -> (var exp)
        #
        # In the first case, the local variable "var" will have the value "nil".  In
        # the second, "var" will be set to whatever value "exp" evaluates.
        #
        # Note that "let" is written so that whatever local variables you declare
        # will be visible to the subsequent local variables.  That way, you can use
        # them immediately if you'd like.
        nestedEnv = Env(outer=env)
        for local in x[1]:
            if isa(local, list):
                localVar = local[0]
                nestedEnv[localVar] = eval(local[1], nestedEnv)
            else:
                nestedEnv[local] = list()
        return eval(x[2], nestedEnv)
    
    elif x[0] == 'with':
        # (with (variable filename [mode]) form) opens a file, making it accessible
        # for evaluation as "variable", and keeps it open through the evaluation of
        # "form".  It returns whatever "form" evaluates to.
        #
        # "filename" must evaluate to either a local or absolute file path and name,
        # represented as a literal string.
        #
        # "mode" should be one of the modes acceptable to Python's open() function,
        # and defaults to "r" ("read") if no value is supplied.
        fileVar = x[1][0]
        fileName = eval(x[1][1], env)
        mode = "r" if len(x[1]) == 2 else eval(x[1][2], env)
        
        with open(fileName, mode) as theFile:
            nestedEnv = Env(outer=env)
            nestedEnv[fileVar] = theFile
            returnValue = eval(x[2], nestedEnv)
        
        return returnValue
    
    elif x[0] == 'dolines':
        # (dolines (variable filename) form) allows for evaluating a form over every
        # line in a file.  The string read in each iteration of the loop is stored
        # in "variable", and the file to be opened is specified by "filename".  This
        # returns whatever value the last iteration over form returns.
        iterVar = x[1][0]
        filename = eval(x[1][1], env)
        returnValue = None
        
        nestedEnv = Env(outer=env)
        try:
            with open(filename) as file:
                for line in file:
                    nestedEnv[iterVar] = line
                    returnValue = eval(x[2], nestedEnv)
            return returnValue
        except ShortCircuitReturn as e:
            return e.value
    
    elif x[0] == 'dolist':
        # (dolist (variable list [result]) form)
        # Evaluates form for each item in list, accessing the current element through
        # variable. If form does not evaluate a (return x) call, then result is returned.
        # Otherwise, the x from the (return x) is returned.
        iterVar = x[1][0]
        nestedEnv[iterVar] = x
        lst = eval(x[1][1], env)
        returnValue = None
        result = None
        if len(x[1]) > 2:
            result = x[1][2]
        try:
            for i in lst:
                nestedEnv[iterVar] = i
                returnValue = eval(x[2], nestedEnv)
            if not returnValue:
                return eval(result)
            else:
                return returnValue
        
        except ShortCircuitReturn as e:
            return e.value
    
    elif x[0] == 'dotimes':
        # (dotimes (variable maxValue [result]) form):
        # Evaluates form maxValue times. For each evaluation of form, variable
        # will contain a value in the range [0, maxValue). If form does not evaluate
        # a (return x) call, then result is returned. Otherwise, the x from the
        # (return x) is returned.
        iterVar = x[1][0]
        maxVal = eval(x[1][1])
        returnValue = None
        nestedEnv = Env(outer=env)
        result = None
        try:
            if len(x[1]) > 2:
                result = x[1][2]
            for v in range(0, maxVal):
                nestedEnv[iterVar] = v
                returnValue = eval(x[2], nestedEnv)
            return returnValue
        except ShortCircuitReturn as e:
            return e.value

    elif x[0] == 'and':
        # (and form*)
        # Returns True if all of the passed forms evaluate to non-empty lists or
        # if no forms are passed, and False otherwise.
        # form*: Zero or more forms to evaluate.
        form = eval(x[1])
        for i in form:
            if isNil(i):
                return False
        return True

    elif x[0] == 'or':
        # (or form*)
        # Returns True if at least one of the passed forms evaluate to non-empty lists, and False otherwise.
        # form*: Zero or more forms to evaluate.
        form = eval(x[1])
        for i in form:
            if not isNil(i):
                return True
        return False

    elif x[0] == 'trace':
        #Toggles Trace
        if tracelist.__contains__(x[1]):
            tracelist.remove(x[1])
        else:
            tracelist.append(x[1])
        print "(%s)"%x[1]
    
    elif x[0]=="count":
        if counts.has_key(x[1]):
            return counts[x[1]]
        else:
            return 0

    elif x[0]=='get':
        if(len(x) == 2):
            return globals()[x[1]]()
        else:
            env.update({x[2]:globals()[x[1]]()})

    elif x[0]=='preheat':
        eval(x[1]).preheat(x[2])

    elif x[0]=='addto':
        obj1=eval(x[1])
        if obj1.contents!=None:
            obj1.contents.append(eval(x[2]))
        else:
            raise cant_do_that("addto "+obj.__class__.__name__)

    elif x[0]=='crack':
        obj1=eval(x[1])
        if isinstance(obj1, Egg):
            obj1.crack()
        else:
            raise cant_do_that("crack "+obj.__class__.__name__)

    elif x[0]=='beat':
        obj1=eval(x[1])
        if isinstance(obj1, Egg):
            obj1.beat()
        else:
            raise cant_do_that("beat "+obj.__class__.__name__)

    elif x[0]=='peel':
        obj1=eval(x[1])
        if isinstance(obj1, Egg) or isinstance(obj1, Potato):
            obj1.peel()
        else:
            raise cant_do_that("peel "+obj.__class__.__name__)

    elif x[0]=='flip':
        obj1=eval(x[1])
        if isinstance(obj1,Egg) or isinstance(obj1, Bread):
            obj1.flip()
        else:
            raise cant_do_that("flip "+obj.__class__.__name__)

    elif x[0]=='melt':
        obj1=eval(x[1])
        if isinstance(obj1,Butter):
            obj1.melt()
        else:
            raise cant_do_that("melt "+obj.__class__.__name__)

    elif x[0]=='fold':
        obj1=eval(x[1])
        if isinstance(obj1,Egg):
            obj1.flip()
        else:
            raise cant_do_that("fold "+obj.__class__.__name__)

    elif x[0]=='cook':
        eval(x[1]).cook(eval(x[2]))

    elif x[0]=='display':
        eval(x[1]).longprint()

    elif x[0]=='move':
        obj1=eval(x[1])
        obj2=eval(x[2])
        if obj1.contents!=None and obj2.contents!=None:
            obj2.contents=obj1.contents
            obj1.contents=[]

    elif x[0]=='moveonly':
        obj1=eval(x[1])
        source=eval(x[2])
        dest=eval(x[3])
        if source.contents!=None and dest.contents!=None:
            source.contents.remove(obj1)
            dest.contents.append(obj1)


    # Functions ------------------------------------------------------------------
    # If all the previous checks have failed, then the current value must be an
    # unquoted form, which makes it a function call.  Evaluate all the functions'
    # arguments in order, then pass the evaluated arguments to the underlying
    # Python function.
    else:
        exps = [eval(exp, env) for exp in x]
        proc = exps.pop(0)
        return proc(*exps)


def isNil(value):
    return (
            value is None or \
            value is not 0 and (
                                (isinstance(value, list) and len(value) == 0) or \
                                value == False
                                )
            )

def lispyRead(filename, charCount=1):
    # (read file [charcount])
    # Reads the specified number of characters from the specified file object.
    # Returns a string of at most charcount characters if EOF has not been reached; otherwise, it returns nil.
    file = open(filename)
    s = file.read()
    if charCount > len(s):
        return 'nil'
    return s[0:charCount]


def readAll(filename):
    # (read-all file)
    # Returns the remaining contents of the file as a string, or nil if EOF has been reached.
    file = open(filename)
    s = file.read()
    if not s:
        return 'nil' #EOF
    return s

def readLine(filename):
    # (read-line file)
    # Returns a string containing all the characters from the current position in the file
    # up to and including the next line break.
    # If EOF has been reached, nil is returned.
    file = open(filename)
    s = file.readline()
    if not s:
        return 'nil'
    return s

def readLines(filename):
    # (read-lines file)
    # Returns a list of all the files lines from the current position.
    file = open(filename)
    s = file.readline()
    toReturn = []
    while s:
        toReturn.append(s)
        s = file.readline()
    return toReturn

def write(filename, val):
    # (write file value)
    # Writes a string representation of the passed value to the file. Returns None.
    file = open(filename, 'w')
    file.write(val)
    return None

def lispyMap(function, lst):
    # (map function list+)
    # Builds a new list where each element is the result of calling function on the current tuple of elements from the passed lists.
    toReturn = []
    for i in lst[:-1]:
        toReturn.append(function(i, i+1))
    return toReturn

def lispyReduce(function, lst, initalValue=None):
    # (reduce function list [initialValue]):
    # Calculates and returns some aggregate value by applying function to every item in list.
    # For example, (reduce + '(1 2 3 4)) returns 10. In the case of an exception, return an empty list.
    cntr = 0
    if initalValue == None:
        initalValue = lst[cntr]
        cntr = 1
        initalValue = function(initalValue, lst[cntr])
        cntr = 2
    for i in lst[cntr:]:
        initalValue = function(initalValue, i)
    return initalValue

################################ Lispy Printing ################################
def to_string(exp, printStringRepresentation=True):
    "Convert a Python object back into a Lisp-readable string."
    if isNil(exp):
        return 'nil'
    elif exp is not 1 and exp == True:
        return 't'
    elif isa(exp, str) and not isa(exp, Symbol):
        if printStringRepresentation:
            return '"%s"' % exp.__repr__()[1:-1]
        else:
            return exp
    return '('+' '.join(map(to_string, exp))+')' if isa(exp, list) else str(exp)

################################## Lispy REPL ##################################
def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop."
    while True:
        for part in parse(raw_input(prompt)):
            if part == 'exit':
                return
            
            try:
                val = eval(part)
            except ShortCircuitReturn as e:
                val = e.value
            except SymbolNotFound as e:
                val = None
                print "--ERROR: could not find '{}'".format(e.symbol)
            
            if val is not None:
                print to_string(val)

##################################### Main #####################################
if __name__ == '__main__':
    global_env.update({'read': lispyRead,
                      'read-all': readAll,
                      'read-line': readLine,
                      'read-lines': readLines,
                      'write': write,
                      'map': lispyMap,
                      'reduce': lispyReduce            
                      })
    
    
    repl()

