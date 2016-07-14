#!/usr/bin/env python
#encoding: utf8
#
# author: goodbest <lovegoodbest@gmail.com>
# github: github.com/goodbest


import requests
import json
import os
import sys
from datetime import datetime
import dateutil.parser
from dateutil import tz
from PIL import Image
from StringIO import StringIO
from requests_toolbelt import SSLAdapter
import ssl


def is_ok(myjson):
    try:
      json_object = json.loads(myjson)
    except ValueError, e:
      return False

    if 'Ok' in json_object:
        if json_object['Ok']:
            return True
        else:
            print json_object['Msg']
            return False
    else:
        return True


def req_get(url, param = '', type = 'json', token = True):
    if token:
        if param:
            param.update({'token': leanote_token})
        else:
            param={'token': leanote_token}

    s = requests.Session()
    if leanote_host.startswith('https'):
        s.mount('https://', SSLAdapter(ssl.PROTOCOL_TLSv1))
    r = s.get(leanote_host + '/api/' + url, params = param)
    if r.status_code == requests.codes.ok:
        if type=='json':
            if is_ok(r.text):
                rj = json.loads(r.text)
                # if 'Msg' in rj:
                #     rj=rj['Msg']
                return rj
            else:
                print '[Err] requests to url %s fail' %(r.url)
                return None
        elif type=='image':
            i = Image.open(StringIO(r.content))
            return i

    else:
        print '[Err] connect to url %s fail, error code %d ' %(r.url, r.status_cde)
        return None


def req_post(url, param = '', type = 'json', token = True):
    if token:
        if param:
            param.update({'token': leanote_token})
        else:
            param={'token': leanote_token}

    s = requests.Session()
    if leanote_host.startswith('https'):
        s.mount('https://', SSLAdapter(ssl.PROTOCOL_TLSv1))
    r = s.post(leanote_host + '/api/' + url, data = param)
    if r.status_code == requests.codes.ok:
        if type=='json':
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
def getNotebooks(includeTrash = False):
    r = req_get('notebook/getNotebooks')
    if r:
        if includeTrash:
            return {notebook['NotebookId'] : notebook for notebook in r}
        else:
            return {notebook['NotebookId'] : notebook for notebook in r if not notebook['IsDeleted']}
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


def getImage(fileId):
    param = {
        'fileId': fileId,
    }
    return req_get('file/getImage', param, type = 'image')


def addNotebook(title='Import', parentId='', seq=-1):
    param = {
        'title': title,
        'parentNotebookId': parentId,
        'seq' : seq
    }
    return req_post('notebook/addNotebook', param)


def addNote(NotebookId, Title, Content, Tags=[], IsMarkdown = True, Abstract= '', Files=[]):
    param = {
        'NotebookId': NotebookId,
        'Title': Title,
        'Content': Content,
        'Tags[]': Tags,
        'IsMarkdown': IsMarkdown,
        'Abstract': Abstract,
        #'Files' : seq
    }
    return req_post('note/addNote', param)


def readFromFile(filename):
    import yaml
    with open (filename) as file:
        file_meta = ''
        file_content = ''
        meta_flag=False
        for line in file:
            #print line
            if meta_flag:
                file_content += line
            else:
                if line.find('---')>-1:
                    meta_flag = True
                else:
                    file_meta += line
                    #print meta

        if not meta_flag:
            file_content = file_meta
            file_meta = ''
        if meta_flag:
            meta = yaml.load(file_meta)
        else:
            meta = {}
        return file_content, meta


def saveToFile(notes, noteBooks, path = '.'):
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
        try:
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
            if note['Files']:
                if len(note['Files']) > 0:
                    for attach in note['Files']:
                        if not attach['IsAttach']:
                            i = getImage(attach['FileId'])
                            print 'saving its image: %s.%s' %(attach['FileId'], i.format)
                            i.save(attach['FileId'] + '.' + i.format)

        except:
            print "error: ", filename


def LeanoteExportToMD(path = '.'):
    print 'Reading your notebooks...'
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
    saveToFile(notes, noteBooks, path = path)
    logout()
    print 'all done, bye~'


def LeanoteImportFromMD(path = '.'):
    filelist = os.listdir(path)
    filelist = [file for file in filelist if file.find('.md')>-1 or file.find('.txt')>-1]

    importedNotebookTitleMapID = {}
    ret = addNotebook(title='imported_note', parentId='', seq=-1)
    if ret:
        print 'imporing into a new notebook: %s' %ret['Title']
        importedNotebookTitleMapID['import'] = ret['NotebookId']

    for filename in filelist:
        content, meta = readFromFile(path + '/' + filename)

        parentTitle='import'
        currentTitle=''
        if not meta.get('categories'):
            categories=['import']
        else:
            categories= meta.get('categories')
        for cat in categories:
            currentTitle=cat
            if currentTitle in importedNotebookTitleMapID.keys():
                parentTitle=currentTitle
            else:
                ret = addNotebook(title = currentTitle, parentId = importedNotebookTitleMapID[parentTitle])
                importedNotebookTitleMapID[currentTitle] = ret['NotebookId']
                parentTitle=currentTitle

        if not meta.get('title'):
            meta['title'] = filename.replace('.md','').replace('.txt','')
        importedNote = addNote(NotebookId=importedNotebookTitleMapID[currentTitle], Title=meta.get('title'), Content=content, Tags=meta.get('tags', []), Abstract='')
        if importedNote:
            print 'imported %s' %filename
    logout()
    print 'all done, bye~'


if __name__ == '__main__':
    choice = raw_input("Enter your choice: (import or export) ")

    leanote_host = raw_input("Enter your host: (default is http://leanote.com) ")
    if not leanote_host:
        leanote_host = 'https://leanote.com' #使用http://leanote.com会报503错误
    leanote_email = raw_input('Enter your email: ')
    leanote_password = raw_input('Enter your password: ')
    path = raw_input("Enter your save path: (default is current dir) ")
    if not path:
        path = '.'

    # leanote_host='http://leanote.com'
    # leanote_email='admin@leanote.com'
    # leanote_password='abc123'
    # path = '.'

    print 'Connecting to %s' %leanote_host
    leanote_token = login(leanote_email, leanote_password)
    local_zone=tz.tzlocal()

    if choice == 'import':
        LeanoteImportFromMD(path)
        exit()

    elif choice == 'export':
        LeanoteExportToMD(path)
        exit()

    else:
        print 'command format: \npython Leanote4MD.py import\npython Leanote4MD.py export'









