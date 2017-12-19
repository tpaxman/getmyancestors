#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   getmyancestors.py - Retrieve GEDCOM data from FamilySearch Tree
   Copyright (C) 2014-2016 Giulio Genovese (giulio.genovese@gmail.com)

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.

   Written by Giulio Genovese <giulio.genovese@gmail.com>
   and by Benoît Fontaine <benoitfontaine.ba@gmail.com>
"""

from __future__ import print_function
import sys
import argparse
import getpass
import time
import asyncio
import re
from fsearch_translation import translations

try:
    import requests
except ImportError:
    sys.stderr.write('You need to install the requests module first\n')
    sys.stderr.write('(run this in your terminal: "python3 -m pip install requests" or "python3 -m pip install --user requests")\n')
    exit(2)

FACT_TAGS = {
    'http://gedcomx.org/Birth': 'BIRT',
    'http://gedcomx.org/Christening': 'CHR',
    'http://gedcomx.org/Death': 'DEAT',
    'http://gedcomx.org/Burial': 'BURI',
    'http://gedcomx.org/PhysicalDescription': 'DSCR',
    'http://gedcomx.org/Occupation': 'OCCU',
    'http://gedcomx.org/MilitaryService': '_MILT',
    'http://gedcomx.org/Marriage': 'MARR',
    'http://gedcomx.org/Divorce': 'DIV',
    'http://gedcomx.org/Annulment': 'ANUL',
    'http://gedcomx.org/CommonLawMarriage': '_COML',
    'http://gedcomx.org/BarMitzvah': 'BARM',
    'http://gedcomx.org/BatMitzvah': 'BASM',
    'http://gedcomx.org/Naturalization': 'NATU',
    'http://gedcomx.org/Residence': 'RESI',
    'http://gedcomx.org/Religion': 'RELI',
    'http://familysearch.org/v1/TitleOfNobility': 'TITL',
    'http://gedcomx.org/Cremation': 'CREM',
    'http://gedcomx.org/Caste': 'CAST',
    'http://gedcomx.org/Nationality': 'NATI',
}

FACT_EVEN = {
    'http://gedcomx.org/Stillbirth': 'Stillborn',
    'http://familysearch.org/v1/Affiliation': 'Affiliation',
    'http://gedcomx.org/Clan': 'Clan Name',
    'http://gedcomx.org/NationalId': 'National Identification',
    'http://gedcomx.org/Ethnicity': 'Race',
    'http://familysearch.org/v1/TribeName': 'Tribe Name'
}


def cont(level, string):
    return re.sub(r'[\r\n]+', '\n' + str(level) + ' CONT ', string)


# FamilySearch session class
class Session:
    def __init__(self, username, password, verbose=False, logfile=sys.stderr, timeout=60):
        self.username = username
        self.password = password
        self.verbose = verbose
        self.logfile = logfile
        self.timeout = timeout
        self.fid = self.lang = None
        self.login()

    # retrieve FamilySearch session ID (https://familysearch.org/developers/docs/guides/oauth2)
    def login(self):
        while True:
            try:
                url = 'https://www.familysearch.org/auth/familysearch/login'
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Downloading: ' + url + '\n')
                r = requests.get(url, params={'ldsauth': False}, allow_redirects=False)
                url = r.headers['Location']
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Downloading: ' + url + '\n')
                r = requests.get(url, allow_redirects=False)
                idx = r.text.index('name="params" value="')
                span = r.text[idx + 21:].index('"')
                params = r.text[idx + 21:idx + 21 + span]

                url = 'https://ident.familysearch.org/cis-web/oauth2/v3/authorization'
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Downloading: ' + url + '\n')
                r = requests.post(url, data={'params': params, 'userName': self.username, 'password': self.password}, allow_redirects=False)

                if 'The username or password was incorrect' in r.text:
                    if self.verbose:
                        self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: The username or password was incorrect\n')
                    exit()

                if 'Invalid Oauth2 Request' in r.text:
                    if self.verbose:
                        self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Invalid Oauth2 Request\n')
                    time.sleep(self.timeout)
                    continue

                url = r.headers['Location']
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Downloading: ' + url + '\n')
                r = requests.get(url, allow_redirects=False)
                self.fssessionid = r.cookies['fssessionid']
            except requests.exceptions.ReadTimeout:
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Read timed out\n')
                continue
            except requests.exceptions.ConnectionError:
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Connection aborted\n')
                time.sleep(self.timeout)
                continue
            except requests.exceptions.HTTPError:
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: HTTPError\n')
                time.sleep(self.timeout)
                continue
            except KeyError:
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: KeyError\n')
                time.sleep(self.timeout)
                continue
            except ValueError:
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: ValueError\n')
                time.sleep(self.timeout)
                continue
            if self.verbose:
                self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: FamilySearch session id: ' + self.fssessionid + '\n')
            return

    # retrieve FamilySearch developer key (wget -O- --max-redirect 0 https://familysearch.org/auth/familysearch/login?ldsauth=false)
    def get_key(self):
        url = 'https://familysearch.org/auth/familysearch/login'
        while True:
            if self.verbose:
                self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Downloading: ' + url + '\n')
            try:
                r = requests.get(url, params={'ldsauth': False}, allow_redirects=False, timeout=self.timeout)
                location = r.headers['Location']
                idx = location.index('client_id=')
                key = location[idx + 10:idx + 49]
            except ValueError:
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: FamilySearch developer key not found\n')
                time.sleep(self.timeout)
                continue
            if self.verbose:
                self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: FamilySearch developer key: ' + key + '\n')
            return key

    # retrieve FamilySearch session ID (https://familysearch.org/developers/docs/guides/oauth1/login)
    def old_login(self, oldmethod=False):
        url = 'https://api.familysearch.org/identity/v2/login'
        data = {'key': self.key, 'username': self.username,
                'password': self.password}
        while True:
            if self.verbose:
                self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Downloading: ' + url + '\n')
            try:
                r = requests.post(url, data, timeout=self.timeout)
            except requests.exceptions.ReadTimeout:
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Read timed out\n')
                continue
            except requests.exceptions.ConnectionError:
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Connection aborted\n')
                time.sleep(self.timeout)
                continue
            if self.verbose:
                self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Status code: ' + str(r.status_code) + '\n')
            if r.status_code == 401:
                self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Login failure\n')
                raise Exception('Login failure')
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError:
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: HTTPError\n')
                time.sleep(self.timeout)
                continue
            self.fssessionid = r.cookies['fssessionid']
            if self.verbose:
                self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: FamilySearch session id: ' + self.fssessionid + '\n')
            return

    # retrieve JSON structure from FamilySearch URL
    def get_url(self, url):
        while True:
            try:
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Downloading: ' + url + '\n')
                # r = requests.get(url, cookies = { 's_vi': self.s_vi, 'fssessionid' : self.fssessionid }, timeout = self.timeout)
                r = requests.get(url, cookies={'fssessionid': self.fssessionid}, timeout=self.timeout)
            except requests.exceptions.ReadTimeout:
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Read timed out\n')
                continue
            except requests.exceptions.ConnectionError:
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Connection aborted\n')
                time.sleep(self.timeout)
                continue
            if self.verbose:
                self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: Status code: ' + str(r.status_code) + '\n')
            if r.status_code == 204 or r.status_code == 410:
                return None
            if r.status_code == 401:
                self.login()
                continue
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError:
                if self.verbose:
                    self.logfile.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + ']: HTTPError\n')
                if r.status_code == 403:
                    if 'message' in r.json()['errors'][0] and r.json()['errors'][0]['message'] == u'Unable to get ordinances.':
                        self.logfile.write('Unable to get ordinances. Try with an LDS account or without option -c.\n')
                        exit()
                    else:
                        self.logfile.write('Warning code 403 link: ' + url + ' ' + r.json()['errors'][0]['message'] or '')
                        return None
                time.sleep(self.timeout)
                continue
            return r.json()

    # retrieve FamilySearch current user ID
    def set_current(self):
        url = 'https://familysearch.org/platform/users/current.json'
        data = self.get_url(url)
        if data:
            self.fid = data['users'][0]['personId']
            self.lang = data['users'][0]['preferredLanguage']

    def get_userid(self):
        if not self.fid:
            self.set_current()
        return self.fid

    def _(self, string):
        if not self.lang:
            self.set_current()
        if string in translations and self.lang in translations[string]:
            return translations[string][self.lang]
        return string


# some GEDCOM objects
class Note:

    counter = 0

    def __init__(self, text='', tree=None, num=None):
        if num:
            self.num = num
        else:
            Note.counter += 1
            self.num = Note.counter
        if tree:
            tree.notes.append(self)

        self.text = text.strip()

    def print(self, file=sys.stdout):
        file.write('0 @N' + str(self.num) + '@ NOTE ' + cont(1, self.text) + '\n')

    def link(self, file=sys.stdout, level=1):
        file.write(str(level) + ' NOTE @N' + str(self.num) + '@\n')


class Source:

    counter = 0

    def __init__(self, data=None, tree=None, num=None):
        if num:
            self.num = num
        else:
            Source.counter += 1
            self.num = Source.counter
        if tree and data:
            tree.sources[data['id']] = self

        self.url = self.citation = self.title = self.fid = None
        self.notes = set()

        if data:
            self.fid = data['id']
            if 'about' in data:
                self.url = data['about'].replace('familysearch.org/platform/memories/memories', 'www.familysearch.org/photos/artifacts')
            if 'citations' in data:
                self.citation = data['citations'][0]['value']
            if data['titles']:
                self.title = data['titles'][0]['value']
            if 'notes' in data:
                for n in data['notes']:
                    if n['text']:
                        self.notes.add(Note(n['text'], tree))

    def print(self, file=sys.stdout):
        file.write('0 @S' + str(self.num) + '@ SOUR \n')
        if self.title:
            file.write('1 TITL ' + cont(2, self.title) + '\n')
        if self.citation:
            file.write('1 AUTH ' + cont(2, self.citation) + '\n')
        if self.url:
            file.write('1 PUBL ' + cont(2, self.url) + '\n')
        for n in self.notes:
            n.link(file, 1)
        file.write('1 REFN ' + self.fid + '\n')

    def link(self, file=sys.stdout, level=1):
        file.write(str(level) + ' SOUR @S' + str(self.num) + '@\n')


class Fact:

    def __init__(self, data=None, tree=None):
        self.value = self.type = self.date = self.place = self.note = None
        if data:
            if 'value' in data:
                self.value = data['value']
            if 'type' in data:
                self.type = data['type']
                if self.type in FACT_EVEN:
                    self.type = tree.fs._(FACT_EVEN[self.type])
                elif self.type[:6] == u'data:,':
                    self.type = self.type[6:]
                elif self.type not in FACT_TAGS:
                    self.type = None
            if 'date' in data:
                self.date = data['date']['original']
            if 'place' in data:
                self.place = data['place']['original']
            if 'changeMessage' in data['attribution']:
                self.note = Note(data['attribution']['changeMessage'], tree)
            if self.type == 'http://gedcomx.org/Death' and not (self.date or self.place):
                self.value = 'Y'

    def print(self, file=sys.stdout, key=None):
        if self.type in FACT_TAGS:
            file.write('1 ' + FACT_TAGS[self.type])
            if self.value:
                file.write(' ' + self.value)
        elif self.type:
            file.write('1 EVEN\n2 TYPE ' + self.type)
            if self.value:
                file.write('\n2 NOTE Description: ' + cont(3, self.value))
        else:
            return
        file.write('\n')
        if self.date:
            file.write('2 DATE ' + self.date + '\n')
        if self.place:
            file.write('2 PLAC ' + self.place + '\n')
        if self.note:
            self.note.link(file, 2)


class Memorie:

    def __init__(self, data=None):
        self.description = self.url = None
        if data and 'links' in data:
            self.url = data['links']['alternate'][0]['href']
            if 'titles' in data:
                self.description = data['titles'][0]['value']
            if 'descriptions' in data:
                self.description = ('' if not self.description else self.description + '\n') + data['descriptions'][0]['value']

    def print(self, file=sys.stdout):
        file.write('1 OBJE\n2 FORM URL\n')
        if self.description:
            file.write('2 TITL ' + cont(2, self.description) + '\n')
        if self.url:
            file.write('2 FILE ' + self.url + '\n')


class Name:

    def __init__(self, data=None, tree=None):
        self.given = ''
        self.surname = ''
        self.prefix = None
        self.suffix = None
        self.note = None
        if data:
            if 'parts' in data['nameForms'][0]:
                for z in data['nameForms'][0]['parts']:
                    if z['type'] == u'http://gedcomx.org/Given':
                        self.given = z['value']
                    if z['type'] == u'http://gedcomx.org/Surname':
                        self.surname = z['value']
                    if z['type'] == u'http://gedcomx.org/Prefix':
                        self.prefix = z['value']
                    if z['type'] == u'http://gedcomx.org/Suffix':
                        self.suffix = z['value']
            if 'changeMessage' in data['attribution']:
                self.note = Note(data['attribution']['changeMessage'], tree)

    def print(self, file=sys.stdout, typ=None):
        file.write('1 NAME ' + self.given + ' /' + self.surname + '/')
        if self.suffix:
            file.write(' ' + self.suffix)
        file.write('\n')
        if typ:
            file.write('2 TYPE ' + typ + '\n')
        if self.prefix:
            file.write('2 NPFX ' + self.prefix + '\n')
        if self.note:
            self.note.link(file, 2)


class Ordinance:

    def __init__(self, data=None):
        self.date = self.temple_code = self.status = self.famc = None
        if data:
            if 'date' in data:
                self.date = data['date']['formal']
            if 'templeCode' in data:
                self.temple_code = data['templeCode']
            if data['status'] == u'http://familysearch.org/v1/Completed':
                self.status = 'COMPLETED'
            if data['status'] == u'http://familysearch.org/v1/Cancelled':
                self.status = 'CANCELED'
            if data['status'] == u'http://familysearch.org/v1/InProgress':
                self.status = 'SUBMITTED'

    def print(self, file=sys.stdout):
        if self.date:
            file.write('2 DATE ' + self.date + '\n')
        if self.temple_code:
            file.write('2 TEMP ' + self.temple_code + '\n')
        if self.status:
            file.write('2 STAT ' + self.status + '\n')
        if self.famc:
            file.write('2 FAMC @F' + str(self.famc.num) + '@\n')


# GEDCOM individual class
class Indi:

    counter = 0

    # initialize individual
    def __init__(self, fid=None, tree=None, num=None):
        if num:
            self.num = num
        else:
            Indi.counter += 1
            self.num = Indi.counter
        self.fid = fid
        self.tree = tree
        self.famc_fid = set()
        self.fams_fid = set()
        self.famc_num = set()
        self.fams_num = set()
        self.name = None
        self.gender = None
        self.baptism = self.confirmation = self.endowment = self.sealing_child = None
        self.nicknames = set()
        self.facts = set()
        self.birthnames = set()
        self.married = set()
        self.aka = set()
        self.notes = set()
        self.sources = set()
        self.memories = set()
        if fid and tree and tree.fs:
            url = 'https://familysearch.org/platform/tree/persons/%s.json' % self.fid
            data = tree.fs.get_url(url)
            if data:
                x = data['persons'][0]
                if x['names']:
                    for y in x['names']:
                        if y['preferred']:
                            self.name = Name(y, self.tree)
                        else:
                            if y['type'] == u'http://gedcomx.org/Nickname':
                                self.nicknames.add(Name(y, self.tree))
                            if y['type'] == u'http://gedcomx.org/BirthName':
                                self.birthnames.add(Name(y, self.tree))
                            if y['type'] == u'http://gedcomx.org/AlsoKnownAs':
                                self.aka.add(Name(y, self.tree))
                            if y['type'] == u'http://gedcomx.org/MarriedName':
                                self.married.add(Name(y, self.tree))
                if 'gender' in x:
                    if x['gender']['type'] == 'http://gedcomx.org/Male':
                        self.gender = 'M'
                    elif x['gender']['type'] == 'http://gedcomx.org/Female':
                        self.gender = 'F'
                    elif x['gender']['type'] == 'http://gedcomx.org/Unknown':
                        self.gender = 'U'
                for y in x['facts']:
                    if y['type'] == u'http://familysearch.org/v1/LifeSketch':
                        self.notes.add(Note('=== ' + self.tree.fs._('Life Sketch') + ' ===\n' + y['value'], self.tree))
                    else:
                        self.facts.add(Fact(y, self.tree))
                if 'sources' in x:
                    for y in x['sources']:
                        source = self.tree.add_source(y['descriptionId'])
                        if source:
                            if 'changeMessage' in y['attribution']:
                                self.sources.add((source, y['attribution']['changeMessage']))
                            else:
                                self.sources.add((source,))
                if 'evidence' in x:
                    url = 'https://familysearch.org/platform/tree/persons/%s/memories.json' % self.fid
                    data = tree.fs.get_url(url)
                    if data and 'sourceDescriptions' in data:
                        for y in data['sourceDescriptions']:
                            self.memories.add(Memorie(y))

        self.parents = None
        self.children = None
        self.spouses = None

    # add a fams to the individual
    def add_fams(self, fams):
        if fams not in self.fams_fid:
            self.fams_fid.add(fams)

    # add a famc to the individual
    def add_famc(self, famc):
        if famc not in self.famc_fid:
            self.famc_fid.add(famc)

    # retrieve parents
    def get_parents(self):
        if not self.parents:
            url = 'https://familysearch.org/platform/tree/persons/%s/parents.json' % self.fid
            data = self.tree.fs.get_url(url)
            if data:
                x = data['childAndParentsRelationships'][0]
                self.parents = (x['father']['resourceId'] if 'father' in x else None,
                                x['mother']['resourceId'] if 'mother' in x else None)
            else:
                self.parents = (None, None)
        return self.parents

    # retrieve children relationships
    def get_children(self):
        if not self.children:
            url = 'https://familysearch.org/platform/tree/persons/%s/children.json' % self.fid
            data = self.tree.fs.get_url(url)
            if data:
                self.children = [(x['father']['resourceId'] if 'father' in x else None,
                                  x['mother']['resourceId'] if 'mother' in x else None,
                                  x['child']['resourceId']) for x in data['childAndParentsRelationships']]
        return self.children

    # retrieve spouse relationships
    def get_spouses(self):
        if not self.spouses:
            url = 'https://familysearch.org/platform/tree/persons/%s/spouses.json' % self.fid
            data = self.tree.fs.get_url(url)
            if data and 'relationships' in data:
                self.spouses = [(x['person1']['resourceId'], x['person2']
                                 ['resourceId'], x['id']) for x in data['relationships']]
        return self.spouses

    # retrieve individual notes
    def get_notes(self):
        notes = self.tree.fs.get_url('https://familysearch.org/platform/tree/persons/%s/notes.json' % self.fid)
        if notes:
            for n in notes['persons'][0]['notes']:
                text_note = '===' + n['subject'] + \
                    '===\n' if 'subject' in n else ''
                text_note += n['text'] + '\n' if 'text' in n else ''
                self.notes.add(Note(text_note, self.tree))

    # retrieve LDS ordinances
    def get_ordinances(self):
        res = []
        famc = False
        url = 'https://familysearch.org/platform/tree/persons/%s/ordinances.json' % self.fid
        data = self.tree.fs.get_url(url)['persons'][0]['ordinances']
        if data:
            for o in data:
                if o['type'] == u'http://lds.org/Baptism':
                    self.baptism = Ordinance(o)
                if o['type'] == u'http://lds.org/Confirmation':
                    self.confirmation = Ordinance(o)
                if o['type'] == u'http://lds.org/Endowment':
                    self.endowment = Ordinance(o)
                if o['type'] == u'http://lds.org/SealingChildToParents':
                    self.sealing_child = Ordinance(o)
                    if 'father' in o and 'mother' in o:
                        famc = (o['father']['resourceId'],
                                o['mother']['resourceId'])
                if o['type'] == u'http://lds.org/SealingToSpouse':
                    res.append(o)
        return res, famc

    # retrieve contributors
    def get_contributors(self):
        temp = set()
        data = self.tree.fs.get_url('https://familysearch.org/platform/tree/persons/%s/changes.json' % self.fid)
        for entries in data['entries']:
            for contributors in entries['contributors']:
                temp.add(contributors['name'])
        if temp:
            text = '=== ' + self.tree.fs._('Contributors') + ' ===\n' + '\n'.join(sorted(temp))
            for n in self.tree.notes:
                if n.text == text:
                    self.notes.add(n)
                    return
            self.notes.add(Note(text, self.tree))

    # print individual information in GEDCOM format
    def print(self, file=sys.stdout):
        file.write('0 @I' + str(self.num) + '@ INDI\n')
        if self.name:
            self.name.print(file)
        for o in self.nicknames:
            file.write('2 NICK ' + o.given + ' ' + o .surname + '\n')
        for o in self.birthnames:
            o.print(file)
        for o in self.aka:
            o.print(file, 'aka')
        for o in self.married:
            o.print(file, 'married')
        if self.gender:
            file.write('1 SEX ' + self.gender + '\n')
        for o in self.facts:
            o.print(file)
        for o in self.memories:
            o.print(file)
        if self.baptism:
            file.write('1 BAPL\n')
            self.baptism.print(file)
        if self.confirmation:
            file.write('1 CONL\n')
            self.confirmation.print(file)
        if self.endowment:
            file.write('1 ENDL\n')
            self.endowment.print(file)
        if self.sealing_child:
            file.write('1 SLGC\n')
            self.sealing_child.print(file)
        for num in self.fams_num:
            file.write('1 FAMS @F' + str(num) + '@\n')
        for num in self.famc_num:
            file.write('1 FAMC @F' + str(num) + '@\n')
        file.write('1 _FSFTID ' + self.fid + '\n')
        for o in self.notes:
            o.link(file)
        for o in self.sources:
            o[0].link(file, 1)
            if len(o) > 1:
                file.write('2 PAGE ' + cont(2, o[1]) + '\n')


# GEDCOM family class
class Fam:
    counter = 0

    # initialize family
    def __init__(self, husb=None, wife=None, tree=None, num=None):
        if num:
            self.num = num
        else:
            Fam.counter += 1
            self.num = Fam.counter
        self.husb_fid = husb if husb else None
        self.wife_fid = wife if wife else None
        self.tree = tree
        self.husb_num = self.wife_num = self.fid = None
        self.facts = set()
        self.sealing_spouse = None
        self.chil_fid = set()
        self.chil_num = set()
        self.notes = set()
        self.sources = set()

    # add a child to the family
    def add_child(self, child):
        if child not in self.chil_fid:
            self.chil_fid.add(child)

    # retrieve and add marriage information
    def add_marriage(self, fid):
        if not self.fid:
            self.fid = fid
            url = 'https://familysearch.org/platform/tree/couple-relationships/%s.json' % self.fid
            data = self.tree.fs.get_url(url)
            if data and 'facts' in data['relationships'][0]:
                for x in data['relationships'][0]['facts']:
                    self.facts.add(Fact(x, self.tree))
            if data and 'sources' in data['relationships'][0]:
                for y in data['relationships'][0]['sources']:
                    source = self.tree.add_source(y['descriptionId'])
                    if source:
                        if 'changeMessage' in y['attribution']:
                            self.sources.add((source, y['attribution']['changeMessage']))
                        else:
                            self.sources.add((source,))

    # retrieve marriage notes
    def get_notes(self):
        if self.fid:
            notes = self.tree.fs.get_url('https://familysearch.org/platform/tree/couple-relationships/%s/notes.json' % self.fid)
            if notes:
                for n in notes['relationships'][0]['notes']:
                    text_note = '===' + n['subject'] + \
                        '===\n' if 'subject' in n else ''
                    text_note += n['text'] + '\n' if 'text' in n else ''
                    self.notes.add(Note(text_note, self.tree))

    # retrieve contributors
    def get_contributors(self):
        if self.fid:
            temp = set()
            data = self.tree.fs.get_url('https://familysearch.org/platform/tree/couple-relationships/%s/changes.json' % self.fid)
            for entries in data['entries']:
                for contributors in entries['contributors']:
                    temp.add(contributors['name'])
            if temp:
                text = '=== ' + self.tree.fs._('Contributors') + ' ===\n' + '\n'.join(sorted(temp))
                for n in self.tree.notes:
                    if n.text == text:
                        self.notes.add(n)
                        return
                self.notes.add(Note(text, self.tree))

    # print family information in GEDCOM format
    def print(self, file=sys.stdout):
        file.write('0 @F' + str(self.num) + '@ FAM\n')
        if self.husb_num:
            file.write('1 HUSB @I' + str(self.husb_num) + '@\n')
        if self.wife_num:
            file.write('1 WIFE @I' + str(self.wife_num) + '@\n')
        for num in self.chil_num:
            file.write('1 CHIL @I' + str(num) + '@\n')
        for o in self.facts:
            o.print(file)
        if self.sealing_spouse:
            file.write('1 SLGS\n')
            self.sealing_spouse.print(file)
        if self.fid:
            file.write('1 _FSFTID ' + self.fid + '\n')
        for o in self.notes:
            o.link(file)
        for o in self.sources:
            o[0].link(file, 1)
            if len(o) > 1:
                file.write('2 PAGE ' + cont(2, o[1]) + '\n')


# family tree class
class Tree:
    def __init__(self, fs=None):
        self.fs = fs
        self.indi = dict()
        self.fam = dict()
        self.notes = list()
        self.sources = dict()

    # add individual to the family tree
    def add_indi(self, fid):
        if fid and fid not in self.indi:
            self.indi[fid] = Indi(fid, self)

    # add family to the family tree
    def add_fam(self, father, mother):
        if not (father, mother) in self.fam:
            self.fam[(father, mother)] = Fam(father, mother, self)

    # add a children relationship (possibly incomplete) to the family tree
    def add_trio(self, father, mother, child):
        self.add_indi(father)
        self.add_indi(mother)
        self.add_indi(child)
        if father:
            self.indi[father].add_fams((father, mother))
        if mother:
            self.indi[mother].add_fams((father, mother))
        self.indi[child].add_famc((father, mother))
        self.add_fam(father, mother)
        self.fam[(father, mother)].add_child(child)

    # retrieve and add parents relationships
    def add_parents(self, fid):
        father, mother = self.indi[fid].get_parents()
        if father or mother:
            self.add_trio(father, mother, fid)
        return filter(None, (father, mother))

    # retrieve and add spouse relationships
    def add_spouses(self, fid):
        rels = self.indi[fid].get_spouses()
        if rels:
            for father, mother, relfid in rels:
                self.add_indi(father)
                self.add_indi(mother)
                self.indi[father].add_fams((father, mother))
                self.indi[mother].add_fams((father, mother))
                self.add_fam(father, mother)
                self.fam[(father, mother)].add_marriage(relfid)

    # retrieve and add children relationships
    def add_children(self, fid):
        children = list()
        rels = self.indi[fid].get_children()
        if rels:
            for father, mother, child in rels:
                self.add_trio(father, mother, child)
                children.append(child)
        return children

    # retrieve ordinances
    def add_ordinances(self, fid):
        ret, famc = self.indi[fid].get_ordinances()
        if famc and famc in self.fam:
            self.indi[fid].sealing_child.famc = self.fam[famc]
        for o in ret:
            if (fid, o['spouse']['resourceId']) in self.fam:
                self.fam[(fid, o['spouse']['resourceId'])
                         ].sealing_spouse = Ordinance(o)
            elif (o['spouse']['resourceId'], fid) in self.fam:
                self.fam[(o['spouse']['resourceId'], fid)
                         ].sealing_spouse = Ordinance(o)

    # Find source by fid
    def add_source(self, fid=None):
        if fid:
            if fid in self.sources:
                return self.sources[fid]
            data = self.fs.get_url('https://familysearch.org/platform/sources/descriptions/%s.json' % fid)
            if data:
                return Source(data['sourceDescriptions'][0], self)
        return False

    def reset_num(self):
        for husb, wife in self.fam:
            self.fam[(husb, wife)].husb_num = self.indi[husb].num if husb else None
            self.fam[(husb, wife)].wife_num = self.indi[wife].num if wife else None
            self.fam[(husb, wife)].chil_num = set([self.indi[chil].num for chil in self.fam[(husb, wife)].chil_fid])
        for fid in self.indi:
            self.indi[fid].famc_num = set([self.fam[(husb, wife)].num for husb, wife in self.indi[fid].famc_fid])
            self.indi[fid].fams_num = set([self.fam[(husb, wife)].num for husb, wife in self.indi[fid].fams_fid])

    # print GEDCOM file
    def print(self, file=sys.stdout):
        file.write('0 HEAD\n')
        file.write('1 CHAR UTF-8\n')
        file.write('1 GEDC\n')
        file.write('2 VERS 5.5\n')
        file.write('2 FORM LINEAGE-LINKED\n')
        for fid in sorted(self.indi, key=lambda x: self.indi.__getitem__(x).num):
            self.indi[fid].print(file)
        for husb, wife in sorted(self.fam, key=lambda x: self.fam.__getitem__(x).num):
            self.fam[(husb, wife)].print(file)
        sources = sorted(self.sources.values(), key=lambda x: x.num)
        for s in sources:
            s.print(file)
        notes = sorted(self.notes, key=lambda x: x.num)
        for i, n in enumerate(notes):
            if i > 0:
                if n.num == notes[i - 1].num:
                    continue
            n.print(file)
        file.write('0 TRLR\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Retrieve GEDCOM data from FamilySearch Tree (4 Jul 2016)',
                                     add_help=False, usage='getmyancestors.py -u username -p password [options]')
    parser.add_argument('-u', metavar='<STR>', type=str,
                        help='FamilySearch username')
    parser.add_argument('-p', metavar='<STR>', type=str,
                        help='FamilySearch password')
    parser.add_argument('-i', metavar='<STR>', nargs='+', type=str,
                        help='List of individual FamilySearch IDs for whom to retrieve ancestors')
    parser.add_argument('-a', metavar='<INT>', type=int,
                        default=4, help='Number of generations to ascend [4]')
    parser.add_argument('-d', metavar='<INT>', type=int,
                        default=0, help='Number of generations to descend [0]')
    parser.add_argument('-m', action="store_true", default=False,
                        help='Add spouses and couples information [False]')
    parser.add_argument('-r', action="store_true", default=False,
                        help='Add list of contributors in notes [False]')
    parser.add_argument('-c', action="store_true", default=False,
                        help='Add LDS ordinances (need LDS account) [False]')
    parser.add_argument("-v", action="store_true", default=False,
                        help="Increase output verbosity [False]")
    parser.add_argument('-t', metavar='<INT>', type=int,
                        default=60, help='Timeout in seconds [60]')
    try:
        parser.add_argument('-o', metavar='<FILE>', type=argparse.FileType('w', encoding='UTF-8'), default=sys.stdout, help='output GEDCOM file [stdout]')
        parser.add_argument('-l', metavar='<FILE>', type=argparse.FileType('w', encoding='UTF-8'), default=sys.stderr, help='output log file [stderr]')
    except TypeError:
        sys.stderr.write('Python >= 3.4 is required to run this script\n')
        sys.stderr.write('(see https://docs.python.org/3/whatsnew/3.4.html#argparse)\n')
        exit(2)

    # extract arguments from the command line
    try:
        parser.error = parser.exit
        args = parser.parse_args()
    except SystemExit:
        parser.print_help()
        exit(2)

    username = args.u if args.u else input("Enter FamilySearch username: ")
    password = args.p if args.p else getpass.getpass("Enter FamilySearch password: ")

    # initialize a FamilySearch session and a family tree object
    fs = Session(username, password, args.v, args.l, args.t)
    tree = Tree(fs)

    # check LDS account
    if args.c:
        fs.get_url('https://familysearch.org/platform/tree/persons/%s/ordinances.json' % fs.get_userid())

    loop = asyncio.get_event_loop()

    # add list of starting individuals to the family tree
    todo = set(args.i if args.i else [fs.get_userid()])
    for fid in todo:
        tree.add_indi(fid)

    async def download_tree(func, todo, n, loop):
        futures = set()
        done = set()
        for i in range(n):
            next_todo = set()
            for fid in todo:
                done.add(fid)
                futures.add(loop.run_in_executor(None, func, fid))
            for future in futures:
                for parent in await future:
                    next_todo.add(parent)
            todo = next_todo - done

    # download ancestors
    loop.run_until_complete(download_tree(tree.add_parents, todo, args.a, loop))

    # download descendants
    todo = set(tree.indi.keys())
    loop.run_until_complete(download_tree(tree.add_children, todo, args.d, loop))

    # download spouses
    async def download_spouses(loop):
        futures = set()
        todo = set(tree.indi.keys())
        for fid in todo:
            futures.add(loop.run_in_executor(None, tree.add_spouses, fid))
        for future in futures:
            await future

    if args.m:
        loop.run_until_complete(download_spouses(loop))

    # download ordinances, notes and contributors
    async def download_stuff(loop):
        futures = set()
        for fid, indi in tree.indi.items():
            if args.c:
                futures.add(loop.run_in_executor(None, tree.add_ordinances, fid))
            futures.add(loop.run_in_executor(None, indi.get_notes))
            if args.r:
                futures.add(loop.run_in_executor(None, indi.get_contributors))
        for fid, fam in tree.fam.items():
            futures.add(loop.run_in_executor(None, fam.get_notes))
            if args.r:
                futures.add(loop.run_in_executor(None, fam.get_contributors))
        for future in futures:
            await future

    loop.run_until_complete(download_stuff(loop))

    # compute number for family relationships and print GEDCOM file
    tree.reset_num()
    tree.print(args.o)
