
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np


# # CLASS

# In[ ]:


class OxyGen(pd.DataFrame):
    
    def  __init__(self, filename):
        KEEP_DICT = {
        'OXG_ID_INDIVIDU'  : 'person',
        'OXG_ID_FATHER'    : 'father',
        'OXG_ID_MOTHER'    : 'mother',
        'OXG_PARTNER'      : 'spouse',
        'OXG_ID_PATRONYME' : 'surname',
        'OXG_GIVNAME'      : 'firstname',
        'OXG_Sex'          : 'sex',
        }
        SEX_DICT = {0:'male',1:'female'}
        df = pd.read_csv(filename)
        df = df[list(KEEP_DICT.keys())]
        df.rename(columns=KEEP_DICT,inplace=True)
        df['sex'].replace(SEX_DICT, inplace=True)
        df.set_index('person',inplace=True)
        super().__init__(df)
        
    def find_origin_couple(self):
        df = self
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
    
    def find_children(self,father=None,mother=None):
        df = self
        
        father_slicer = (df.father==father) if father!=None else True
        mother_slicer = (df.mother==mother) if mother!=None else True
        
        df_bool = father_slicer & mother_slicer    
        
        """if (father != None) & (mother != None):
            df_bool = (df.father==father) & (df.mother==mother)
        elif (father != None) & (mother == None):
            df_bool = (df.father==father)
        elif (father == None) & (mother != None):
            df_bool = (df.mother==mother)
        elif (father == None) & (mother == None):
            df_bool = (df.mother==mother)"""
        children = df[df_bool].index.tolist()
        return children

    def find_spouse(self,person):
        df = self
        spouse = df.spouse[person]
        return spouse


# # TESTS

# In[ ]:


TEST_FILE = './test3_familytreebeard/descend_familytreebeard.csv'
og = OxyGen(TEST_FILE)


# In[ ]:


og.find_children(0,4)


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


father = 0
mother = 4



df[(df.father==father) | (df.mother==mother)].index.tolist()


# In[ ]:


og.find_children(father=2,mother=4)


# In[ ]:


find_children(og,0,4)


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

