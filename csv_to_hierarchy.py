
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


# In[ ]:


df.head()


# Find oldest couple of the set

# In[ ]:


np.isnan([float('nan'), 2, 3, 4]).any()


# In[ ]:


for index, row in df.iterrows():
    if np.isnan([row.father, row.mother, ])
    if np.isnan(row.father) & np.isnan()


# In[ ]:


for person in df.person:
    mother = df.loc[df.person==person,'mother'].values[0]
    father = df.loc[df.person==person,'father'].values[0]
    spouse = df.loc[df.person==person,'spouse'].values[0]
    spousemother = df.loc[df.person==spouse, 'mother'].values[0]
    spousefather = df.loc[df.person==spouse, 'father'].values[0]
    print(mother,father,spouse,spousemother,spousefather)


# In[ ]:


df.reset_index(inplace=True)
df.set_index('person',inplace=True)


# In[ ]:


df


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

