from logging import NullHandler, debug
from flask import Flask,render_template,request,redirect,url_for, make_response
import sqlite3, os
from werkzeug.utils import secure_filename

app=Flask(__name__)

@app.route('/')
def main():
    return render_template('diarymain.html')


@app.route('/logout')
def logout():

    resp=make_response(render_template('diarymain.html'))
    resp.set_cookie('userID','')
    return resp

@app.route('/gomain')
def gomain():

    
    return render_template('maindiary.html')

@app.route('/login' , methods=['POST','GET'])
def login():
    if request.method=='POST':
        name2=request.form['ID']
        pw=request.form['PASSWORD']
    conn = sqlite3.connect('mydb.db')
    c=conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS student (db_id varchar(50), db_pw varchar(50))")
    pwbox=None
    for row in c.execute('SELECT db_id, db_pw FROM student WHERE student.db_id==?',(name2,)):
        pwbox=row[1]
    if pwbox==None:
        return '아이디 조회 실패! 뒤로가서 다시 시도하세요!'
    
    if pw!=pwbox:
        return '암호오류! 뒤로가서 다시시도하세요!'

    resp=make_response(render_template('maindiary.html'))
    resp.set_cookie('userID',name2)

    return resp

@app.route('/writediary')
def writediary():
    return render_template('writediary.html')

@app.route('/editdiary')
def editdiary():
    diaryname=request.cookies.get('diaryID')
    username=request.cookies.get('userID')
    conn = sqlite3.connect('mydb.db')
    c=conn.cursor()
    for row in c.execute('SELECT * FROM diary WHERE diary.db_id == ? AND diary.db_title==?',(username,diaryname)) : 
        lst=row
    conn.commit()
    conn.close()

    
    return render_template('editdiary.html',lst=lst)

@app.route('/viewdiary/<diaryname>')
def viewdiary(diaryname):
    name=request.cookies.get('userID')
    conn = sqlite3.connect('mydb.db')
    c=conn.cursor()
    for row in c.execute('SELECT * FROM diary WHERE diary.db_id == ? AND diary.db_title==?',(name,diaryname)) : 
        lst=row
    conn.commit()
    conn.close()
    resp=make_response(render_template('viewdiary.html',lst=lst))
    resp.set_cookie('diaryID',row[1])
    
    return resp

@app.route('/viewlist')
def viewlist():
    tex=''
    name=request.cookies.get('userID')
    conn = sqlite3.connect('mydb.db')
    c=conn.cursor()
    n=0
    dl=[]
    for row in c.execute('SELECT * FROM diary WHERE diary.db_id == ? ',(name,)) : 
        dl.append(row)
        n=n+1
    
    conn.commit()
    conn.close()

    

    return render_template('diarylist.html',lst=dl,num=n)
@app.route('/sign')
def sign():
    return render_template('signup.html')


@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method=='POST':
        name2=request.form['ID']
        pw=request.form['PASSWORD']
    conn = sqlite3.connect('mydb.db')

    c=conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS student (db_id varchar(50), db_pw varchar(50))")
    for row in c.execute('SELECT db_id FROM student WHERE student.db_id==?',(name2,)):
        return 'ID 중복입니다! 뒤로가기를 눌러 다시 실행해주세요.'
    c.execute("INSERT INTO student VALUES(?,?)",(name2,pw))
    conn.commit()
    conn.close()
    return '회원가입이 완료되었습니다. 메인으로 돌아가 로그인해주세요.'

@app.route('/editsave', methods=['POST','GET'])
def editsave():
    username=request.cookies.get('userID')
    diaryname=request.cookies.get('diaryID')
    if request.method=='POST':
        title=request.form['Title']
        contents=request.form['Contents']
    conn = sqlite3.connect('mydb.db')

    c=conn.cursor()
    c.execute('UPDATE diary SET db_title=?  WHERE db_id==? AND db_title==?',(title,username,diaryname))
    c.execute('UPDATE diary SET db_content=?  WHERE db_id==? AND db_title==?',(contents,username,title))
    conn.commit()
    conn.close()

    return render_template('savedone.html')

@app.route('/rmdiary', methods=['POST','GET'])
def rmdiary():
    username=request.cookies.get('userID')
    diaryname=request.cookies.get('diaryID')
    if request.method=='POST':
        title=request.form['Title']
        contents=request.form['Contents']
    conn = sqlite3.connect('mydb.db')

    c=conn.cursor()
    c.execute('DELETE FROM diary WHERE db_id==? AND db_title==?',(username,diaryname))
    
    conn.commit()
    conn.close()

    return render_template('rmdone.html')
@app.route('/savediary', methods=['POST','GET'])
def savediary():
    name=request.cookies.get('userID')
    if request.method=='POST':
        title=request.form['Title']
        contents=request.form['Contents']
        f=request.files['upload_file']
        if not os.path.exists("./static"):
            os.makedirs('./static')
        f.save("./static/"+ f.filename)
        
    conn = sqlite3.connect('mydb.db')

    c=conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS diary (db_id varchar(50), db_title varchar(50), db_content varchar(1000) ,img varchar(100) )")
    
    c.execute("INSERT INTO diary VALUES(?,?,?,?)",(name,title,contents,f.filename))
    conn.commit()
    conn.close()
    return render_template('savedone.html')




if __name__ == '__main__':
    app.run(debug = True)