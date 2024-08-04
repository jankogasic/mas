import pandas as pd

df_student_info = pd.read_csv('data/studentInfo.csv')
df_student_registration = pd.read_csv('data/studentRegistration.csv')

# Remove students who have unregistered prior to the deadline (arbitrary selected to be 90 days)
valid_students = (df_student_registration['date_unregistration'].isna()) | (df_student_registration['date_unregistration'] > 90)
key_columns = ['code_module', 'code_presentation', 'id_student']
df_student_registration = df_student_registration[valid_students]
df_student_registration = df_student_registration[key_columns]

df_student_info = df_student_info.merge(df_student_registration, on=key_columns, how='inner')

# Deal with categorical attributes
df_student_info['gender'] = df_student_info['gender'].map({'M': 0, 'F': 1})
df_student_info['disability'] = df_student_info['disability'].map({'N': 0, 'Y': 1})
df_student_info = pd.get_dummies(df_student_info, columns=['region', 'highest_education', 'imd_band', 'age_band'], dtype=int)

df_student_info['final_result'] = df_student_info['final_result'].map({'Pass': 0, 'Distinction':0, 'Withdrawn': 1, 'Fail': 1})

# Add VLE attributes
df_vle = pd.read_csv('data/vle.csv')
df_studentvle = pd.read_csv('data/studentVle.csv')

df_studentvle = df_studentvle.merge(df_vle, on=['code_module', 'code_presentation', 'id_site'], how='left')
df_studentvle = df_studentvle.drop('id_site', axis=1)
df_studentvle = df_studentvle.loc[df_studentvle['date'] <= 90, :]
df_studentvle['week_of_interaction'] = round(df_studentvle['date']/7)

df_studentvle_clicks = df_studentvle.groupby(key_columns)['sum_click'].sum().reset_index()

df_studentvle_activity_click = df_studentvle.pivot_table(index=key_columns, values=['sum_click'], columns=['activity_type'], aggfunc='sum', fill_value=0)
df_studentvle_activity_click.columns = ['_'.join(col).strip() for col in df_studentvle_activity_click.columns.values]
prefix = 'studentvle_activity_type_'
df_studentvle_activity_click.columns = [prefix + col for col in df_studentvle_activity_click.columns]
df_studentvle_activity_click = df_studentvle_activity_click.reset_index()

df_studentvle_week_of_interaction = df_studentvle.pivot_table(index=key_columns, values=['sum_click'], columns=['week_of_interaction'], aggfunc='sum', fill_value=0)
df_studentvle_week_of_interaction.columns = ['_'.join([str(col) for col in col_tuple]).strip() for col_tuple in df_studentvle_week_of_interaction.columns.values]
prefix = 'studentvle_week_of_interaction_'
df_studentvle_week_of_interaction.columns = [prefix + col for col in df_studentvle_week_of_interaction.columns]
df_studentvle_week_of_interaction = df_studentvle_week_of_interaction.reset_index()

df_student_info = df_student_info.merge(df_studentvle_clicks, on=key_columns, how='left')
df_student_info = df_student_info.merge(df_studentvle_activity_click, on=key_columns, how='left')
df_student_info = df_student_info.merge(df_studentvle_week_of_interaction, on=key_columns, how='left')

df_student_info = df_student_info.fillna(0)

# Adding Assessment attributes
df_assessment = pd.read_csv('data/assessments.csv')
df_studentAssessment = pd.read_csv('data/studentAssessment.csv')

df_studentAssessment = df_studentAssessment.merge(df_assessment, on=['id_assessment'], how='left')
df_studentAssessment['time_of_assessment'] = df_studentAssessment['date'] - df_studentAssessment['date_submitted']
df_studentAssessment['weighted_score'] = df_studentAssessment['score'] * df_studentAssessment['weight'] / 100

df_studentAssessment_weighted_score = df_studentAssessment.groupby(key_columns)['weighted_score'].sum().reset_index()
df_studentAssessment_time_of_assessment = df_studentAssessment.groupby(key_columns)['time_of_assessment'].mean().reset_index()

df_studentAssessment_weighted_score = df_studentAssessment.pivot_table(index=key_columns, values=['weighted_score'], columns=['assessment_type'], aggfunc='sum', fill_value=0)
df_studentAssessment_weighted_score.columns = ['_'.join([str(col) for col in col_tuple]).strip() for col_tuple in df_studentAssessment_weighted_score.columns.values]
prefix = 'student_assessment_'
df_studentAssessment_weighted_score.columns = [prefix + col for col in df_studentAssessment_weighted_score.columns]
df_studentAssessment_weighted_score = df_studentAssessment_weighted_score.reset_index()

df_studentAssessment_type = df_studentAssessment.pivot_table(index=key_columns, values=['time_of_assessment'], columns=['assessment_type'], aggfunc='sum', fill_value=0)
df_studentAssessment_type.columns = ['_'.join([str(col) for col in col_tuple]).strip() for col_tuple in df_studentAssessment_type.columns.values]
prefix = 'student_assessment_type_'
df_studentAssessment_type.columns = [prefix + col for col in df_studentAssessment_type.columns]
df_studentAssessment_type = df_studentAssessment_type.reset_index()

df_student_info = df_student_info.merge(df_studentAssessment_weighted_score, on=key_columns, how='left')
df_student_info = df_student_info.merge(df_studentAssessment_time_of_assessment, on=key_columns, how='left')
df_student_info = df_student_info.merge(df_studentAssessment_weighted_score, on=key_columns, how='left')
df_student_info = df_student_info.merge(df_studentAssessment_type, on=key_columns, how='left')

df_student_info = df_student_info.fillna(0)

df_student_info['label'] = df_student_info['final_result']
df_student_info = df_student_info.drop('final_result', axis=1)

df_student_info.to_csv('data/student_pred_problem.csv', index=False)