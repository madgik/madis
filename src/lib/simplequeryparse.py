
from pyparsing import Literal, CaselessLiteral, Word, Upcase, delimitedList, Optional, \
    Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, quotedString, \
    ZeroOrMore, restOfLine, Keyword

def recdictflatten(el,top,dictattr):    
    lst=[]
    try:
        lst+=list(el[dictattr])
    except KeyError:
        pass
    try:        
        lst+=recdictflatten(el[top],top,dictattr)
    except KeyError:
        pass
    return lst

def dependencytbs( query ):
    try:
        tokens = simpleSQL.parseString( query )
        return recdictflatten(tokens.asDict(),"tablel",'tables')
    except ParseException, err:
        #print " "*err.loc + "^\n" + err.msg
        #print err
        return False




# define SQL tokens
selectStmt = Forward()
selectToken = Keyword("select", caseless=True)
fromToken   = Keyword("from", caseless=True)

ident          = Word( alphas, alphanums + "_$" ).setName("identifier")
tableName      = delimitedList( ident, ".", combine=True ) 
tt=tableName.setResultsName( "tables" ,listAllMatches=True)
fromplace=  tt  | ( "(" + selectStmt + ")")
tableNameList  = Group( delimitedList( fromplace ) )

# define the grammar
selectStmt      << ( selectToken + '*'  + fromToken + tableNameList.setResultsName( "tablel") )

simpleSQL =  "'" + 'query:' + selectStmt + "'"


