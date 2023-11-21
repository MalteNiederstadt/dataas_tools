import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from scipy.stats import shapiro,levene,ttest_ind,mannwhitneyu
import plotly.graph_objects as go
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb

upload_df = st.file_uploader("upload file", type={"csv", "txt",'xlsx'})
col1, col2 = st.columns(2)
#read uploaded file , provide options of columns in form of checkbox / radiobutton 
if upload_df is not None:
    if upload_df.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(upload_df)
    else:
        df = pd.read_csv(upload_df)
    st.dataframe(df)
    with col1:
        st.caption('Choose the column defining the group')
        group_column = st.radio("Select the group column", df.columns)
        st.write(f'Selected group column: {group_column}')
        groups = list(df[group_column].unique())
        groups.sort()
        groups_to_compare = set()
        st.caption('Choose two groups to run the A/B test on')
        for group in groups:
            groups_add = st.checkbox(f"{group}", False,key=f"group_{group}")
            if groups_add:
                groups_to_compare.add(group)
        groups_to_compare = list(groups_to_compare)
    with col2:
        metric_columns = set()
        st.caption('Choose the columns defining the metrics which the test should be performed on')
        for column in df.columns:
            metric_add = st.checkbox(f"{column}", False,key=f"metric_{column}")
            if metric_add:
                metric_columns.add(column)
        st.write(f'Selected metric columns: {",".join(list(metric_columns))}')




    #setup dictionaries and datasets to be used in normality test , homogeneity test , and a b test
    normality_dict = {}
    homogeneity_dict = {}
    groups_to_compare.sort()
    if len(groups_to_compare) == 2:
        dataset1 = df[df[group_column]==groups_to_compare[0]]
        dataset2 = df[df[group_column]==groups_to_compare[1]]

    def normality_test(df1,df2,column):
        _, p = shapiro(df1[column])
        _, p2 = shapiro(df2[column])
        if p > 0.05 and p2 > 0.05:
            return True
        else:
            return False
    
    def homogeneity_test(df1,df2,column):
        _, p = levene(df1[column], df2[column])
        if p > 0.05: 
            return True
        else:
            return False
        
    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        format1 = workbook.add_format({'num_format': '0.00'}) 
        worksheet.set_column('A:A', None, format1)  
        writer.save()
        processed_data = output.getvalue()
        return processed_data
        

    #button to perform the a b test    
    if st.button('Perform A/B Test'):
        #run tests for normality and homogeneity
        for column in metric_columns:
            normality_dict[column] = normality_test(dataset1,dataset2,column)
            homogeneity_dict[column] = homogeneity_test(dataset1,dataset2,column)

        method = None
        results = pd.DataFrame(columns=['Gruppe 1', 'Gruppe 2', 'KPI', 'Durchschnitt 1', 'Durchschnitt 2' , 'p', 'Signifikant', 'Testmethode'])
        alpha = 0.05

        #run a b test based on normality and homogeneity tests
        for key,value in normality_dict.items():
            #check if normality assumption is confirmed, and homogeneity assumption (for the same column is confirmed)
            if value == True and homogeneity_dict[key] == True:
                _, p = ttest_ind(dataset1[key], dataset2[key])
                method = 'T-Test'
            else:
                _, p = mannwhitneyu(dataset1[key], dataset2[key], alternative='two-sided')  
                method = 'Mann-Whitney U'

            results_new_row = {
            'Gruppe 1': groups_to_compare[0],
            'Gruppe 2': groups_to_compare[1],
            'KPI': key,
            'Durchschnitt 1': dataset1[key].mean(),
            'Durchschnitt 2': dataset2[key].mean(),
            'p': p,
            'Signifikant': True if p < alpha else False,
            'Testmethode': method
             }
            results_new_row = pd.DataFrame([results_new_row])
            results = pd.concat([results, results_new_row], ignore_index=True)
        
        
        # Define the first custom styling function to highlight the larger value column
        def highlight_larger_value(row):
            max_col = 'Durchschnitt 1' if row['Durchschnitt 1'] > row['Durchschnitt 2'] else 'Durchschnitt 2'
            styles = ['background-color: yellow' if col == max_col else '' for col in row.index]
            return styles

        # Define the second custom styling function to highlight significant rows
        def highlight_significant_rows(row):
            styles = ['font-weight: bold;' if row['p'] < alpha else '' for _ in row.index]
            return styles

        # Apply the custom styling functions and combine the styles
        def apply_custom_styles(df):
            styled_df = df.style.apply(highlight_larger_value, axis=1)
            styled_df = styled_df.apply(highlight_significant_rows, axis=1)
            return styled_df

        # Apply the custom styles to the DataFrame
        styled_results = apply_custom_styles(results)

        # Render the styled DataFrame
        #st.dataframe(styled_results)
        st.write(styled_results.to_html(), unsafe_allow_html=True)
        df_xlsx = to_excel(styled_results)
        file_name = str(upload_df.name).split('.')[0]
        st.download_button(label='📥 Download Results',
                                        data=df_xlsx ,
                                        file_name= f'{groups_to_compare[0]}_{groups_to_compare[1]}_{file_name}.xlsx')

    #return a bunch of histograms
    if st.button('Plots Plots Plots'):
        for column in metric_columns:
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=dataset1[column], name=f'{groups_to_compare[0]}:{column}', marker_color='#1f77b4'))
                fig.add_trace(go.Histogram(x=dataset2[column],  name=f'{groups_to_compare[1]}:{column}', marker_color='#d62728'))

                # Overlay both histograms
                fig.update_layout(barmode='overlay')
                # Reduce opacity to see both histograms
                fig.update_traces(opacity=0.75)
                #fig.show()
                #fig = px.histogram(df, x=column, color=group_column)
                st.plotly_chart(fig, use_container_width=True)

                  
  

           