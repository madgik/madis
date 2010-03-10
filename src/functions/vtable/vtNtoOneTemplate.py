import setpath          #for importing from project root directory  KEEP IT IN FIRST LINE
from vtout import SourceNtoOne


 #UNCOMMENT TO REGISTER THE N to 1 OPERATOR
#registered=True

__doc__=\
"""
Document the operation
"""




def yourfunction(diter,*args,**kargs):
    ## diter is an iterator over table results 
    ## diter returns a tuple of the row and a list of tuples with columnname and type
    ##Your code here
    pass


boolargs=['booleantag1']
nonstringargs={'tag':{'val':'replaceval'}}


def Source():
    global boolargs, nonstringargs
    return SourceNtoOne(yourfunction,boolargs, nonstringargs)