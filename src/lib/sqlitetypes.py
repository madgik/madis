def getElementSqliteType(element):
    elemtype=type(element)
    if elemtype==int:
        return "integer"
    if elemtype==float:
        return "real"
    if elemtype==str or elemtype==unicode:
        return 'text'
    if elemtype==buffer:
        return "blob"
    return "none"

def typestoSqliteTypes(type):
    type=str(type).upper()
    if type=="TEXT" or type=="INTEGER" or type=="REAL" or type=="NONE" or  type=="NUMERIC":
        return type
    if "INT" in type:
        return "INTEGER"
    if "CHAR" in type or "CLOB" in type or "TEXT" in type:
        return "TEXT"
    if "BLOB" in type or type=="":
        return "NONE"
    if "REAL" in type or "FLOA" in type or "DOUB" in type:
        return "REAL"
    return "NUMERIC"