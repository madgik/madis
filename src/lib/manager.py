import logging

def LogFormat(logfile):
    logging.basicConfig(filename=logfile,level=logging.NOTSET,format="%(asctime)s - %(name)s - %(flowname)s - %(levelname)s - %(message)s")

SQLITE=0
class DBhandler:
    def __init__(self,type,sqlitefl=None,host=None,user=None,password=None,dbname=None):
        self.connection=None
        self.type=type
        self.preparedstatementstring="""%s"""
        if type==SQLITE:
            import apsw
            self.connection=apsw.Connection(sqlitefl)
            self.preparedstatementstring="?"
    def getconnection(self):
        return self.connection

    def getdate2string(self,colname,alias):
        if self.type==SQLITE:
            return " strftime('%s',%s) as %s " %("%s",colname,alias)


    #The following 2 functions and return a list of sql statements that  reverse the action they do
    #drops indexes on the columnlst attributes ALL and maybe more than them (not any of the columnlst attributes)
    def drop_ind_if_exists(self,tablename,columnlst):
        recoverlst=[]
        if self.type==SQLITE:
            cr1=self.getconnection().cursor()
            cr2=self.getconnection().cursor()
            dropstmt=[]
            for indname,sqlstmt in cr1.execute("select name,sql from sqlite_master where tbl_name='%s' and type='index' and name not like 'sqlite_autoindex%%'" %(tablename)):
                #columns=[]
                #for indinfo in cr2.execute("pragma index_info(%s)" %(indname)):
                #    columns+=[indinfo[2]] #column that participate in the index
                columns=[indinfo[2] for indinfo in cr2.execute("pragma index_info(%s)" %(indname))]
                relatedindex=True
                for i in columnlst:
                    if i not in columns:
                        relatedindex=False
                if relatedindex:
                    recoverlst+=[sqlstmt]
                    dropstmt=["drop index %s" %(indname)]
            for drs in dropstmt:
                cr2.execute(drs)
            cr1.close()
            cr2.close()
            return recoverlst
        return recoverlst

    def drop_all_ind(self,tablename):
        recoverlst=[]
        if self.type==SQLITE:
            cr1=self.getconnection().cursor()
            cr2=self.getconnection().cursor()
            dropstmt=[]
            for indname,sqlstmt in cr1.execute("select name,sql from sqlite_master where tbl_name='%s' and type='index' and name not like 'sqlite_autoindex%%'" %(tablename)):
                #columns=[]
                #for indinfo in cr2.execute("pragma index_info(%s)" %(indname)):
                #    columns+=[indinfo[2]] #column that participate in the index
                columns=[indinfo[2] for indinfo in cr2.execute("pragma index_info(%s)" %(indname))]
                recoverlst+=[sqlstmt]
                dropstmt=["drop index %s" %(indname)]
            for drs in dropstmt:
                cr2.execute(drs)
            cr1.close()
            cr2.close()
            return recoverlst
        return recoverlst


    #creates index on the columnlst attributes ALL (not in subset of the columnlst attributes)
    def create_ind_if_not_exists(self,tablename,columnlst):
        recoverlst=[]
        if self.type==SQLITE:
            cr1=self.getconnection().cursor()
            cr2=self.getconnection().cursor()
            relatedindex=False
            for indname,sqlstmt in cr1.execute("select name,sql from sqlite_master where tbl_name='%s' and type='index'" %(tablename)):
                #columns=[]
                #for indinfo in cr2.execute("pragma index_info(%s)" %(indname)):
                #    columns+=[indinfo[2]] #column that participate in the index
                columns=[indinfo[2] for indinfo in cr2.execute("pragma index_info(%s)" %(indname))]
                if(set(columns)==set(columnlst)):
                    relatedindex=True
                    break
            if not relatedindex:
                indexname="Index"+unique_string()
                crstmt="create index %s on %s(%s)" %(indexname,tablename,",".join(columnlst))
                drstmt="drop index %s" %(indexname)
                recoverlst+=[drstmt]
                cr2.execute(crstmt)
            cr1.close()
            cr2.close()
            return recoverlst
        return recoverlst

    def gettablecolumns(self,tablename): #if table not exists returns []
        names=[]
        cursor=self.getconnection().cursor()

        #cursor.execute("select * from %s limit 1" %(tablename))
        if self.type==SQLITE:
            query="pragma table_info(%s)" %(tablename)
            for row in cursor.execute(query):
                names+=[row[1]]
            return names
        return names

    def makeprinsertstmt(self,table,valnum,tbcols=None):
        s="("+','.join([self.preparedstatementstring]*int(valnum))+")"
        if not tbcols:
            return "INSERT INTO %s VALUES %s" %(table,s)
        return "INSERT INTO %s(%s) VALUES %s" %(table,unicode(", ").join(tbcols),s)


def unique_string():
    import time
    return str(time.time()).replace(".","")

