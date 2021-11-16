import numpy as np
import pandas as pd

diagnoses_ICD = pd.read_csv('convertcsv.csv')
print(diagnoses_ICD.query('patientID == "Aaron"')['ICD9'])
diseaseCount = diagnoses_ICD.drop_duplicates(["patientID", "ICD9"]).groupby('patientID')['ICD9'].count()

#diagnoses_ICD.group


