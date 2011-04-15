#! /usr/bin/python

import sys

# Workaround for windows - DISABLED
#try: import lib.winunicode
#except ImportError: pass
#else: del lib.winunicode

import re
import apsw
import functions

if sys.platform == "win32":
    import pyreadline as readline
else:
    import readline

import datetime
import lib.reimport
import locale
import os

from lib.dsv import writer
import csv

class mtermoutput(csv.Dialect):
    def __init__(self):
        self.delimiter='|'
#        self.doublequote=True
        self.quotechar='|'
        self.quoting=csv.QUOTE_MINIMAL
        self.escapechar="\\"
        self.lineterminator='\n'

def reloadfunctions():
    global connection, automatic_reload

    if not automatic_reload:
        return

    modified=lib.reimport.modified()

    if len(modified)==0 or (modified==['__main__']):
        return

    tmp_settings=functions.settings
    tmp_vars=functions.variables
    connection.close()
    lib.reimport.reimport(functions)
    connection = functions.Connection(db)
    functions.settings=tmp_settings
    functions.variables=tmp_vars
    functions.register(connection)

def raw_input_no_history(*args):
    try:
        input = raw_input(*args)
    except:
        return None
    if input!='':
        try:
            readline.remove_history_item(readline.get_current_history_length()-1)
        except:
            pass
    return input

def update_tablelist():
    global alltables, alltablescompl, connection
    alltables=[]
    alltablescompl=[]
    cursor = connection.cursor()
    cexec=cursor.execute('PRAGMA database_list;')
    for row in cexec:
        if row[1]!='temp':
            cursor1 = connection.cursor()
            cexec1 = cursor1.execute("select name from "+row[1]+".sqlite_master where type='table';")
            for row1 in cexec1:
                tname=row1[0].lower().encode('ascii')
                if row[1]=='main':
                    alltables.append(tname)
                    alltablescompl.append(tname)
                else:
                    dbtname=(row[1]+'.'+tname).lower().encode('ascii')
                    alltables.append(dbtname)
                    alltablescompl.append(dbtname)
                    if tname not in alltablescompl:
                        alltablescompl.append(tname)
            cursor1.close()
    cursor.close()

def update_cols_for_table(t):
    global alltablescompl, colscompl, lastcols, connection

    if t!='':
        if t[-1]=='.':
            t=t[0:-1]
        if t[-2:]=='..':
            t=t[0:-2]

    if t in alltablescompl:
        cursor = connection.cursor()
        cexec=cursor.execute('select * from '+str(t))
        try:
            desc=cursor.getdescription()
            colscompl+= ['.'.join([ t, x ]) for x, y in desc]
            colscompl+= [x for x,y in desc]
            colscompl=list(set(colscompl)-set(lastcols))
        except:
            pass

def normalizename(col):
    if re.match(ur'[\w_$\d.]+$', col,re.UNICODE):
        return col
    else:
        return "`"+col.lower()+"`"

def mcomplete(textin,state):
    text=textin

    #Complete \t to tabs
    if text[-2:]=='\\t':
        if state==0:
            return text[:-2]+'\t'
        else:
            return
        
    postfix=''
    prefix=''
    tail=''
    if text!='':
        if text[-1]=='.':
            tail='..'

    localtables=[]

    beforecompl= readline.get_line_buffer()[0:readline.get_begidx()]

    #If completition starts at a string boundary, complete from local dir
    if beforecompl!='' and beforecompl[-1] in ("'", '"'):
        completitions=os.listdir(os.getcwdu())
    #Detect if in simplified 'from' or .schema
    elif re.search(r'(?i)(from\s(?:\s*[\w\d._$]+(?:\s*,\s*))*(?:\s*[\w\d._$]+)?$)|(^\s*\.schema)', beforecompl, re.DOTALL| re.UNICODE):
        localtables=alltablescompl[:]
        completitions=localtables
    else:
        localtables=[x+tail for x in alltablescompl]
        completitions=lastcols[:]+colscompl
        completitions+=sqlandmtermstatements+allfuncs+localtables

    hits= [x.lower() for x in completitions if x.lower()[:len(text)]==unicode(text.lower())]

    #If completing something that looks like a table, complete only from cols
    if hits==[] and text[-2:]!='..':
        prepost=re.match(r'(.+\.)([^.]*)$', text)
        if prepost:
            prefix, text=prepost.groups()
            hits= [x.lower() for x in lastcols+[y for y in colscompl if y.find('.')==-1] if x.lower()[:len(text)]==unicode(text.lower())]

    if state<len(hits):
        sqlstatem=set(sqlandmtermstatements)
        altset=set(localtables)
        if hits[state]=='..':
            if text=='..' and lastcols!=[]:
                return prefix+', '.join([normalizename(x) for x in lastcols])+' '
            else:
                return prefix+hits[state]
        if hits[state] in sqlstatem:
            return prefix+hits[state]+' '
        if hits[state] in altset:
            update_cols_for_table(text)
            if text[-2:]=='..':
                tname=text[:-2]
                cursor = connection.cursor()
                cexec=cursor.execute('select * from '+str(tname))
                try:
                    return prefix+', '.join([x for x,y in cursor.getdescription()])+' '
                except:
                    pass
            return prefix+hits[state]
        else:
            return prefix+normalizename(hits[state])
    else:
        return

