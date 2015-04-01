#!/usr/bin/env python
#encoding: utf8
# 
# author: goodbest <lovegoodbest@gmail.com>
# github: github.com/goodbest


import requests
import json
from datetime import datetime
import dateutil.parser
from dateutil import tz

# leanote_host='http://leanote.com'
# leanote_email=''
# leanote_password=''


def is_ok(myjson):
    try:
      json_object = json.loads(myjson)
    except ValueError, e:
      return False
    
    if 'Ok' in json_object:
        if json_object['Ok']:
            return True
        else:
            return False
    else:
        return True


def req_get(url, param = '', token = True):
    if token:
        if param:
            param.update({'token': leanote_token})
        else:
            param={'token': leanote_token}
            
    r = requests.get(leanote_host + '/api/' + url, params = param)
    if r.status_code == requests.codes.ok:
        if is_ok(r.text):
            rj = json.loads(r.text)
            # if 'Msg' in rj:
            #     rj=rj['Msg']
            return rj
        else:
            print '[Err] requests to url %s fail' %(r.url)
            return None
    else:
        print '[Err] connect to url %s fail, error code %d ' %(r.url, r.status_cde)
        return None


#ret leanote_token
def login(email, pwd):
    param = {
        'email': email,
        'pwd':   pwd,
    }
    r = req_get('auth/login', param, token=False)
    if r:
        print 'Login success! Welcome %s (%s)' %(r['Username'], r['Email'])
        return r['Token']
    else:
        print 'Login fail! Start again.'
        exit()


def logout():
    return req_get('auth/logout')


#ret dict(notebookId: type.Notebook}
def getNotebooks():
    r = req_get('notebook/getNotebooks')
    if r:
        return {notebook['NotebookId'] : notebook for notebook in r}
    else:
        return none


#ret [type.Note], which contains noteId, and note meta data
def getNotesMeta(notebookId):
    param = {
        'notebookId': notebookId,
    }
    return req_get('note/getNotes', param)


#ret type.NoteContent
def getNoteDetail(noteId):
    param = {
        'noteId': noteId,
    }
    return req_get('note/getNoteAndContent', param)


def saveToFile(notes, path = '.'):
    unique_noteTitle = set()
    for note in notes:    
        if note['Title'] == '':
            filename = note['NoteId']
        else:
            filename = note['Title']
        
        if filename in unique_noteTitle:
            filename='%s_%s' %(filename, note['NoteId'])
        else:
            unique_noteTitle.add(filename)

        if note['IsMarkdown']:
            filename += '.md'
        else:
            filename += '.txt'
        with open(path + '/' + filename, 'w') as file:
            print 'write file: %s' %filename
            file.write('title: %s\n' %note['Title'].encode('utf-8'))
        
            date = dateutil.parser.parse(note['CreatedTime'])
            file.write('date: %s\n' %datetime.strftime(date.astimezone(local_zone), '%Y/%m/%d %H:%M:%S'))
        
            date = dateutil.parser.parse(note['UpdatedTime'])
            file.write('updated: %s\n' %datetime.strftime(date.astimezone(local_zone), '%Y/%m/%d %H:%M:%S'))
        
            if note['Tags']:
                if len(note['Tags']) == 1:
                    if note['Tags'][0]:
                        file.write('tags:\n')
                        for tag in note['Tags']:
                            file.write('- %s\n' %tag.encode('utf-8'))
        
            category = []
            current_notebook = note['NotebookId']
            category.append(noteBooks[current_notebook]['Title'])
            while noteBooks[current_notebook]['ParentNotebookId'] != '':
                category.append(noteBooks[noteBooks[current_notebook]['ParentNotebookId']]['Title'])
                current_notebook = noteBooks[current_notebook]['ParentNotebookId']
            file.write('categories:\n')
            category.reverse()
            for cat in category:
                file.write('- %s\n' %cat.encode('utf-8'))            
        
            file.write('---\n')
            file.write('%s' %note['Content'].encode('utf-8'))
    
        file.close()


if __name__ == '__main__':
    local_zone=tz.tzlocal()

    leanote_host = raw_input("Enter your host: (default is http://leanote.com) ")
    if not leanote_host:
        leanote_host='http://leanote.com'
    leanote_email = raw_input('Enter your email: ')
    leanote_password = raw_input('Enter your password: ')
    
    print 'Connecting to %s' %leanote_host    
    leanote_token = login(leanote_email, leanote_password)    

    print 'Reading your noteboos...'
    noteBooks = getNotebooks()
    
    #get not deleted notes list
    notes=[]
    for notebook in noteBooks.values():
        if not notebook['IsDeleted']:
            notesMeta = getNotesMeta(notebook['NotebookId'])
            for noteMeta in notesMeta:
                    if not noteMeta['IsTrash']:
                        note = getNoteDetail(noteMeta['NoteId'])
                        notes.append(note)
    print 'found %d notes' %len(notes)
    
    #write file
    saveToFile(notes, path = '.')
    
    logout()
    print 'all done, bye~'
