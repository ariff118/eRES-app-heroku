# import os
import streamlit as st
import pandas as pd
import tabula
from tabula.io import read_pdf
import base64
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pandas.api.types import CategoricalDtype
from IPython.display import display, HTML

################################################################################
####                               MAIN ANALYSIS                             ###
################################################################################

frame_text = st.sidebar.write("## e-RES Report UiTM Kedah v1.0")
image = st.sidebar.image("logo fakulti.png")
rad = st.sidebar.radio("Menu",["Home","Analysis", "Report", "About Us"])
# LE15 = st.sidebar.file_uploader("Upload LE15 File: ")
# PLO = st.sidebar.file_uploader("Upload PLO File: ")

#LE15 = st.sidebar.text_input('Copy and Paste or type the file location here (example: E:\eRES\LE15.pdf): ', "Type Here ...")
#PLO = st.sidebar.text_input('Copy and Paste or type the file location here (example: E:\eRES\PLO.pdf): ', "Type Here ...")


LE15 = st.sidebar.file_uploader("Choose LE15 file")
if LE15 is not None:
    df_le15 = read_pdf(LE15, pages = "all", multiple_tables = True)
    st.sidebar.write('Successfully uploaded File:', LE15)

PLO = st.sidebar.file_uploader("Choose PLOA file")
if LE15 is not None:
    df_PLO = read_pdf(PLO, pages = "all", multiple_tables = True)
    st.sidebar.write('Successfully uploaded File:', PLO)

# FROM HOME TAB
# LE15 = st.write("Your LE15 File Location is: ", LE15)
# PLO = st.write("Your PLO File Location is: ", PLO)

# FROM ANALYSIS TAB

#def file_selector2(folder_path='./'):
#    filenames2 = os.listdir(folder_path)
#    selected_filename2 = st.selectbox2('Select a file', filenames2)
#    return os.path.join(folder_path, selected_filename2)

###################################################################
# Get Program Information from LE15 eRES pdf file                 #
###################################################################

# file_path = input('Copy and Paste or type the file location here (example: E:\eRES\LE15.pdf): ')
# file_path = "./LE15.pdf"

#file_path1 = file_selector1()
#st.write('You selected `%s`' % file_path1)

# using file path to read data
# df_le15 = read_pdf(file_path1, pages = "all", multiple_tables = True)
# df_le15 = read_pdf(LE15, pages = "all", multiple_tables = True)

# concatenate columns
df_le15_combined = pd.concat(df_le15[0:len(df_le15)])
df_le15_combined.reset_index(drop=True, inplace=True)

# select column
df_le15_selection = df_le15_combined.iloc[:, [1,7]]

# reset LE15 index
df_le15_selection.reset_index(drop=True, inplace=True)


###################################################################
# Get PLO Grade Inforamtion from PLOA eRES pdf files             #
# (Note: removed the headings before uploading)                   #
###################################################################

# file_path2 = input('Copy and Paste or type the file location here (example: E:\eRES\PLO.pdf): ')
# file_path2 = "./PLO.pdf"
#file_path2 = file_selector2()
#st.write('You selected `%s`' % file_path2)

# using file path
# df_PLO = read_pdf(file_path2, pages = "all", multiple_tables = True)
# df_PLO = read_pdf(PLO, pages = "all", multiple_tables = True)
df_PLO_combined = pd.concat(df_PLO[0:len(df_PLO)])

# Convert from wide to long format using melt function in numpy
# for 3 PLO's

if len(df_PLO_combined) < 21:
    df_PLO_selection = df_PLO_combined.iloc[1:, [1,3,6,10,14]]
else:
    df_PLO_selection = df_PLO_combined.iloc[1:, [1,3,6,10,14]]
    df_PLO_selection = df_PLO_selection.drop(0, axis=0)  # only for multiple pages