def schemaprint(cols):
    if cols!=[]:
        print "--- Column names ---"
        colstoprint="| "+" | ".join([x for x in cols])+" |"
        if len(colstoprint)<=80:
            print colstoprint
        else:
            print "| "+" | ".join([x[0:10]+".." if len(x)>12 and len(cols)>1 else x for x in cols])+" |"


mtermdetails="mTerm - version 0.8"
intromessage="""Enter ".help" for instructions
Enter SQL statements terminated with a ";" """

helpmessage=""".functions             Lists all functions
.help                  Show this message (also accepts '.h' )
.help FUNCTION         Show FUNCTION's help page
.output FILENAME       Send output to FILENAME
.output stdout         Send output to the screen
.quit                  Exit this program
.schema ?TABLE?        Show the CREATE statements
.separator STRING      Change separator used by output mode and .import   
.tables                List names of tables """

if 'HOME' not in os.environ: # Windows systems
        if 'HOMEDRIVE' in os.environ and 'HOMEPATH' in os.environ:
                os.environ['HOME'] = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
        else:
                os.environ['HOME'] = "C:\\"

histfile = os.path.join(os.environ["HOME"], ".mterm")

try:
    readline.read_history_file(histfile)
except IOError:
    pass
import atexit
atexit.register(readline.write_history_file, histfile)

output = sys.stdout
separator = "|"
db = ""
automatic_reload=True
language, output_encoding = locale.getdefaultlocale()

if len(sys.argv) >= 2:
    db = sys.argv[1]
    if db=="-q":
        db=':memory:'

connection = functions.Connection(db)

if db=='' or db==':memory':
    functions.variables.execdb=None
else:
    functions.variables.execdb=str(os.path.abspath(os.path.expandvars(os.path.expanduser(os.path.normcase(db)))))
    
try:
    functions.register(connection)
except apsw.BusyError,e:
    print e
    exit(0)

functions.variables.flowname='main'

if len(sys.argv)>2:
        
    statement=' '.join(sys.argv[2:])
    statement = statement.decode(output_encoding)
        
    printer=writer(output,dialect=mtermoutput(),delimiter=separator)
    cursor = connection.cursor()
    try:
        for row in cursor.execute(statement):
            printer.writerow(row)
        cursor.close()
    except KeyboardInterrupt:
        sys.exit()
    finally:
        try:
            cursor.close()
        except:
            pass
    sys.exit()

sqlandmtermstatements=['select', 'create', 'where', 'table', 'group', 'drop', 'order', 'index', 'from', 'alter', 'limit', 'delete',
                        '.help', '.colnames', '.schema', '.functions', '.tables', '..']
allfuncs=functions.functions['vtable'].keys()+functions.functions['row'].keys()+functions.functions['aggregate'].keys()
alltables=[]
alltablescompl=[]
update_tablelist()
lastcols=[]
colscompl=[]

readline.set_completer(mcomplete)
readline.parse_and_bind("tab: complete")
readline.set_completer_delims(' \t\n`!@#$^&*()=+[{]}|;:\'",<>?')

#Intro Message
print mtermdetails
print "running on Python: "+'.'.join([str(x) for x in sys.version_info[0:3]])+', APSW: '+apsw.apswversion()+', SQLite: '+apsw.sqlitelibversion()
print intromessage


