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

# contact
table_name='CONTACTS'
table_version="0.1"
table_creation="CREATE TABLE CONTACTS (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                category TEXT,  \
                firstname TEXT, \
                lastname TEXT, \
                emails TEXT, \
                address TEXT, \
                comment TEXT, \
                creationdt DATE)"
arg_desc='Kpim-contacts \
        \nCreated by Kalyparker \
        \nTool for keep contacts in cmdline'
listing_query="select distinct category, firstname, lastname from CONTACTS order by 3,2"
listing_category="select distinct category from CONTACTS order by 1"
insert_contact="INSERT INTO CONTACTS (category,firstname,lastname,emails,address,comment,creationdt) VALUES ('{categ}','{firstname}','{lastname}','{emails}','{address}','{comment}','{creationdt}')"


def check_args():
    """
    Check args
    -v: check version
    -h: help
    -i: Initialisation
    -l: list contacts
    -lc: list category
    -s: search contact (all column)
    -c: filter on category
    -f: filter on firstname
    -n: filter on lastname
    -add: add new contact 
    -del: delete a precise note
    """
    create_db = False
    listContact = False
    listCategory = False
    searchcontact = ''
    filtercategory = ''
    filterfirstname = ''
    filterlastname = ''
    addrow = ''
    delrow=''

    parser = argparse.ArgumentParser(description=arg_desc,formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v','--version',action='version',version=basename(argv[0]) + ' version: ' + __version__)
    parser.add_argument('-i', '--init', help="Initialisation - create table", action="store_true")
    parser.add_argument('-l', '--listcontact', help="List All contacts by name", action="store_true")
    parser.add_argument('-lc', '--listcategory', help="List All the category", action="store_true")
    parser.add_argument('-s', '--search', help="Search all column")   
    parser.add_argument('-c', '--category', help="Filter on category")
    parser.add_argument('-f', '--firstname',help="Filter on firstname")
    parser.add_argument('-n','--lastname', help="Filter on Lastname")
    parser.add_argument('-add', help="add contact. Syntax: kpim-contacts.py -add 'categ,firstname,lastname,emails,address,comment'")
    parser.add_argument('-del', '--delete',help="del row. Syntax: kpim-contacts.py -del 'categ,firstname,lastname,emails,address,comment'")
    args = parser.parse_args()

    if len(argv)==1:
        parser.print_help()
        exit(1)

    # Init - creation of DB
    if args.init:
        if isfile(kpim.DBNAME):
            # file exist
            # test if table CONTACTS exist
            try:
                ver = kpim.check_version(table_name)
                # if ver is empty, CONTACTS is not register in VERSION table
                if len(ver) == 0:
                    exist = kpim.check_table(table_name)
                    # if exist is empty, table CONTACTS does not exist
                    if len(exist) == 0:
                        create_db = True
            except:
                print('Database',kpim.DBNAME,'already exists')
                exit(1)
        else:
            create_db = True 

    # list all contacts
    if args.listcontact:
        listContact = True

    # list category
    if args.listcategory:
        listCategory = True

    # search content
    if args.search:
        searchcontact = args.search
        
    # filter on category
    if args.category:
        filtercategory=args.category
    
    # filter on firstname
    if args.firstname:
        filterfirstname = args.firstname

    # filter on lastname
    if args.lastname:
        filterlastname = args.lastname

    # add contact 
    if args.add:
        addrow = (args.add).split(',')

    # del contact 
    if args.delete:
        delrow = (args.delete).split(',')
        
    return create_db, listContact, listCategory, searchcontact, filtercategory, filterfirstname, filterlastname, addrow, delrow

def create_base(version):
    """
    Database Creation
    VERSION if not exist (script in kpim)
    CONTACTS (id, category, firstname,lastname, emails, address, comment, creationdt)
    """
    try:
        # test if VERSION exist
        exist = kpim.check_table('VERSION')
        if len(exist) == 0:
            # VERSION does not exist - create table
            if not (kpim.create_version()):
                print('Error in creation of version table')
                exit(1)
        # insert version of CONTACTS 
        if not (kpim.add_version(table_version, table_name)):
            print('Error in insertion of version table')
            exit(1)
        
        # Create table CONTACTS
        if not (kpim.execdml(table_creation)):
            print('Error in creation of CONTACTS table')
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
        # if ver is empty, CONTACTS is not register in VERSION table
        if (len(ver) == 0) or (ver[0][0] != table_version):
            return False
        # check if table CONTACTS exist
        exist = kpim.check_table(table_name)
        if len(exist) == 0:
            return False
        return True
    except:
        print('Error during the db check')
        exit(1)   


def listAllContacts():
    """ List all contacts """
    try:
        row = kpim.execquery(listing_query)
        for c in row:
            if not c[0]:
                print(Fore.CYAN + '{} {}'.format(c[1],c[2]))
            else:
                print(Fore.CYAN + '{} {} ({})'.format(c[1],c[2],c[0]))
    except:
        print("Error during the contact listing")
        exit(1)       

def listCategories():
    """ List All Categories """
    try:
        row = kpim.execquery(listing_category)
        for c in row:
            print(Fore.CYAN + '{}'.format(c[0]))
    except:
        print("Error during the category listing")
        exit(1)


def searchcontacts(contact, category, firstname, name):
    """
    searchcontacts
    if contact => search on all columns
    if category only => search on category
    if firstname only => search on firstname
    if lastname only => search on lastname
    if contact and/or category and/or firstname and/or lastname => search on all columns and use category and/or firstname and/or lastname as filter
    """
    try:
        search={'category','firstname','lastname','emails','address','comment'}

        query="select * from ("
        # Forge query
        if contact and not category and not firstname and not name:
            # only contact
            first=True
            for i in search:
                if not first:
                    query=query+' union '
                else:
                   first=False
                query=query+"select * from CONTACTS where " + i + " like '%{searchcontent}%'"
            query=query + ') order by firstname, lastname, category'
            query=query.format(searchcontent=contact)
        elif not contact and category and not firstname and not name:
            # only category
            query="select * from CONTACTS where category like '%{categ}%'"
            query=query + ' order by firstname, lastname, category'
            query=query.format(categ=category)
        elif not contact and not category and firstname and not name:
            # only firstname
            query="select * from CONTACTS where firstname like '%{firstname}%'"
            query=query + ' order by firstname, lastname, category'
            query=query.format(firstname=firstname)
        elif not contact and not category and not firstname and name:
            # only name
            query="select * from CONTACTS where lastname like '%{name}%'"
            query=query + ' order by firstname, lastname, category'
            query=query.format(name=name)
        elif contact and category and not firstname and not name:
            # contact and category
            first=True
            for i in search:
                if not first:
                    query=query+' union '
                else:
                   first=False
                query=query+"select * from CONTACTS where " + i + " like '%{searchcontent}%'"
                query=query + " and category like '%{categ}%'"
            query=query + ') order by firstname, lastname, category'
            query=query.format(searchcontent=contact,categ=category)
        elif contact and not category and firstname and not name:
            # contact and firstname
            first=True
            for i in search:
                if not first:
                    query=query+' union '
                else:
                   first=False
                query=query+"select * from CONTACTS where " + i + " like '%{searchcontent}%'"
                query=query + " and firstname like '%{firstname}%'"
            query=query + ') order by firstname, lastname, category'
            query=query.format(searchcontent=contact,firstname=firstname)
        elif contact and not category and not firstname and name:
            # contact and name
            first=True
            for i in search:
                if not first:
                    query=query+' union '
                else:
                   first=False
                query=query+"select * from CONTACTS where " + i + " like '%{searchcontent}%'"
                query=query + " and lastname like '%{name}%'"
            query=query + ') order by firstname, lastname, category'
            query=query.format(searchcontent=contact,name=name)
        elif contact and category and firstname and not name:
            # contact and category and firstname
            first=True
            for i in search:
                if not first:
                    query=query+' union '
                else:
                   first=False
                query=query+"select * from CONTACTS where " + i + " like '%{searchcontent}%'"
                query=query + " and category like '%{categ}%'"
                query=query + " and firstname like '%{firstname}%'"
            query=query + ') order by firstname, lastname, category'
            query=query.format(searchcontent=contact,categ=category,firstname=firstname)
        elif contact and category and not firstname and name:
            # contact and category and name
            first=True
            for i in search:
                if not first:
                    query=query+' union '
                else:
                   first=False
                query=query+"select * from CONTACTS where " + i + " like '%{searchcontent}%'"
                query=query + " and category like '%{categ}%'"
                query=query + " and lastname like '%{name}%'"
            query=query + ') order by firstname, lastname, category'
            query=query.format(searchcontent=contact,categ=category,name=name)
        elif contact and category and firstname and name:
            # contact and category and firstname and name
            first=True
            for i in search:
                if not first:
                    query=query+' union '
                else:
                   first=False
                query=query+"select * from CONTACTS where " + i + " like '%{searchcontent}%'"
                query=query + " and category like '%{categ}%'"
                query=query + " and firstname like '%{firstname}%'"
                query=query + " and lastname like '%{name}%'"
            query=query + ') order by firstname, lastname, category'
            query=query.format(searchcontent=contact,categ=category,firstname=firstname,name=name)
        elif contact and not category and firstname and name:
            # contact and firstname and name
            first=True
            for i in search:
                if not first:
                    query=query+' union '
                else:
                   first=False
                query=query+"select * from CONTACTS where " + i + " like '%{searchcontent}%'"
                query=query + " and firstname like '%{firstname}%'"
                query=query + " and lastname like '%{name}%'"
            query=query + ') order by firstname, lastname, category'
            query=query.format(searchcontent=contact,firstname=firstname,name=name)
        elif not contact and category and firstname and not name:
            # category and firstname
            query="select * from CONTACTS where category like '%{categ}%'"
            query=query + " and firstname like '%{firstname}%'"
            query=query + ' order by firstname, lastname, category'
            query=query.format(categ=category,firstname=firstname)
        elif not contact and category and not firstname and name:
            # category and name
            query="select * from CONTACTS where category like '%{categ}%'"
            query=query + " and lastname like '%{name}%'"
            query=query + ' order by firstname, lastname, category'
            query=query.format(categ=category,name=name)
        elif not contact and category and firstname and name:
            # category and firstname and name
            query="select * from CONTACTS where category like '%{categ}%'"
            query=query + " and firstname like '%{firstname}%'"
            query=query + " and lastname like '%{name}%'"
            query=query + ' order by firstname, lastname, category'
            query=query.format(categ=category,firstname=firstname,name=name)
        elif not contact and not category and firstname and name:
            # firstname and name
            query="select * from CONTACTS where firstname like '%{firstname}%'"
            query=query + " and lastname like '%{name}%'"
            query=query + ' order by firstname, lastname, category'
            query=query.format(firstname=firstname,name=name)

        row = kpim.execquery(query)
        for res_search in row:      
            # CONTACTS (id, category, firstname,lastname, emails, address, comment, creationdt)
            #print(res_search)
            if not res_search[1]:
                rescateg=''
            else:
                rescateg=res_search[1]
            if not res_search[2]:
                resfirstname=''
            else:
                resfirstname=res_search[2]
            if not res_search[3]:
                reslastname=''
            else:
                reslastname=res_search[3]
                # firstname, lastname and category 
            if rescateg=='':
                printname = Fore.CYAN + '{} {}'.format(resfirstname,reslastname)
            else:
                 printname = Fore.CYAN + '{} {} ({})'.format(resfirstname,reslastname,rescateg)
            print(printname)
            # emails
            if res_search[4]:
                print(Fore.RED   + "   + email(s): " + Fore.RESET + Style.DIM + '{} '.format(res_search[4]))
            # address 
            if res_search[5]:
                print(Fore.RED + "   + address: " + Fore.RESET + Style.DIM + '{}'.format(res_search[5])) 
            # comment
            if res_search[6]:
                print(Fore.RED + "   + comment: " + Fore.RESET + Style.DIM + '{}'.format(res_search[6]))
    except:
        print("Error during the contact search")
        exit(1)    

def addNewContact(contact):
    """
    Add new contact 
    id and time are set automatically
    no check for duplicate!
    """
    # CONTACTS (id, category, firstname, lastname, emails, address, comment, creationdt)
    categ=contact[0]
    firstname=contact[1]
    name=contact[2]
    emails=(contact[3]).replace('[comma]',',')
    address=(contact[4]).replace('[comma]',',')
    comment=(contact[5]).replace('[comma]',',')
    # confirm entry
    print('Confirm this insertion')
    if not categ:
        categ=''
    if not firstname:
        firstname=''
    if not name:
        name=''
    # firstname, lastname and category 
    if categ=='':
        printname = Fore.CYAN + '{} {}'.format(firstname,name)
    else:
        printname = Fore.CYAN + '{} {} ({})'.format(firstname,name,categ)
    print(printname)
    # emails
    if emails:
        print(Fore.RED   + "   + email(s): " + Fore.RESET + Style.DIM + '{} '.format(emails))
    # address 
    if address:
        print(Fore.RED + "   + address: " + Fore.RESET + Style.DIM + '{}'.format(address)) 
    # comment
    if comment:
        print(Fore.RED + "   + comment: " + Fore.RESET + Style.DIM + '{}'.format(comment))
    
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
            if firstname == '':
                firstname=None
            if name == '':
                name=None
            if emails == '':
                emails = None
            if address == '':
                address = None
            if comment == '':
                comment = None
            if not kpim.execdml(insert_contact.format(categ=categ,firstname=firstname,lastname=name,emails=emails,address=address,comment=comment,creationdt=kpim.current_time())):
                print('Error during insertion')
                exit(1)
            print('Contact inserted')
        except:
            print('Error during the insertion')
            exit(1)  

def delContact(contact):
    """
    Delete Contact 
    id and time are not necessary, 
      but beware identical content without its information should be delete in the same time
    no check if note exist or not
    """
    categ=contact[0]
    firstname=contact[1]
    name=contact[2]
    emails=(contact[3]).replace('[comma]',',')
    address=(contact[4]).replace('[comma]',',')
    comment=(contact[5]).replace('[comma]',',')
    # CONTACTS (id, category, firstname, lastname, emails, address, comment, creationdt)
    
    # confirm entry
    print('Confirm this deletion')
    if not categ:
        categ=''
    if not firstname:
        firstname=''
    if not name:
        name=''
    # firstname, lastname and category 
    if categ=='':
        printname = Fore.CYAN + '{} {}'.format(firstname,name)
    else:
        printname = Fore.CYAN + '{} {} ({})'.format(firstname,name,categ)
    print(printname)
    # emails
    if emails:
        print(Fore.RED   + "   + email(s): " + Fore.RESET + Style.DIM + '{} '.format(emails))
    # address 
    if address:
        print(Fore.RED + "   + address: " + Fore.RESET + Style.DIM + '{}'.format(address)) 
    # comment
    if comment:
        print(Fore.RED + "   + comment: " + Fore.RESET + Style.DIM + '{}'.format(comment))
    
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
            query='DELETE FROM CONTACTS WHERE '
            if categ == '':
                query = query + 'category is NULL '
            else:
                query = query + "category='" + categ + "' "
            if firstname == '':
                query = query + 'and firstname is NULL '
            else:
                query = query + "and firstname='" + firstname + "' "
            if name == '':
                query = query + 'and lastname is NULL '
            else:
                query = query + "and lastname='" + name + "' "
            if emails == '':
                query = query + 'and emails is NULL '
            else:
                query = query + "and emails='" + emails + "' "
            if address == '':
                query = query + 'and address is NULL '
            else:
                query = query + "and address='" + address + "' "
            if comment == '':
                query = query + 'and comment is NULL '
            else:
                query = query + "and comment='" + comment + "' "

            if not kpim.execdml(query):
                print('Error during deletion')
                exit(1)
            print('Contact deleted')
        except:
            print('Error during the insertion')
            exit(1)  
   
    
if __name__ == '__main__':
    create_db, listContact, listCategory, searchcontact, filtercategory, filterfirstname, filtername, addrow, delrow = check_args()

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

    # list all contacts
    if listContact:
        listAllContacts()

    # list all categories
    if listCategory:
        listCategories()

    if searchcontact or filtercategory or filterfirstname or filtername:
        searchcontacts(searchcontact, filtercategory, filterfirstname, filtername)
    
    if addrow:
        addNewContact(addrow)
        
    if delrow:
        delContact(delrow)

