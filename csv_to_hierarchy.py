
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
            origin_couple = (int(person),int(spouse))
            break
    return origin_couple
    


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

