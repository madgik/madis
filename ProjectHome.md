# About #

[madIS](http://doc.madis.googlecode.com/hg/index.html) is an extensible relational database system built on top of the [SQLite](http://www.sqlite.org/) database with extensions implemented in Python (via [APSW](http://code.google.com/p/apsw/) SQLite wrapper).

In usage, madIS, feels like **Hive** (**Hadoop**'s SQL with User Defined Functions language), without the overhead but also without the distributed processing capabilities. Nevertheless madIS can easily handle tens of millions of rows on a single desktop/laptop computer.

madIS' main goal is to promote the handling of data related tasks within an extended relational model. In doing so, it upgrades the database, from having a support role (storing and retrieving data), to being a full data processing system on its own. madIS comes with functions for file import/export, keyword analysis, data mining tasks, fast indexing, pivoting, statistics and workflow execution.

madIS was designed and implemented by a small team of developers at the MaDgIK lab of the University of Athens, under the supervision of professor Yannis Ioannidis.

# News #
  * 2013-05-14 - Version 1.7 is released:
    * Many bug fixes and optimizations. madIS works better now with SQLite versions before 3.7.11.
    * Major cleanup/simplification of the Virtual Table operators. Most of the operators have been converted to using **vtbase.py**.
    * Added [UNINDEXED](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.unindexed) virtual table, which forces SQLite engine to access its embedded query without using indexes.
    * Added [ORDERED](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.ordered) virtual table, which hints to SQLite engine that the embedded query' results are already sorted, so it can do a **GROUP BY** operation on these, without constructing an index on them first.
    * Added functions userfull for text mining. These are [TEXTWINDOW](http://doc.madis.googlecode.com/hg/row.html#module-functions.row.text), which produces a rolling window over an input text, [REGEXPCOUNTWITHPOSITIONS](http://doc.madis.googlecode.com/hg/row.html#module-functions.row.text) and [REGEXPCOUNTWORDS](http://doc.madis.googlecode.com/hg/row.html#module-functions.row.text), which match regular expression patterns to text in different ways.

  * 2012-06-08 - Version 1.6 is released:
    * Bug fixes to madIS I/O engine. madIS I/O engine is now up to 3 times faster.
    * Added a line based JSON streaming format to [OUTPUT](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.output) and [FILE](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.file). The JSON format, by default, preserves schema and type info of data.
    * Added "strict" option to [FILE](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.file) that works in the same manner as [XMLPARSE](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.xmlparse)'s one.
    * Added [DATE2ISO](http://doc.madis.googlecode.com/hg/row.html#module-functions.row.date) row function. The function autodetects the format of an input date and converts it to ISO8601 date format.

  * 2012-03-16 - Version 1.5 is released:
    * More robust [XMLPARSE](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.xmlparse).
    * Added [EXECPROGRAM, GZ and UNGZ](http://doc.madis.googlecode.com/hg/row.html#module-functions.row.util) utility functions.
    * Added [GRAPHPOWERHASH and GRAPHTODOT](http://doc.madis.googlecode.com/hg/aggregate.html#module-functions.aggregate.graph) functions. GRAPHPOWERHASH is an experimental function that can be used for graph isomorphism (such as finding same chemical molecules) and graph similarity problems (such as finding similar molecules or same molecule parts).
    * [PEARSON, STDEV and VARIANCE](http://doc.madis.googlecode.com/hg/aggregate.html#module-functions.aggregate.statistics) functions now use arbitrary precision fraction arithmetic for maximum calculation accuracy.
    * Added harvesting and processing examples. The examples are based on data/services from [DBLP](http://code.google.com/p/madis/source/browse/#hg%2Fsrc%2Fexamples%2Fdblp), [CiteSeerX](http://code.google.com/p/madis/source/browse/#hg%2Fsrc%2Fexamples%2Fciteseer) and [DIAVGEIA](http://code.google.com/p/madis/source/browse/#hg%2Fsrc%2Fexamples%2Fdiavgeia).
    * [OUTPUT](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.output) can now directly export to one (or split to many) external SQLite DB.
    * Added [HASHMD5MOD and CRC32](http://doc.madis.googlecode.com/hg/row.html#module-functions.row.text) functions.

  * 2011-12-08 - Version 1.4 is released:
    * [XMLPARSE](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.xmlparse) can now work without any provided prototype, producing JSON dicts which contain all parsed XML data. XMLPARSE accepts now Jdicts and Jlists in addition to XML snippets as prototypes.
    * [FILE](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.file) works with gzip compressed files, HTTP and FTP streams directly in a streaming way.
    * New functions which work with Jdicts were added (jdictkeys, jdictvals, jdictsplit, jdictgroupunion).
    * [APACHELOGSPLIT](http://doc.madis.googlecode.com/hg/row.html?highlight=apachelog#functions.row.logparse.apachelogsplit) parses and splits Apache log lines.
    * Optimizations in Virtual Tables (up to 3 times faster). XMLPARSE is up to 2x faster (using _fast:1_ switch).

  * 2011-07-18 - Version 1.3 is released:
    * [XMLPARSE](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.xmlparse) was added. XMLPARSE processes its input in a streaming fashion, and has been tested with very large (~20+ GB) XML source files without problems.
    * [JPACK functions](http://doc.madis.googlecode.com/hg/row.html#module-functions.row.jpacks) were added. Jpacks are now the preferable way to store a set of values into a single tuple. For easy viewing and exporting of the jpacks, their format was based on the [JSON](http://www.json.org) format.
    * Heavy testing under Windows and Mac OSX. [CLIPBOARD](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.clipboard) and [CLIPOUT](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.clipout) virtual tables work under all OSes.
    * CLIPOUT and CLIPBOARD, have been tested with Excel, Libre/Open Office Calc, and iWork Numbers.
    * Functions that return tables, can easily be coded now, by using Python's generators (yield)
    * A lot of completions (via TAB) have been added to mterm. Mterm's completion engine can automatically complete, tables, column names, table index names and database filenames in **attach database**.

  * 2010-07-09 - Version 1.2 is released:
    * [WEBTABLE](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.webtable) and [CLIPBOARD](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.clipboard)(untested under windows) virtual tables were added.
    * The PEARSON correlation function was added in the [aggregate statistics functions](http://doc.madis.googlecode.com/hg/aggregate.html#module-functions.aggregate.statistics)
    * Various other fixes.

  * 2010-04-29 - Version 1.1 is released:
    * [FILE](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.file) function can read now, non-UTF8 files via 'encoding' parameter.
    * [CACHE](http://doc.madis.googlecode.com/hg/vtable.html#module-functions.vtable.cache) function, requires less memory now.
    * Various fixes.

# madIS is suitable for #

## Complex data analysis tasks ##

With madIS it is very easy to create additional relational functions, or join against external files without first importing them into the database.

madIS also offers a very fast multidimensional index that greatly speeds up multi-constraint joins, even when joining against external sources.

## Data transformations ##

madIS can already use the file system or network sources as tables. In addition, with a little knowledge of Python, complex data transformation functions can be created and used inside the database. All these can be achieved without having to import the data in the database.

In addition madIS offers an easy to work with, workflow engine that automates data transformation steps.

## Database research ##

You can easily develop and test a new indexing structure with madIS, as it uses Python for its extensions and already has plenty of code to start from.

# Documentation #

You'll find madIS [documentation here](http://doc.madis.googlecode.com/hg/index.html).

# Download #

You can download the latest madIS version from [madIS download page](http://code.google.com/p/madis/downloads/list). You should also take a look at [madIS installation instructions](http://doc.madis.googlecode.com/hg/install.html).

# Screenshot #

![http://doc.madis.googlecode.com/hg/_static/madis-screen.png](http://doc.madis.googlecode.com/hg/_static/madis-screen.png)