# rename column headings
df_PLO_selection = df_PLO_selection.rename(columns = {'Unnamed: 0': 'STUDENT ID',
                                                      'Unnamed: 1': 'Student Name',
                                                      'PLO7': 'PLO1',
                                                      'Unnamed: 6': 'PLO3', })

df_PLO_selection = df_PLO_selection.rename(columns = {'Unnamed: 10': 'PLO7', })

# reset PLO index
df_PLO_selection.reset_index(drop=True, inplace=True)


###################################################################
# Merge LE15 and PLO Data                                         #
###################################################################

left = pd.DataFrame(df_PLO_selection)
right = pd.DataFrame(df_le15_selection)

# result = pd.concat([left, right], axis=1)
result = pd.merge(left, right, left_index=True, right_index=True, how="inner")


program = result.groupby('PROGRAMME')

# Sidebar - PROGRAMME selection
sorted_PROGRAMME_unique = sorted( result['PROGRAMME'].unique() )
selected_PROGRAMME = st.sidebar.multiselect('PROGRAMME', sorted_PROGRAMME_unique, sorted_PROGRAMME_unique)

# Filtering data
result_selected_PROGRAMME = result[ (result['PROGRAMME'].isin(selected_PROGRAMME)) ]


###################################################################
# Select PLO's Only                                               #
###################################################################
# for 3 PLO's
df_PLO_only = result.iloc[:, [2,3,4,6]]
df2=pd.melt(df_PLO_only, id_vars=['PROGRAMME'], value_vars=['PLO1','PLO3','PLO7'], var_name='PLO', value_name='Grade')
cat_grade_order = CategoricalDtype(['A+','A','A-','B+','B','B-','C+','C','C-','D+','D','E','F'],
                                  ordered = True)
df2['Grade'] = df2['Grade'].astype(cat_grade_order)

df2_sort = df2.sort_values('Grade')


###################################################################
# Create Plots                                                    #
###################################################################
#st.ylabel('Bilangan Pelajar')
fig = sns.catplot(x = "Grade", hue = "PLO",kind = "count", palette = "pastel", data = df2_sort)


###################################################################
# Create Frequency Tables                                         #
###################################################################


# create frequency table by program and plo's
freq = df2_sort.groupby(["PROGRAMME","PLO","Grade"]).size()

# convert frequency table from long to wide format
freq_wide = df2_sort.groupby(["PROGRAMME","PLO","Grade"]).size().reset_index(name="Bilangan Pelajar")

# group table by program
freq_wide = pd.pivot_table(freq_wide, values='Bilangan Pelajar', index=['PROGRAMME', 'Grade'],
                    columns=['PLO'])

p = df2['PLO'].unique()

if rad == "Home":
    image_jata = st.image("jata.jpg")

    st.write("""
    # Laporan Peperiksaan Akhir

    Data diperolehi dari laporan eRES semester semasa.

    Muatnaik fail yang diperlukan dalam format pdf.

    Nota: Fail pdf PLO dari eRES hendaklah di buang 'header'
    jadual pada setiap page sebelum di muatnaik ke sistem

    """)

    image_PLO = st.image("image_PLO.png")

