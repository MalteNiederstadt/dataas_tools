import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from scipy.stats import shapiro,levene,ttest_ind,mannwhitneyu
import plotly.graph_objects as go

upload_df = st.file_uploader("upload file", type={"csv", "txt"})
col1, col2 = st.columns(2)
if upload_df is not None:
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



    normality_dict = {}
    homogeneity_dict = {}
    dataset1 = df[df[group_column]==groups_to_compare[0]]
    dataset2 = df[df[group_column]==groups_to_compare[1]]
    if st.button('Perform A/B Test'):
        # st.write(dataset1["bounce_rate"].mean())
        # st.write(dataset2["bounce_rate"].mean())

        
        #
        # 
        # st.write(f'Selected groups : {",".join(list(groups_to_compare))}')
        for column in metric_columns:
                stat, p = shapiro(dataset1[column])
                if p >= 0.05:
                    print(f"{column}: Data appears to be normally distributed")
                   # if assumption of normality on dataset 1 is confirmed, check against dataset 2 to confirm the normality on both datasets
                    stat, p = shapiro(dataset2[column])
                    if p < 0.05:
                         normality_dict[column] = False
                    else:
                         normality_dict[column] = True
                # if assumption of normality on dataset 1 is refuted, set value for that column to False
                else:
                    print(f"{column}:Data does not appear to be normally distributed")
                    normality_dict[column] = False


        st.write(normality_dict)

        for column in metric_columns:
                stat, p = levene(dataset1[column], dataset2[column])
                if p >= 0.05:
                    print(f"{column}: Homogeneity of variances is met")
                    homogeneity_dict[column] = True
                else:
                    homogeneity_dict[column] = False
        st.write(homogeneity_dict)

        method = None
        results = pd.DataFrame(columns=['Gruppe 1', 'Gruppe 2', 'KPI', 'Durchschnitt 1', 'Durchschnitt 2' , 'p', 'Signifikant', 'Testmethode'])
        alpha = 0.05
        for key,value in normality_dict.items():
            if value == True and homogeneity_dict[key] == True:
                t, p = ttest_ind(dataset1[key], dataset2[key])
                method = 'T-Test'
            else:
                t, p = mannwhitneyu(dataset1[key], dataset2[key], alternative='two-sided')  
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
        
        
        def highlight_larger_value(row):
            max_col = 'Durchschnitt 1' if row['Durchschnitt 1'] > row['Durchschnitt 2'] else 'Durchschnitt 2'
            styles = ['background-color: yellow' if col == max_col else '' for col in row.index]
            return styles

        # Use st.dataframe with custom styling
        st.dataframe(results.style.apply(highlight_larger_value, axis=1))



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

                  
  

           