
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import datetime as dt


# # CLASS

# In[ ]:


class OxyGen(pd.DataFrame):
    
    def  __init__(self, filename, change_headers=True):
        KEEP_DICT = {
        'OXG_ID_INDIVIDU'  : 'person',
        'OXG_ID_FATHER'    : 'father',
        'OXG_ID_MOTHER'    : 'mother',
        'OXG_PARTNER'      : 'spouse',
        'OXG_ID_PATRONYME' : 'surname',
        'OXG_GIVNAME'      : 'firstname',
        'OXG_BIRTH_DATE'   : 'birthday', 
        'OXG_Sex'          : 'sex',
        }
        SEX_DICT = {0:'male',1:'female'}
        df = pd.read_csv(filename)
        
        if change_headers==True:
            df = df[list(KEEP_DICT.keys())]
            df.rename(columns=KEEP_DICT,inplace=True)
        df['sex'].replace(SEX_DICT, inplace=True)
        df.set_index('person',inplace=True)
        super().__init__(df)

    def is_couple(self,person1,person2):
        df = self
        if df.spouse[person1] == person2:
            return True
        else:
            return False
        
    def find_origin_couple(self):
        df = self
        people_with_no_parents = df[np.isnan(df.mother) & np.isnan(df.father)].index
        for person in people_with_no_parents:
            spouse = df.spouse[person]
            spousemother = df.mother[spouse]
            spousefather = df.father[spouse]
            if np.isnan([spousemother,spousefather]).all():
                if df.sex[person]=='male':
                    origin_couple = {'father':person, 'mother':spouse}
                elif df.sex[person=='female']:
                    origin_couple = {'father':spouse, 'mother':person}
                break
        return origin_couple
    
    def find_children(self, *args):
        df = self
        parents = args
        num_parents = len(parents)
        assert (num_parents <= 2), 'too many parent inputs (1 or 2 only)'
        assert (num_parents > 0), 'not enough parent inputs'
        if num_parents == 2:
            parent1 = parents[0]
            parent2 = parents[1]
            assert self.is_couple(parent1,parent2), 'not a couple'
            if df.sex[parent1]=='male':
                father = parent1
                mother = parent2
            else:
                mother = parent1
                father = parent2
            father_slicer = (df.father==father)
            mother_slicer = (df.mother==mother)
            children_row = df[father_slicer & mother_slicer].sort_values(by=['birthday'])
        elif num_parents == 1:
            parent = parents[0]
            if df.sex[parent]=='male':
                children_row = df[df.father==parent]
            else:
                children_row = df[df.mother==parent]
        children_row = children_row.sort_values(by=['birthday'])    
        return children_row

    def find_spouse(self,person):
        df = self
        spouse = df.loc[person,'spouse']
        spouse_row = df[df.index == spouse]
        return spouse_row
        
        """if np.isnan(spouse):
            return None
        else: 
            return spouse.astype(int)"""
    
    def find_children_and_spouses(self,father=None,mother=None):
        children = self.find_children(father,mother)
        spouses = self.find_spouse(children)
        children_and_spouse_tup = tuple(zip(spouses.index,spouses))
        return children_and_spouse_tup
    
    def assign_generation_to_person(self,person):
        x
        
#TEST_FILE = './test3_familytreebeard/descend_familytreebeard.csv'
#og = OxyGen('./test3_familytreebeard/descend_familytreebeard.csv')
og = OxyGen('./test4_ursenbach_actual_family/nana_and_grandad_descendants.csv',change_headers=False)


# # TESTS

# In[ ]:


for person, row in og.iterrows():
    og.loc[person,'children'] = [[tuple(og.find_children(person).index)]]
    


# In[ ]:


"""og['branch']=''
og['gen']=''

orig_couple = og.find_origin_couple()
father = orig_couple['father']
mother = orig_couple['mother']
children = og.find_children(father=father,mother=mother)"""

def print_branch_name(og,person,childnum):
    print(og.firstname[person],og.surname[person])
    spouse = og.find_spouse(person).index
    if not np.isnan(spouse):
        children = og.find_children.index
        if not children.empty:
            print_branch_name()
    else:
        break
    
children = og.find_children(0,4)
for index, person in enumerate(children.index):
    print_branch_name(og,person,index)


# In[ ]:


def print_branch_name(og,children,current_gen=0):
    if not children.empty:
        current_gen += 1
        gen_marker = '#' * (current_gen+1)
        for index, person in enumerate(children):
            spouse_row = og.find_spouse(person)
            if not spouse_row.empty:
                spouse = spouse_row.index[0]
                print(gen_marker, og.firstname[person],og.surname[person],'/',
                      og.firstname[spouse],og.surname[spouse])
                children = og.find_children(person,spouse).index
                print_branch_name(og,children,current_gen)
            else:
                print(gen_marker, og.firstname[person],og.surname[person])


