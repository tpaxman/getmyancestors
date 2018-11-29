
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np


# These are the column names of the wanted variables, produced by Oxy-Gen, with their conversions to easier names:

# In[ ]:


keep_dict = {
    'OXG_ID_INDIVIDU'  : 'person',
    'OXG_ID_FATHER'    : 'father',
    'OXG_ID_MOTHER'    : 'mother',
    'OXG_PARTNER'      : 'spouse',
    'OXG_ID_PATRONYME' : 'surname',
    'OXG_GIVNAME'      : 'firstname',
    'OXG_Sex'          : 'sex',
}


# In[ ]:


df = pd.read_csv('./test3_familytreebeard/descend_familytreebeard.csv')
df = df[list(keep_dict.keys())]
df.rename(columns=keep_dict,inplace=True)
df['sex'].replace({0:'male',1:'female'}, inplace=True)

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


class GedcomDF(pd.DataFrame):
    def  __init__(self, filename):
        self = pd.read_csv(filename)


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

