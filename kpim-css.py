#!/usr/bin/env python3
# -*- coding=utf-8 -*-
import kpim
import argparse
from sys import argv
from os.path import basename, isfile
from colorama import init, Fore, Back, Style

# colorama autoreset
init(autoreset=True)

__version__="0.1"

# CheatSheet - CSS
table_name='CSS'
table_version="0.1"
table_creation="CREATE TABLE CSS (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                categ TEXT,  \
                subcateg TEXT, \
                cmd TEXT, \
                description TEXT, \
                creationdt DATE)"
arg_desc='Kpim-css \
        \nCreated by Kalyparker \
        \nTool for writing and retrieving cheatsheet in cmdline'
listing_query="select distinct categ, subcateg from CSS order by 1,2"
search_content="select * from \
              (select * from CSS where cmd like '%{search}%' \
              union \
              select * from CSS where description like '%{search}%')\
              order by categ, subcateg"
search_content_categ="select * from \
                    (select * from CSS where cmd like '%{search}%' \
                    and categ like '%{categ}%' \
                    union \
                    select * from CSS where description like '%{search}%' \
                    and categ like '%{categ}%' )\
                    order by categ, subcateg" 
search_categ="select * from CSS where categ like '%{categ}%' \
            order by categ, subcateg"
search_content_categ_subcateg="select * from \
                  (select * from CSS where cmd like '%{search}%' \
                  and categ like '%{categ}%' \
                  and subcateg like '%{subcateg}%' \
                  union \
                  select * from CSS where description like '%{search}%' \
                  and categ like '%{categ}%' \
                  and subcateg like '%{subcateg}%') \
                  order by categ, subcateg" 
search_categ_subcateg="select * from CSS \
                  where categ like '%{categ}%' \
                  and subcateg like '%{subcateg}%' \
                  order by categ, subcateg"
search_subcateg="select * from CSS where subcateg like '%{subcateg}%' \
                  order by categ, subcateg"
search_content_subcateg="select * from \
                  (select * from CSS where cmd like '%{search}%' \
                  and subcateg like '%{subcateg}%' \
                  union \
                  select * from CSS where description like '%{search}%' \
                  and subcateg like '%{subcateg}%' )\
                  order by categ, subcateg"              
insert_css="INSERT INTO CSS (categ,subcateg,cmd,description,creationdt) VALUES ('{categ}','{subcateg}','{cmd}','{description}','{creationdt}')"
 


