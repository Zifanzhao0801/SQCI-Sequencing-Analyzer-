

import streamlit as st
import pandas as pd
st.title("CosmosID Sequencing Overview")

uploaded_files = st.file_uploader("Upload your SQCI files (Make sure they end in \"Template.xlsx\")",
                                   accept_multiple_files=True, type=["xlsx"])

if uploaded_files:
     # Initialize an empty DataFrame
    overall_SQCI = pd.DataFrame()

     # Process each uploaded file
    for file in uploaded_files:
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file, header=1)
            Pooling_Run = file.name[:10]
            df.insert(0, 'Pooling_Run', Pooling_Run)
            overall_SQCI = pd.concat([overall_SQCI, df], ignore_index=True)
        else:
            st.error("Only .xlsx files are allowed. Please upload files that end with 'Template.xlsx'.")

         # Concatenate the data

    overall_SQCI["Project_ID"] = overall_SQCI["CosmosID Client Sample ID"] 

    #overall_SQCI["Quoted Reads (M Total)"] *= 1.3

    df = overall_SQCI.dropna(subset=[
        'Quoted Reads (M Total)',
        'Actual Reads (M Total)', ])

    df2 = df.copy()

     # Check for button click
    if st.button("Run Analysis"):
        projects_df = pd.DataFrame(columns=[
            'Project ID', 'Client', 'Barcode','Sample Name', 'Quoted Reads','Actual Reads','Over/Under',
            'Percentage Over/Under'
                               ])

        unique_projects = df2["Project_ID"].unique()

        for unique_project in unique_projects:
            project_id = df2.loc[df2["Project_ID"] == unique_project, "CosmosID Client Project ID (Confirm it's in CP##### Format)"].iloc[0]
            total_samples = len(df2.loc[df2["Project_ID"] == unique_project])
            client = df2.loc[df2["Project_ID"] == unique_project, "Customer"].iloc[0]
            barcode = df2.loc[df2["Project_ID"]== unique_project,"Original Barcode"].iloc[0]
            sample_name = df2.loc[df2["Project_ID"]== unique_project,"Sequencing Lab ID"].iloc[0]
            quoted_reads = df2.loc[df2["Project_ID"]== unique_project,"Quoted Reads (M Total)"].iloc[0]
            actual_reads = df2.loc[df2["Project_ID"]== unique_project,"Actual Reads (M Total)"].iloc[0]
            difference = quoted_reads-actual_reads
            percentage_over_under = (difference/actual_reads)*100
            run_id_series = df2.loc[df2["Project_ID"] == unique_project, "Pooling_Run"]
            run_id = run_id_series.iloc[0] if not run_id_series.empty else 'Unknown'
            quoted = df2.loc[df2["Project_ID"] == unique_project, "Quoted Reads (M Total)"].sum()
            total_reads = df2.loc[df2["Project_ID"] == unique_project]["Actual Reads (M Total)"].sum()

             # Create a new row as a DataFrame
            new_row = pd.DataFrame({
                 'Project ID': [project_id],
                 'Client':[client],
                 'Barcode':[barcode],
                 'Sample Name':[sample_name],
                 'Quoted Reads':[quoted_reads],
                 'Actual Reads':[actual_reads],
                 'Over/Under':[difference],
                 'Percentage Over/Under':[percentage_over_under]


            })

            projects_df = pd.concat([projects_df, new_row], ignore_index=True)

        for column in [

             'Percentage Over/Under'
         ]:
             projects_df[column] = projects_df[column]

        projects_df.dropna(subset=["Project ID"], inplace=True)

        st.write(projects_df)

#remark part        
    remark_SQCI = overall_SQCI.copy()
    remark_SQCI["Project_ID"] = remark_SQCI["CosmosID Client Project ID (Confirm it's in CP##### Format)"] + "_" + \
                                remark_SQCI["Customer"]
    #remark_SQCI["Quoted Reads (M Total)"] *= 1.3
    df_remark = remark_SQCI.dropna(subset=[
        'Quoted Reads (M Total)',
        'Actual Reads (M Total)', ])

    df3 = df_remark.copy()


    remark_unique_projects = df3["Project_ID"].unique()

    for remark_unique_project in remark_unique_projects:
            remark_total_samples = len(df3.loc[df3["Project_ID"] == remark_unique_project])

            remark_quoted = df3.loc[df3["Project_ID"] == remark_unique_project, "Quoted Reads (M Total)"].sum()
            remark_total_reads = df3.loc[df3["Project_ID"] == remark_unique_project]["Actual Reads (M Total)"].sum()

            remark_difference = (remark_total_reads - remark_quoted) / remark_total_samples


            remark_percentage_above_quoted = 0
            remark_percentage_below_quoted = 0
            if remark_total_samples != 0:
                remark_percentage_above_quoted = (remark_difference[remark_difference >= 0].sum() / remark_quoted) *100
                remark_percentage_below_quoted = (remark_difference[remark_difference < 0].sum() / remark_quoted) * 100


            if remark_percentage_above_quoted >50:
                st.write('To Conclude, sample', remark_unique_project ,'is bad since it overperformed on average'
                         ,remark_difference, 'which is',remark_percentage_above_quoted,'%')
            if remark_percentage_above_quoted <0:
                 st.write('To Conclude, sample', remark_unique_project ,'is bad since it underperformed on average'
                         ,remark_difference, 'which is',remark_percentage_below_quoted,'%' )
            if remark_percentage_above_quoted >0 and remark_percentage_above_quoted <50 :
                 st.write('To Conclude, sample', remark_unique_project ,'is good since it has'
                         ,remark_difference, 'which is',remark_percentage_above_quoted,'%' )
            