number_of_kb_exceptions=0
while True:
    statement = raw_input_no_history("mterm> ")
    if statement==None:
        number_of_kb_exceptions+=1
        print
        if number_of_kb_exceptions<2:
            continue
        else:
            break
    number_of_kb_exceptions=0
    statement=statement.decode(output_encoding)
    iscommand=re.match("\s*\.(?P<command>\w+)\s*(?P<argument>([\w\.]*))\s*;?\s*$", statement)
    validcommand=False

    if iscommand:
        validcommand=True
        command=iscommand.group('command')
        argument=iscommand.group('argument')        
        statement=None
        if command=='mode' and argument=='csv':            
            separator = ","
        elif command=='mode' and argument=='tabs':
            separator = "\t"
        elif command=='separator' and argument:
            separator=argument
            if not argument.startswith("'") or not argument.endswith("'"):
                if not argument.startswith('"') or not argument.endswith('"'):
                    argument='"'+argument+'"'
            try:
                separator = eval(argument)
            except Exception:
                print "Cannot parse separator value"

        elif command=='output':
            if output!=sys.stdout:
                    output.close()
            if argument=="stdout":         
                    output=sys.stdout
            else:
                output=open(argument,"w")

        elif 'tables'.startswith(command):
            update_tablelist()
            for i in alltables:
                print i
           
        elif command=='colnames':
                if argument:
                    names=[]
                    cursor = connection.cursor()
                    for cid,name,type,notnull,defaultv,pk in cursor.execute("pragma table_info(%s)" %(argument)):
                        names+=[name]
                    cursor.close()
                    printer=writer(output,dialect=mtermoutput(),delimiter=separator)
                    printer.writerow(names)

        elif command=='schema':
            if not argument:
                statement="select sql from sqlite_master where sql is not null;"
            else:
                argument=argument.rstrip('; ')
                update_tablelist()
                if argument not in alltables:
                    print "No table found"
                else:
                    db='main'
                    if '.' in argument:
                        sa=argument.split('.')
                        db=sa[0]
                        argument=''.join(sa[1:])
                    statement="select sql from "+db+".sqlite_master where tbl_name like '%s' and sql is not null;" %(argument)
        elif "quit".startswith(command):
            connection.close()
            exit(0)
        elif command=="functions":
            for type in functions.functions:
                for f in functions.functions[type]:
                    print f+' :'+type
        elif "help".startswith(command):
            if not argument:
                print helpmessage
            else:
                for type in functions.functions:
                    if argument in functions.functions[type]:
                        print "Function "+ argument + ":"
                        print functions.functions[type][argument].__doc__
        elif command=="autoreload":
            automatic_reload=automatic_reload ^ True
            print "Automatic reload is now: " + str(automatic_reload)
        else:
            validcommand=False
            print """unknown command. Enter ".help" for help"""

        if validcommand:
            histstatement='.'+command+' '+argument
            try:
                readline.add_history(histstatement.encode('utf-8'))
            except:
                pass

    if statement:
        histstatement=statement
        while not apsw.complete(statement):
            more = raw_input_no_history("  ..> ")
            if more==None:
                statement=None
                break
            more=more.decode(output_encoding)
            statement = statement + '\n'.decode(output_encoding) + more
            histstatement=histstatement+' '+more

        reloadfunctions()
        number_of_kb_exceptions=0
        if not statement:
            print
            continue
        try:
            if not validcommand:
                readline.add_history(histstatement.encode('utf-8'))
        except:
            pass

        before=datetime.datetime.now()
        printer=writer(output,dialect=mtermoutput(),delimiter=separator)
        cursor = connection.cursor()
        try:
            cexec=cursor.execute(statement)

            try:
                lastcols=[x for x,y in cursor.getdescription()]
            except apsw.ExecutionCompleteError, e:
                lastcols=[]

            for row in cexec:
                printer.writerow(row)
            cursor.close()

            after=datetime.datetime.now()
            tmdiff=after-before

            schemaprint(lastcols)
            print "Query executed in %s min. %s sec %s msec" %((int(tmdiff.days)*24*60+(int(tmdiff.seconds)/60),(int(tmdiff.seconds)%60),(int(tmdiff.microseconds)/1000)))
            if functions.settings['beep']:
                print '\a'
            colscompl=[]

            #Autoupdate in case of schema change
            if re.search(r'(?i)(create|attach)', statement):
                update_tablelist()

        except KeyboardInterrupt:
            schemaprint(lastcols)
            print "KeyboardInterrupt exception: Query execution stopped"
            continue
        except (apsw.SQLError, apsw.ConstraintError , functions.MadisError), e:
            print e
            continue
        except Exception, e:
            print "Unknown error:"+functions.mstr(e)
            #raise
        finally:
            try:
                cursor.close()
            except:
                #print "Not proper clean-up"
                pass