def check_args():
    """
    Check args
    -v: check version
    -h: help
    -i: Initialisation
    -l: list categories and subcategories
    -s: search content
    -c: filter on category
    -sub: filter on subcategory
    -add: add new cheatsheet
    -del: delete a precise cheatsheet
    """
    create_db = False
    listCateg = False
    searchcontent = ''
    filtercategory = ''
    filtersubcategory = ''
    addrow = ''
    delrow=''



    parser = argparse.ArgumentParser(description=arg_desc,formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v','--version',action='version',version=basename(argv[0]) + ' version: ' + __version__)
    parser.add_argument('-i', '--init', help="Initialisation - create table", action="store_true")
    parser.add_argument('-l', '--listcateg', help="List All categories and subcategories", action="store_true")
    parser.add_argument('-s', '--search', help="Search content")
    parser.add_argument('-c', '--category', help="Filter on category")
    parser.add_argument('-sub', '--subcategory', help="Filter on subcategory")
    parser.add_argument('-add', help="add row. Syntax: kpim-css.py -add 'categ,subcateg,description,cmd'")
    parser.add_argument('-del', '--delete',help="del row. Syntax: kpim-css.py -del 'categ,subcateg,description,cmd'")
    args = parser.parse_args()

    if len(argv)==1:
        parser.print_help()
        exit(1)

    # Init - creation of DB
    if args.init:
        if isfile(kpim.DBNAME):
            # file exist
            # test if table CSS exist
            try:
                ver = kpim.check_version(table_name)
                # if ver is empty, CSS is not register in VERSION table
                if len(ver) == 0:
                    exist = kpim.check_table(table_name)
                    # if exist is empty, table CSS does not exist
                    if len(exist) == 0:
                        create_db = True
            except:
                print('Database',kpim.DBNAME,'already exists')
                exit(1)
        else:
            create_db = True 

    # list all category
    if args.listcateg:
        listCateg = True

    # search content
    if args.search:
        searchcontent = args.search
        
    # filter on category
    if args.category:
        filtercategory=args.category

    # filter on subcategory
    if args.subcategory:
        filtersubcategory=args.subcategory        
        
    # add row
    if args.add:
        addrow = (args.add).split(',')

    # del row
    if args.delete:
        delrow = (args.delete).split(',')
        
    return create_db, listCateg, searchcontent, filtercategory, filtersubcategory, addrow, delrow


def create_base(version):
    """
    Database Creation
    VERSION if not exist (script in kpim)
    CSS (id, categ, subcateg, cmd, description, creationdt)
    """
    try:
        # test if VERSION exist
        exist = kpim.check_table('VERSION')
        if len(exist) == 0:
            # VERSION does not exist - create table
            if not (kpim.create_version()):
                print('Error in creation of version table')
                exit(1)
        # insert version of CSS
        if not (kpim.add_version(table_version, table_name)):
            print('Error in insertion of version table')
            exit(1)
        
        # Create table CSS
        if not (kpim.execdml(table_creation)):
            print('Error in creation of CSS table')
            exit(1)
    except:
        print('Error during the db creation')
        exit(1)
  
def check_base(version):
    """
    Check Database
    db version identical DB and Script?
    tables exist?
    """
    try:
        ver = kpim.check_version(table_name)
        # if ver is empty, CSS is not register in VERSION table
        if (len(ver) == 0) or (ver[0][0] != table_version):
            return False
        # check if table CSS exist
        exist = kpim.check_table(table_name)
        if len(exist) == 0:
            return False
        return True
    except:
        print('Error during the db check')
        exit(1)   

def listCategories():
    """ List all categories and subcategories """
    try:
        row = kpim.execquery(listing_query)
        for c in row:
            if not c[1]:
                print(Fore.CYAN + '[{}]'.format(c[0]))
            else:
                print(Fore.CYAN + '[{}:{}]'.format(*c))
    except:
        print("Error during the categories' listing")
        exit(1)       

def searchnotes(content, category, subcategory):
    """
    searchnotes
    if content only => search on cmd and description
    if category only => search on category
    if subcategory only => search on subcategory
    if content and (category or subcategory) => search on cmd and description and use category and/or subcategory as filter
    """
    try:
        query=""
        
        # forge query
        if content and not category and not subcategory:
            # only content
            query=search_content.format(search=content)
        elif content and category and not subcategory:
            # content and category filter
            query=search_content_categ.format(search=content,categ=category)
        elif content and category and subcategory:
            # content and category and subcategory filter
            query=search_content_categ_subcateg.format(search=content, categ=category, subcateg=subcategory) 
        elif not content and category and not subcategory:
            # only category
            query=search_categ.format(categ=category)
        elif not content and category and subcategory:
            # category and subcategory
            query=search_categ_subcateg.format(categ=category, subcateg=subcategory)
        elif not content and not category and subcategory:
            # only subcategory
            query=search_subcateg.format(subcateg=subcategory)
        elif content and not category and subcategory:
            # subcategory and content
            query=search_content_subcateg.format(search=content, subcateg=subcategory)

        row = kpim.execquery(query)
        for res_search in row:
            # CSS (id, categ, subcateg, cmd, description, creationdt)
            # category and subcategory
            if not res_search[2]:
                printcateg = Fore.CYAN + '[{}] '.format(res_search[1])
            else:
                printcateg = Fore.CYAN + '[{}:{}] '.format(res_search[1],res_search[2])
            # desc
            if res_search[4]:
                printdesc = Fore.RESET + Style.DIM + '{} '.format(res_search[4]) + Fore.RED +Style.BRIGHT + '=> '
            else:
                printdesc = ''
            # cmd
            if res_search[3]:
                printcmd = Style.RESET_ALL + '{}'.format(res_search[3])
            else:
                printcmd = ''
            print(printcateg + printdesc + printcmd)
    except:
        print("Error during the cheatsheet search")
        exit(1)    

def addNewCSS(note):
    """
    Add new Css
    id and time are set automatically
    no check for duplicate!
    """
    # CSS (id, categ, subcateg, cmd, description, creationdt)
    categ=note[0]
    subcateg=note[1]
    desc=note[2]
    cmd=note[3]
    desc = desc.replace('[comma]',',')
    cmd = cmd.replace('[comma]',',')
    # confirm entry
    print('Confirm this insertion')
    # category and subcategory
    if not subcateg:
        printcateg = Fore.CYAN + '[{}] '.format(categ)
    else:
        printcateg = Fore.CYAN + '[{}:{}] '.format(categ,subcateg)
    # desc
    if desc:    
        printdesc = Fore.RESET + Style.DIM + '{} '.format(desc) + Fore.RED +Style.BRIGHT + '=> '
    else:
        printdesc = ''
    # cmd
    if cmd:
        printcmd = Style.RESET_ALL + '{}'.format(cmd)
    else:
        printcmd = ''    
    print(printcateg + printdesc + printcmd)
    error = True
    update = False
    while error:
        try:
            confirm = input('Y/N ? ')
            if confirm == 'Y':
                update = True
                error = False
            elif confirm == 'N':
                error = False
            else:
                print('Use Y or N')
        except:
            print('Use Y or N')
    
    if update:
        try:
            if categ == '':
                categ=None
            if subcateg == '':
                subcateg=None
            if cmd == '':
                cmd=None
            if desc == '':
                desc=None
            if not kpim.execdml(insert_css.format(categ=categ,subcateg=subcateg,cmd=cmd,description=desc,creationdt=kpim.current_time())):
                print('Error during insertion')
                exit(1)
            print('CheatSheet inserted')
        except:
            print('Error during the insertion')
            exit(1)  

def delCSS(note):
    """
    Delete CSS
    id and time are not necessary, 
      but beware identical content without its information should be delete in the same time
    no check if note exist or not
    """
    # CSS (id, categ, subcateg, cmd, description, creationdt)
    categ=note[0]
    subcateg=note[1]
    desc=(note[2]).replace('[comma]',',')
    cmd=(note[3]).replace('[comma]',',')

    # confirm entry
    print('Confirm this deletion')
    # category and subcategory
    if not subcateg:
        printcateg = Fore.CYAN + '[{}] '.format(categ)
    else:
        printcateg = Fore.CYAN + '[{}:{}] '.format(categ,subcateg)
    # desc
    if desc:
        printdesc = Fore.RESET + Style.DIM + '{} '.format(desc) + Fore.RED +Style.BRIGHT + '=> '
    else:
        printdesc = ''
    # cmd
    if cmd:
        printcmd = Style.RESET_ALL + '{}'.format(cmd)
    else:
        printcmd = ''    
    print(printcateg + printdesc + printcmd)
    error = True
    delete = False
    while error:
        try:
            confirm = input('Y/N ? ')
            if confirm == 'Y':
                delete = True
                error = False
            elif confirm == 'N':
                error = False
            else:
                print('Use Y or N')
        except:
            print('Use Y or N')
    
    if delete:
        try:
            query='DELETE FROM CSS WHERE '
            if categ == '':
                query = query + 'categ is NULL '
            else:
                query = query + "categ='" + categ + "' "
            if subcateg == '':
                query = query + 'and subcateg is NULL '
            else:
                query = query + "and subcateg='" + subcateg + "' "
            if cmd == '':
                query = query + 'and cmd is NULL '
            else:
                query = query + "and cmd='" + cmd + "' "
            if desc == '':
                query = query + 'and description is NULL '
            else:
                query = query + "and description='" + desc + "'"
            if not kpim.execdml(query):
                print('Error during deletion')
                exit(1)
            print('Cheatsheet deleted')
        except:
            print('Error during the insertion')
            exit(1)  
   
    
if __name__ == '__main__':
    create_db, listCateg, searchcontent, filtercategory, filtersubcategory, addrow, delrow = check_args() 

    # create_db if flag on
    if create_db:
        create_base(table_version)
        print('DB created')
    else:
        # check if db exist
        if not(isfile(kpim.DBNAME)):
            print("Database don't exist. Run this program with -i flag.")
            exit(1)
        if not check_base(table_version):
            print('Problem with db - check version')
            exit(1)

    # list all categories
    if listCateg:
        listCategories()
    
    if searchcontent or filtercategory or filtersubcategory:
        searchnotes(searchcontent, filtercategory, filtersubcategory)
    
    if addrow:
        addNewCSS(addrow)
        
    if delrow:
        delCSS(delrow)