origin_couple = og.find_origin_couple()
mom = origin_couple['mother']
dad = origin_couple['father']
current_gen=0
gen_marker = '#' * (current_gen+1)
print(gen_marker, og.firstname[dad],og.surname[dad],'/',
      og.firstname[mom],og.surname[mom])
children = og.find_children(mom,dad).index
print_branch_name(og,children,current_gen)


# In[ ]:


children = og.find_children(0,4).index
for index, person in enumerate(children):
    print(og.firstname[person],og.surname[person])


# In[ ]:


x=og.find_spouse(1).index[0]
og.find_children(1,x)


# In[ ]:


og.find_children().index.empty


# In[ ]:


def add_branch_name(og, person):
    spouse = og.spouse[person]
    father = og.father[person]
    mother = og.mother[person]
    couple_branch = og.branch[father] + BRANCH_NAME_ORDER[index]
    og.loc[person,'branch'] = couple_branch
    og.loc[spouse,'branch'] = couple_branch
    
    og = add_branch_name(og, new_father, new_mother)
    
    if children.empty:
        return og
    else:
        for index, person in enumerate(children.index):
            spouse = og.spouse[person]
            father = og.father[person]
            mother = og.mother[person]
            couple_branch = og.branch[father] + BRANCH_NAME_ORDER[index]
            og.loc[person,'branch'] = couple_branch
            og.loc[spouse,'branch'] = couple_branch
            new_father = person if og.sex[person]=='male' else spouse
            new_mother = og.spouse[new_father]
            og = add_branch_name(og, new_father, new_mother)
            return og


# In[ ]:


og['branch']=''
og['gen']=''
BRANCH_NAME_ORDER = 'abcdefghijklmnopqqrstuvwxyz'

orig_couple = og.find_origin_couple()
father = orig_couple['father']
mother = orig_couple['mother']
children = og.find_children(father,mother)

for index, person in enumerate(children.index):
    spouse = og.spouse[person]
    father = og.father[person]
    mother = og.mother[person]
    couple_branch = og.branch[father] + BRANCH_NAME_ORDER[index]
    og.loc[person,'branch'] = couple_branch
    og.loc[spouse,'branch'] = couple_branch
    
    father = person if og.sex[person]=='male' else spouse
    mother = og.spouse[father]
    print(og.firstname[father],og.firstname[mother])
    children = og.find_children(father,mother)
    for index, person in enumerate(children.index):
        spouse = og.spouse[person]
        father = og.father[person]
        mother = og.mother[person]
        couple_branch = og.branch[father] + BRANCH_NAME_ORDER[index]
        og.loc[person,'branch'] = couple_branch
        og.loc[spouse,'branch'] = couple_branch
        
        father = person if og.sex[person]=='male' else spouse
        mother = og.spouse[father]
        print(og.firstname[father],og.firstname[mother])
        children = og.find_children(father,mother)
        for index, person in enumerate(children.index):
            spouse = og.spouse[person]
            father = og.father[person]
            mother = og.mother[person]
            couple_branch = og.branch[father] + BRANCH_NAME_ORDER[index]
            og.loc[person,'branch'] = couple_branch
            og.loc[spouse,'branch'] = couple_branch
            
og


# In[ ]:


og['branch']=''
og['gen']=''

orig_couple = og.find_origin_couple()
father = orig_couple['father']
mother = orig_couple['mother']
children = og.find_children(father=father,mother=mother)

def add_branch_names(og, children):
    if children.empty:
        return og
    else:
        for index, person in enumerate(children.index):
            spouse = og.spouse[person]
            father = og.father[person]
            mother = og.mother[person]
            couple_branch = og.branch[father] + BRANCH_NAME_ORDER[index]
            og.loc[person,'branch'] = couple_branch
            og.loc[spouse,'branch'] = couple_branch
            new_father = person if og.sex[person]=='male' else spouse
            new_mother = og.spouse[new_father]
            og = add_branch_name(og, new_father, new_mother)
            return og
    
""" father = person if og.sex[person]=='male' else spouse
mother = og.spouse[father]
children = og.find_children(father=father,mother=mother)
for index, person in enumerate(children.index):
    spouse = og.spouse[person]
    father = og.father[person]
    mother = og.mother[person]
    couple_branch = og.branch[father] + BRANCH_NAME_ORDER[index]
    og.loc[person,'branch'] = couple_branch
    og.loc[spouse,'branch'] = couple_branch

    father = person if og.sex[person]=='male' else spouse
    mother = og.spouse[father]
    children = og.find_children(father=father,mother=mother)
    for index, person in enumerate(children.index):
        spouse = og.spouse[person]
        father = og.father[person]
        mother = og.mother[person]
        couple_branch = og.branch[father] + BRANCH_NAME_ORDER[index]
        og.loc[person,'branch'] = couple_branch
        og.loc[spouse,'branch'] = couple_branch       """ 


# In[ ]:


og = add_branch_name(og,0,4)


# In[ ]:


date(1988)


# In[ ]:


for person in children_1:
    print(person in children_1)


# In[ ]:


BRANCH_NAME_ORDER = 'abcdefghijklmnopqrstuvwxyz'
dict(zip(range(0, len(BRANCH_NAME_ORDER)), BRANCH_NAME_ORDER))


# In[ ]:


def find_children(df,father=None,mother=None):
    #father_bool = df.father==father if father==none
    
    father_arg = (father!=None)
    mother_arg = (mother!=None)
    
    if (father != None) & (mother != None):
        children = df[(df.father==father) & (df.mother==mother)].index.tolist()
    elif (father != None) & (mother == None):
        children = df[(df.father==father)].index.tolist()
    elif (father == None) & (mother != None):
        children = df[(df.mother==mother)].index.tolist()
    elif (father == None) & (mother == None):
        children = []
    
    
    return children


# In[ ]:


def convert_to_int(values):
    if np.isnan(values).any():
        return values
    else:
        int_values = [int(a) for a in values] # DOESN'T WORK IF VALUES ISN'T ITERABLE!? WHYYY
        return int_values

x = [float('nan'),2.0,3.0]
y = [1.0,2.0,3.0]
convert_to_int(1)


# ## Class Instance

# In[ ]:


[int(x) for x in [1.,2.,3.]]


# In[ ]:


ged_actual.find_origin_couple()


# In[ ]:


ged_actual.find_children(0,4)


# In[ ]:


ged_actual.find_spouse([1,2,4])


# ## Sandbox

# In[ ]:


def find_spouse(df,person):
    


# In[ ]:


def find_children(df,father,mother):
    df[(df.father==father) & (df.mother==mother)].index.tolist()


# In[ ]:


df[(df.mother==4) & (df.father==0)].index.tolist()


# In[ ]:


#df = df[list(keep_dict.keys())]
#df.rename(columns=keep_dict,inplace=True)
#df['sex'].replace({0:'male',1:'female'}, inplace=True)

df.set_index('person',inplace=True)

"""for index, row in df.iterrows():
    person = index
    father = row.father
    mother = row.mother
    spouse = row.spouse
    spousemother = df.mother[spouse]
    spousefather = df.father[spouse]
    print(person,father,mother,spouse,spousemother,spousefather)
    """

#np.isnan([float('nan'), 2, 3, 4]).any()

def find_origin_couple(df):
    people_with_no_parents = df[np.isnan(df.mother) & np.isnan(df.father)].index
    for person in people_with_no_parents:
        spouse = df.spouse[person]
        spousemother = df.mother[spouse]
        spousefather = df.father[spouse]
        if np.isnan([spousemother,spousefather]).all():
            if df.sex[person]=='male':
                origin_couple = {'male':person, 'female':spouse}
            elif df.sex[person=='female']:
                origin_couple = {'male':spouse, 'female':person}
            break
    return origin_couple
    


# In[ ]:


def find_children(df,father,mother):
    print(df.mother, df.father)
    
find_children(df,0,4)
    


# In[ ]:


class Ged():
    def  __init__(self, filename):
        self.df = pd.read_csv(filename)


# In[ ]:


X = Ged('./test3_familytreebeard/descend_familytreebeard.csv')


# In[ ]:


X.df


# In[ ]:


def mmm():
    a = 2
    b = 3
    def h(k):
        return k*b
    return h(a)

    


# In[ ]:


mmm()


# # SCRAP

# In[ ]:


def find_mother(df,person):
    return df.mother[person]


# In[ ]:


x=[]
for person, row in df.iterrows():
    spouse = row.spouse
    spouseparent = df[parenttype]
    if spousetype == 'mother':
        spouseparent = df.mother[spouse]
    elif spousetype == 'father':
        spouseparent = df.mother[spouse]
    x.append(spouseparent)


# In[ ]:


person = 6
row = df.loc[person,:]
print(row)


# In[ ]:


df_parentless = df[np.isnan(df.mother) & np.isnan(df.father)]
persons_parentless = df_parentless.index
spouses_parentless = df_parentless.spouse
#df_parentless.loc[spouses_parentless]

a = df_parentless.index
b = df_parentless.spouse
for index, row in df_parentless.iterrows():
    print(index in b.values)


# In[ ]:


df_people_noparents = df[np.isnan(df.mother) & np.isnan(df.father)]
#df_people_noparents_spouses


# In[ ]:


df_people_noparents


# In[ ]:


p = find_origin_couple(df)
(df.father==p['male']) & (df.mother==p['female'])
#df[df.father==p[1] & df.mother==p[0]]


# In[ ]:


find_origin_couple(df)


# In[ ]:


for person in df.person:
    mother = df.mother[person]
    father = df.father[person]
    spouse = df.spouse[person]
    spousemother = df.mother[spouse]
    spousefather = df.father[spouse]
    print(person,spouse,father,mother)
    #person_row = df[df.person==person]
    #spouse_row = df[df.person==spouse]
    #print(person_row.firstname[person])
    #print(spouse_row.firstname[spouse])
    
# df.loc[np.isnan(df.father) & np.isnan(df.mother)]


# In[ ]:


df

