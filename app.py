from flask import Flask,render_template,request
import pickle
import numpy as np

popular_df=pickle.load(open('populardf.pkl','rb'))
pt=pickle.load(open('pt.pkl','rb'))
course=pickle.load(open('course.pkl','rb'))
similarity_score=pickle.load(open('similarity_score.pkl','rb'))
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           pic=list(popular_df['image'].values),
                           course_name=list(popular_df['course name'].values),
                           instr=list(popular_df['instructor'].values),
                           platf=list(popular_df['platform'].values),
                           rate=list(popular_df['rating'].values),
                           sub=list(popular_df['subject'].values),
                           lk=list(popular_df['link'].values),
                           cont=list(popular_df['description'].values))


@app.route('/recommend')
def recommend_ui():
    return render_template('first.html')

@app.route('/recommend_course',methods=['post'])
def recommend2():
    user_in = (request.form.get('user_in') or '').strip().lower()
    # subjects in the dataset may carry stray whitespace (e.g. 'ui ux designing ')
    matches = course[course['subject'].str.strip().str.lower() == user_in][0:10]
    if user_in == '' or matches.empty:
        message = ("SORRY FOR THE INCONVENIENCE, WE WILL UPDATE SOON. "
                   "UNTIL THEN YOU CAN REFER TO OUR TOP 50 COURSES")
        return render_template('first.html', data_list=[], message=message)
    data_list = []
    for _, row in matches.iterrows():
        data_list.append([row['course name'], row['description'], row['image'],
                          row['rating'], row['platform'], row['subject'], row['link']])
    return render_template('first.html', data_list=data_list)

@app.route('/recommended')
def recommend_uix():
    return render_template('recommend.html')

@app.route('/recommend_course_',methods=['post'])
def recommend():
    user_input=(request.form.get('user_input') or '').strip()
    positions = np.where(pt.index.str.lower() == user_input.lower())[0]
    if len(positions) == 0:
        return render_template('recommend.html', data=[],
                               message='Course not found. Please enter the exact course name from the Top 50 list.')
    index = positions[0]
    similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:6]
    data = []
    for i in similar_items:
        item = []
        temp_df = course[course['course name'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('course name')['image'].values))
        item.extend(list(temp_df.drop_duplicates('course name')['course name'].values))
        item.extend(list(temp_df.drop_duplicates('course name')['description'].values))
        item.extend(list(temp_df.drop_duplicates('course name')['platform'].values))
        item.extend(list(temp_df.drop_duplicates('course name')['subject'].values))
        item.extend(list(temp_df.drop_duplicates('course name')['rating'].values))
        item.extend(list(temp_df.drop_duplicates('course name')['link'].values))
        data.append(item)
    return render_template('recommend.html', data=data)

if __name__=='__main__':
    app.run(debug=True)