if rad == "Analysis":
    cb1 = st.checkbox('Show LE15 Data')
    if cb1:
        st.subheader('Raw data')
        st.write("### Senarai Keputusan LE15 Pelajar", df_le15_combined.sort_index())

    n_LE15 = df_le15_combined.shape
    st.write("Dimension is ", n_LE15)


    cb2 = st.checkbox('Show PLO Data')
    if cb2:
        st.subheader('Raw data')
        st.write("### Senarai Keputusan PLO Pelajar", df_PLO_selection.sort_index())

    n_PLO = df_PLO_combined.shape
    st.write("Dimension is ", n_PLO)

    cb3 = st.checkbox('Show Full Data')
    if cb3:
        st.subheader('Raw data')
        st.write("### Senarai Penuh Keputusan PLO Pelajar Dan Program", result.sort_index())

    n_result = result.shape
    st.write("Dimension is ", n_result)

    def filedownload(df):
        csv = result.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="result.csv">Download CSV File</a>'
        return href

    st.markdown(filedownload(result), unsafe_allow_html=True)

    st.header('Display Results in Selected PROGRAMME')
    st.write('Data Dimension: ' + str(result_selected_PROGRAMME.shape[0]) + ' rows and ' + str(result_selected_PROGRAMME.shape[1]) + ' columns.')
    st.dataframe(result_selected_PROGRAMME)

    st.title('Taburan PLO Mengikut Gred')
    st.pyplot(fig)

    st.write("""
    ## Taburan PLO
    """)
    st.write("""
    ## Jadual Bilangan dan Peratus PLO's Mengikut Program
    """)

    def filedownload(freq):
        csv = freq.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="freq_wide.csv">Download CSV File</a>'
        return href
    st.markdown(filedownload(freq), unsafe_allow_html=True)

    ##########################
    ##                      ##
    ## CONVERT TO DATAFRAME ##
    ##                      ##
    ##########################

    for i in p:
        df3_i = pd.DataFrame(freq_wide, columns = [i])
        df3_i['percent'] = round((df3_i[i] / df3_i[i].sum()) * 100, 1)
        st.write(df3_i)


    ####################################
    ##                                ##
    ## SAVING TO EXCEL (.xlsx) FORMAT ##
    ##                                ##
    ####################################

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(r'C:\Users\Public\output.xlsx', engine='xlsxwriter')
    for i in p:
        df3_i.to_excel(writer, sheet_name=i)

    result2 = result.iloc[:, [0,1,2,3,4,6]]
    result2.to_excel(writer, sheet_name='ALL')
    writer.save()
    writer.close()

    st.write('Locate your full report at your Public folder. File Name = output.xlsx')

if rad == "Report":
    st.markdown("""
    # Laporan Pencapaian Keseluruhan Pelajaran

    Bahagian ini menerangkan secara terperinci hasil dapatan dari keputusan pencapaian
    penilaian berterusan dan penilaian akhir pelajar bagi semester semasa. Laporan ini
    disediakan berdasarkan maklumat yang diperolehi dari LE15 dan PLOA sistem eRES.

    ---

    ### Pencapaian Keseluruhan Pelajar

    <-- masukkan maklumat dari fail LE15.pdf -->

    ---

    """)


    left1 = pd.DataFrame(df_PLO_selection)
    right1 = pd.DataFrame(df_le15_combined)

    # result = pd.concat([left, right], axis=1)
    result2 = pd.merge(right1, left1, left_index=True, right_index=True, how="inner")
    result2 = result2.iloc[:, [1,2,4,5,7,8,9,12,13,14]]

    sidebars = {}
    for y in result2.columns:
        if (result2[y].dtype == np.object):
            ucolumns=list(result2[y].unique())
            sidebars[y+"filter"]=st.sidebar.multiselect('Filter '+y, ucolumns)
    st.write(result2)

    st.markdown("""
    ### Pencapaian Pelajar Mengikut PLOA

    <-- masukkan maklumat dari fail PLO.pdf -->

    """)

    st.pyplot(fig)




if rad == "About Us":

    st.write("""
    # Meet The Developer
    """)

    image_dev = st.image("profile.jpeg")

    st.markdown("""
    ## **Kamarul Ariffin Mansor**
    Universiti Teknologi MARA, Kedah Branch Campus

    Kamarul Ariffin Mansor, is a senior lecturer at the Faculty of Computer Science and Mathematics,
    Universiti Teknologi MARA (UiTM), Kedah Branch Campus, Malaysia. His research interest includes
    the application of structural equation modeling and statistical applications in other fields of
    studies, data analytics and visualization using Excel, R, Tableau, etc.

    Visit My Website at https://ariff118.github.io/kamansor.github.io/
    """)
