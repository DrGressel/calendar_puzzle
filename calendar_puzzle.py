import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from random import randint as rnd
import math
import time
import sqlite3
from scipy import ndimage
import streamlit as st
import pandas as pd
from datetime import date

# START MAIN FUNCTION
@st.cache
def solve(day, month):
    start = time.process_time()
    class Shape():
        def __init__(self, s):
            self.s = s

        def rotate(self, i):
            for i in range(i):
                self.s = np.rot90(self.s)

        def flip(self):
            self.s = np.fliplr(self.s)

    def shuffle(S):
        S.rotate(rnd(0, 3))
        if rnd(0, 1) == 1:
            S.flip()

    def place(S, so):
        iter = 0
        while True:
            if iter == 500:
                return 1             
            iter += 1
            P_test = P.copy()
            shuffle(S)
            maxrow = 7 - np.shape(S.s)[0]
            maxcol = 7 - np.shape(S.s)[1]
            row = rnd(0, maxrow)
            col = rnd(0, maxcol)
            P_test[row:row + np.shape(S.s)[0], col:col + np.shape(S.s)[1]] = P_test[row:row + np.shape(S.s)[0], col:col + np.shape(S.s)[1]] + S.s

            if 2 not in P_test:
                labeled_array, num_features = ndimage.label(P_test == 0)
                if len([np.sum(labeled_array == k) for k in range(1, num_features + 1) if np.sum(labeled_array == k) < 5]) == 0:
                    P[0:np.shape(P)[0], 0:np.shape(P)[1]] = P_test
                    ii = 0
                    for i in range(row, row + np.shape(S.s)[0]):
                        jj = 0
                        for j in range(col, col + np.shape(S.s)[1]):
                            if S.s[ii, jj] == 1:
                                P2[i, j] = S.s[ii, jj] + so + 1
                            jj += 1
                        ii += 1
                    return 0

    S = [Shape(np.array([[0, 1],[1, 1],[1, 1]]))]
    S.append(Shape(np.array([[1, 1],[1, 1],[1, 1]])))
    S.append(Shape(np.array([[1 ,1 ,1],[1 ,0 ,0],[1 ,0 ,0]])))
    S.append(Shape(np.array([[0 ,1],[1 ,1],[0 ,1],[0, 1]])))
    S.append(Shape(np.array([[1 ,0],[1 ,1],[0 ,1],[0, 1]])))
    S.append(Shape(np.array([[1 ,0, 0],[1 ,1, 1],[0, 0, 1]])))
    S.append(Shape(np.array([[1 ,1, 1],[1 ,0, 1]])))
    S.append(Shape(np.array([[0, 1],[0, 1],[0, 1],[1, 1]])))

    shapes_to_place = 8
    shape_order = np.arange(0, 8)

    month = [math.floor((month-1)/6), month - 6*math.floor((month-1)/6) - 1]
    day = [math.floor((day-1)/7) + 2, day - 7*math.floor((day-1)/7) - 1]
    s = 0
    versuche = 0

    while s == 0:
        P = np.zeros([7, 7])
        P[0:2, 6] = 1
        P[6, 3:7] = 1
        P[month[0], month[1]] = 1
        P[day[0], day[1]] = 1
        P2 = P.copy()
        versuche += 1
        np.random.shuffle(shape_order)
        for i in range(shapes_to_place):
            e = place(S[shape_order[i]], shape_order[i])
            if e == 1:
                break
            elif i == (shapes_to_place - 1):
                s = 1
                break

    ende = time.process_time()
    
    return P2, versuche, ende-start

# END MAIN FUNCTION
#################################################################################

conn = sqlite3.connect('results.db')
c = conn.cursor()

try:
    c.execute("SELECT * FROM results")
except:
    c.execute("CREATE TABLE results (day integer, month integer, result text)")
    conn.commit()


st.title('Kalender Puzzle')

method = st.selectbox('Bitte auswählen', ('Neue Lösung berechnen', 'Lösung aus Datenbank laden'))
today = date.today()

if method == 'Neue Lösung berechnen':
    with st.form('Puzzle'):

        day = st.slider('Tag wählen', min_value = 1, max_value = 31, value = today.day, step = 1)
        month = st.slider('Monat wählen', min_value = 1, max_value = 12, value = today.month, step = 1)
        
        st.write('*Achtung: Die Berechnung kann bis zu 5 Minuten dauern!*')

        if st.form_submit_button('Jetzt berechnen'):
            RES = solve(day, month)
            st.success('Lösung gefunden nach ' + str(round(RES[2], 2)) + ' Sekunden und ' + str(RES[1]) + ' Iterationen.')
    	    
            P = RES[0].astype(np.int32)            
            
            fig = px.imshow(P-1, color_continuous_scale = px.colors.qualitative.Plotly, height = 600, width = 600)
            fig.update_coloraxes(showscale = False)
            mm = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
            for cnt, m in enumerate(mm):
                fig.add_annotation(x = cnt - math.floor(cnt/6)*6, y = math.floor(cnt/6), text = m, showarrow = False)
            for i in range(1, 32):
                fig.add_annotation(x = i - 1 - math.floor((i - 1)/7)*7, y = math.floor((i-1)/7)+2, text = str(i), showarrow = False)
            fig.update_xaxes(showticklabels = False)
            fig.update_yaxes(showticklabels = False)
            st.plotly_chart(fig)

            e = list(c.execute("SELECT * FROM results WHERE day = ? AND month = ?", (str(day), str(month))))
            sv = False
            for i in range(len(e)):
                P_db = np.frombuffer(e[i][-1], dtype = np.int32).reshape([7, 7])
                if P.all() == P_db.all():
                    sv = True
                    st.write('Die gefundene Lösung ist in der Datenbank bereits vorhanden.')
            
            if sv == False:
                st.write('Neue Lösung gefunden! Die Lösung wurde in der Datenbank gespeichert.')
                c.execute("INSERT INTO results VALUES (?, ?, ?)", (day, month, P.tobytes()))
                conn.commit()            

else:
    day = st.slider('Tag wählen', min_value = 1, max_value = 31, value = today.day, step = 1)
    month = st.slider('Monat wählen', min_value = 1, max_value = 12, value = today.month, step = 1)

    e = list(c.execute("SELECT * FROM results WHERE day = ? AND month = ?", (str(day), str(month))))
    st.subheader(str(len(e)) + ' Lösung(en) gefunden')
    for l in range(len(e)):
        st.write('Lösung ' + str(l+1))
        
        P = np.frombuffer(e[l][-1], dtype = np.int32).reshape([7, 7])

        fig = px.imshow(P-1, color_continuous_scale = px.colors.qualitative.Plotly, height = 600, width = 600)
        fig.update_coloraxes(showscale = False)
        mm = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
        for cnt, m in enumerate(mm):
            fig.add_annotation(x = cnt - math.floor(cnt/6)*6, y = math.floor(cnt/6), text = m, showarrow = False)
        for i in range(1, 32):
            fig.add_annotation(x = i - 1 - math.floor((i - 1)/7)*7, y = math.floor((i-1)/7)+2, text = str(i), showarrow = False)
        fig.update_xaxes(showticklabels = False)
        fig.update_yaxes(showticklabels = False)
        st.plotly_chart(fig)
            


conn.close()
