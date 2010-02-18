def getElementSqliteType(element):
    if 'int' in str(type(element)):
        return "integer"
    if 'buffer' in str(type(element)):
        return "blob"
    if 'float' in str(type(element)):
        return "real"
    if ('str' in str(type(element))) or ('unicode' in str(type(element))) :
        return "text"
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