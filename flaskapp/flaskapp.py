# -*- coding: utf-8 -*-
'''
from importlib import reload
from bson.objectid import ObjectId
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify, send_from_directory
from flask_oauthlib.client import OAuth
from gridfs.errors import NoFile
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
try:
    from pymongo.connection import Connection
except ImportError as e:
    from pymongo import MongoClient as Connection
from pymongo import MongoClient
from urllib.request import Request, urlopen, URLError
from config import Config
from werkzeug import secure_filename


import dateutil.parser
import gridfs, datetime, json, os, jinja2, flask, jsonify
import PyPDF2
import hashlib
import nltk
import operator
import ssl
import sys
'''
from flask import Flask, flash, render_template, request, redirect, url_for, session, make_response, jsonify, send_from_directory
from flask_oauthlib.client import OAuth
from werkzeug import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import Config
from urllib.request import Request, urlopen, URLError
try:
    from pymongo.connection import Connection
except ImportError as e:
    from pymongo import MongoClient as Connection
from importlib import reload
import dateutil.parser
import sys
import nltk
import ssl
import hashlib
import gridfs, datetime, json, os, jinja2, flask
#import jinja2
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
SENT_DETECTOR = nltk.data.load('tokenizers/punkt/english.pickle')
app = Flask(__name__, static_url_path='', static_folder=r'C:\Users\sehoon\Desktop\project\flaskapp\static')
#my_loader = jinja2.ChoiceLoader([
#    app.jinja_loader,
#    jinja2.FileSystemLoader(Config.loader_path),
#])
#app.jinja_loader = my_loader
'''
app.config["MONGO_URI"]="mongodb://localhost:27017/"
mongo=Pymongo(app)

reload(sys)
sys.setdefaultencoding('utf-8')
'''
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
UPLOAD_FOLDER = r'C:\Users\sehoon\Desktop\project\flaskapp\static\upload'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])
'''

my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader(Config.loader_path),
])

app.jinja_loader = my_loader

app.config['GOOGLE_ID'] = Config.google["id"]
app.config['GOOGLE_SECRET'] = Config.google["secret"]
app.config['UPLOAD_FOLDER'] = Config.upload_folder
'''
app.debug = True
app.secret_key = 'development'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
#oauth = OAuth(app)

#ALLOWED_EXTENSIONS = set(['jpg'])

#client = MongoClient()
client = MongoClient('localhost', 27017,connect=False)
db = client["Micture"]
fs = gridfs.GridFS(db)

#app.config['UPLOAD_FOLDER'] = Config.upload_folder
#hash_password = Config.hash_password

@app.route("/") #메인 홈페이지 이동
def home():
    userId = checkUserId()
    if 'userId' in session:
        userName=getUserName()
        return render_template('main.html', userName = userName)
    else :
        return render_template('pages-login.html')

@app.route("/main") #메인 홈페이지 이동
def mainpage():
    userId = checkUserId()
    if 'userId' in session:
        userName=getUserName()
        return render_template('main.html', userName = userName)
    else :
        return render_template('pages-login.html')

@app.route("/pages-login") #로그인 페이지 이동
def mainLogin():
    loginFlag = 3
    return render_template('pages-login.html', loginFlag = loginFlag)

@app.route("/pages-register") #회원 가입 페이지 이동
def mainNewMember():
    return render_template('pages-register.html')

@app.route("/pages-profile") #
def myProfile():
    return render_template('pages-profile.html')

@app.route("/pages-gallery") #내 갤러리로 이동
def myGallery():
    count=0
    userId = checkUserId()
    userName=getUserName()
    collection = db.PhotoInformation
    rows = collection.find({"user_id": userId}).sort("time",-1)
    return render_template('pages-gallery.html', data=rows,userName = userName,count=count)

@app.route("/pages-gallery_detail", methods=['GET', 'POST']) #커뮤니티 글 내용 불러오기 기능 구현
def getWriting():
    id = request.args.get("id")
    collection = db.PhotoInformation
    hit = 0
    userId = checkUserId()
    userName=getUserName()
    data = collection.find_one({"_id": ObjectId(id)})
    hit = data['hits']
    photoUserId=data['user_id']
    collection.update({"_id": ObjectId(id)},{"$set": {"hits":hit+1}})
    data = collection.find_one({"_id": ObjectId(id)})
    if userId==photoUserId :
        return render_template('pages-gallery_detail_my.html',data = data, userName = userName,id=id)
    else :
        return render_template('pages-gallery_detail_other.html',data = data, userName = userName,id=id)


@app.route('/enrollPhoto', methods=['POST']) #논문 등록 버튼 클릭 시 처리 함수
def enrollPhoto():
    if 'userId' in session:
        if request.method == 'POST':
            #latestPhotoNum = db.latestPhotoNum
            collection = db.PhotoInformation
            userId = checkUserId()
            userName = getUserName()
            title = request.form['title']
            content = request.form['content']
            hashtag = request.form['hashtag']
            hits = 0
            version = 1
            complete = 0
            commentNum = 0
            photoNum = "" #최종 논문 등록시 논문 번호
            now = datetime.datetime.now()
            currentTime = str(now.strftime("%Y.%m.%d %H:%M"))
            
            #latestCursor = latestPhotoNum.find_one({"latestfind": "latestfind"})
            #myPhotoNum = int(latestCursor['latestPhotoNum']+1)
            #latestPhotoNum.update({"latestfind": "latestfind"},
            #                      {"latestfind": "latestfind",'latestPhotoNum':myPhotoNum})
            fileName = upload_file()
            doc = {'user_id'     : userId,       
                   'hits'        : hits,         'content'     : content,
                   'version'     : version,      'complete'   : complete,
                   'title'       : title,        'hashtag'    : hashtag,
                   'photoNum'    : photoNum,     #'myPhotoNum' : myPhotoNum,
                   'time'        : currentTime,  'commentNumber' : commentNum,
                   'fileName'    : fileName,     'userName'   : userName
                   }
            collection.insert(doc)
            sessionState = checkSession()
            if sessionState == 0: #일반 유저 로그인인 경우
                userCollection = db.Members
                userInfo = userCollection.find_one({"user_id": userId})
                enrollPhotoNum = userInfo['enrollPhotoNum']
                userCollection.update({"user_id": userId}, {"$set":{"enrollPhotoNum":enrollPhotoNum+1}})
            return mainEnroll()
    else:
        loginFlag = 2   #로그인 정보 없을 때 로그인이 필요하다는 flag전달
        return render_template('pages-login.html', loginFlag=loginFlag)

@app.route("/form-upload") #사진업로드 기능
def upload():
    userId = checkUserId()
    userName=getUserName()
    return render_template('form-upload.html', userName = userName)

def passwordTohash(password):
    hash_object = hashlib.sha256(password.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    return hex_dig

def checkUserId():
    userId = ""
    if 'userId' in session:
        userId = session['userId']
    if userId == "":
        session.pop('userId', None)
        return render_template('pages-login.html')
    return userId

def checkSession():
    if 'userId' in session:
        return 0

def getUserName():
    userId = checkUserId()
    if userId=="":
        return render_template('pages-login.html')
    if 'userId' in session:
        user = db.Members
        userData = user.find_one({"user_id": userId})
        userName = userData['user_name']
    if userName=="":
        session.pop('userId', None)
        return render_template('pages-login.html')
    return userName

@app.route('/pages-logout')
def logout():
    userId = ""
    if 'userId' in session:
        session.pop('userId', None)
    return render_template('pages-login.html', userId = userId)

@app.route("/user-login", methods=['POST'])
def userLogin():
    userId = request.form['email_id']
    password = passwordTohash(request.form['password'])
    collection = db.Members
    cursor = collection.find({"user_id": userId}) #회원등록이 되 있는지 검색
    loginFlag = 0
    for document in cursor:
        if document['user_id'] == userId and document['password'] == password:
            session['userId'] = userId
            userName=document['user_name']
            loginFlag = 1
            break
    if loginFlag == 0:
        flash("Email 혹은 비밀번호가 일치하지 않습니다")
        return render_template('pages-login.html', userId = userId, loginFlag = loginFlag)
    elif loginFlag == 1:
        return render_template('main.html', loginFlag = loginFlag, userName = userName)

@app.route("/enrollNewMember", methods=['POST']) #일반회원 가입 기능 구현
def enrollNewMember():
    
    app.config['MONGO_CONNECT'] = False
    if request.method == 'POST':
        userName=request.form['name']
        userId = request.form['email_id']
        newPassWord = passwordTohash(request.form['new_password'])
        newPassWordCheck = passwordTohash(request.form['new_password_check'])
        fame = 0
        subPaperNum = 0
        enrollPhotoNum = 0
        tokenNum = 0
        doc = {'user_id'    : userId,   'user_name'     : userName, 'password':newPassWord,
                'fame'    : fame,       'subPaperNum': subPaperNum, 'enrollPhotoNum': enrollPhotoNum, 
                'tokenNum': tokenNum,   'state' : 0,                'journal_number':0,
	           'obId'       : ""}
        collection = db.Members
        cursor = collection.find({"user_id": userId})
        enrollFlag = 0
        
        for document in cursor:                   #회원 등록 확인
            if document['user_id'] == userId:
                enrollFlag = 1
                flash('이미 가입된 Email 입니다!')
                return render_template('pages-register.html', enrollFlag=enrollFlag)
        collection.insert(doc)                   #아이디 검사 완료시 회원정보 데이터베이스 삽입
        return render_template("pages-waitView.html")
    else:
        return "잘못된 데이터 요청 입니다."

@app.route("/deletePhoto", methods=['GET', 'POST'])
def deletePhoto():
    id = request.args.get("id")
    
    photoCollection = db.PhotoInformation
    userCollection = db.Members
    photoInfo = photoCollection.find_one({"_id": ObjectId(id)})
    filename=photoInfo['fileName']
    userId = photoInfo['user_id']
    userInfo=userCollection.find_one({"user_id": userId})
    enrollPhotoNum= userInfo['enrollPhotoNum']
    photoCollection.remove({"_id": ObjectId(id)})
    userCollection.update({"user_id": userId}, {"$set":{"enrollPhotoNum":enrollPhotoNum-1}})
    return delete_file(filename)
    
def delete_file(filename):
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    flash('사진이 삭제되었습니다')
    return mainEnroll()

@app.route("/main_enroll")
def mainEnroll():
    userId=checkUserId()
    collection = db.PhotoInformation
    rows = collection.find({"user_id": userId}).sort("time",-1)
    userName = getUserName()
    return render_template('pages-gallery.html', data=rows, userName=userName)

@app.route("/pages-token")
def tokenExchange():
    userId=checkUserId()
    userName = getUserName()
    return render_template('pages-token.html', userName=userName)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('선택된 사진이 없습니다.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            flash('사진이 성공적으로 등록되었습니다.')
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return str(filename)

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
@app.route("/photo_upload") #글쓰기 버튼 클릭시 로그인 검사 및 글쓰기 페이지 이동
def mainComunityWrite():
    userId = checkUserId()
    if 'userId' in session:
        return render_template('form-upload.html', userId = userId)
    else:
        loginFlag = 2   #로그인 정보 없을 때 로그인이 필요하다는 flag전달
        return render_template('paegs-login.html', loginFlag=loginFlag)

@app.route("/searchWord", methods=['POST'])
def searchWord():
    photoCollection = db.PhotoInformation
    querySentence = request.form['querySentence'].lower()
    querySentence = querySentence.encode('utf-8').strip()
    querySentenceList = querySentence.split(b" ")
    tempList = []
    photoCursor = None
    photoCursor = photoCollection.find({"complete":0})

    for photo in photoCursor:
        photoTitle = photo['title']
        real_sentences = nltkExtract(photoTitle)
        temp = " "+real_sentences.lower()+" "
        count = 0
        for queryWord in querySentenceList:
            queryWord=queryWord.decode('utf-8')
            if temp.find(queryWord) != -1:
                start = temp.find(queryWord)
                last = start + len(queryWord)
                if temp[start-1] != " " or temp[last] != " ":
                    continue
                count += 1
        if count != 0:
            photo['search_count'] = count
            photo['enroll_date'] = dateutil.parser.parse(photo['time'])
            tempList.append(photo)
    resultList = sorted(tempList, key=compSearch, reverse=True)
    return render_template('pages-gallery.html', data = resultList)

def nltkExtract(sentence):
    sentence = sentence.encode('utf-8').strip()
    sentence = sentence.decode('utf-8')
    sentences = nltk.sent_tokenize(sentence)
    real_sentences = ""
    for i in sentences:
        for word,pos in nltk.pos_tag(nltk.word_tokenize(str(i))):
            if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS'
                or pos == 'VB' or pos == 'VBD' or pos == 'VBG' or pos == 'VBN'
                or pos == 'VBP' or pos == 'VBZ' or pos == 'CD'):
                real_sentences = real_sentences + " " + word
    return real_sentences

def compSearch(elem):
    return elem['search_count'], elem['enroll_date']

@app.route('/js/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.getcwd())
    print(root_dir)
    return send_from_directory(os.path.join(root_dir ,'flaskapp','static', 'js'), filename)
'''
@app.route("/getState")
def getState():
    return str(session['state'])



@app.route("/main_token_buy_page")
def moveTokenBuy():
    userId = checkUserId()
    return render_template('main_token_buy_page.html', userId = userId)

@app.route("/blockEnrollUpdate")
def blockEnrollUpdate():
    userId = checkUserId()
    userCollection = db.Users
    user = userCollection.find_one({"user_id":userId})
    journalNumber = user['journal_number']
    obId = user['obId']
    paperCollection = db.PaperInformation
    paperCollection.update({"_id":ObjectId(obId)}, {"$set": {"complete": 1, "paperNum": journalNumber}})
    userCollection.update({"user_id":userId}, {"$set":{"obId":"0", "journal_number":"0", "state": 0}})
    paperNumInfo = db.PaperNum
    paper = paperNumInfo.find_one({"name":"latestNum"})
    paperNumInfo.update({"name":"latestNum"}, {"$set": {"updatedPaperNum":paper['updatedPaperNum']+1}})
    return mainEnroll()

@app.route("/blockSubscribeUpdate")
def blockSubscribeUpdate():
    userId = checkUserId()
    userCollection = db.Users
    user = userCollection.find_one({"user_id":userId})
    journalNumber = user['journal_number']
    obId = user['obId']
    paperCollection = db.PaperInformation
    paperCollection.update({"_id": ObjectId(obId)},{"$push": {"subscribeArray":userId}})
    userCollection.update({"user_id":userId}, {"$set":{"obId":"0", "journal_number":"0", "state": 0, "subPaperNum":user['subPaperNum']+1}})
    return moveToSubPaper()

@app.route("/enrollState")
def enrollState():
    userId = checkUserId()
    data = request.args.get("data")
    data_list = data.split(',')  # 1st: obId, 2nd : state, 3rd : journalNumber
    userCollection = db.Users
    userCollection.update({"user_id":userId}, {"$set":{"state":int(data_list[1]), "obId":data_list[0], "journal_number":data_list[2]}})
    collection = db.PaperInformation
    rows = collection.find({"complete": 0}).sort("writingPaperNum",-1)
    return render_template('main_enroll.html', result =rows, userId=userId)

@app.route("/subscribeState")
def subscribeState():
    userId = checkUserId()
    data   = request.args.get("data")
    data_list = data.split(',')   # 1st: obId, 2nd : state, 3rd : journalNumber
    #data_list[0].encode('utf-8')
    userCollection = db.Users
    #return str(data_list[0])
    userCollection.update({"user_id":str(userId)}, {"$set":{"state":int(data_list[1]), "obId":data_list[0], "journal_number":data_list[2]}})
    #return "2"
    collection = db.PaperInformation
    rows = collection.find({"complete": 1}).sort("writingPaperNum",-1)
    return render_template('main_view_fix_journal.html', result =rows, userId=userId)
def checkTime(month):   #월이 바뀌는 경우를 판단해주는 함수
    paperNumInfo = db.PaperNum
    data = paperNumInfo.find_one({"name": "latestNum"})
    storedMonth = data['month']
    if(storedMonth != month): #월이 다른 경우
        return 0
    else:
        return 1 #월이 같은 경우 1 리턴

@app.route("/papernum")
def papernum():                      #논문 번호 생성
    paperNumInfo = db.PaperNum
    now   = datetime.datetime.now()
    year  = str(now.strftime("%Y"))
    month = str(now.strftime("%m"))
    flag  = checkTime(month)
    paper = paperNumInfo.find_one({"name":"latestNum"})
    createdPaperNum = 0
    if(flag == 1):
        if(paper['updatedPaperNum']>=0 and paper['updatedPaperNum']<=8):
            createdPaperNum = year+month+"000"+str(int(paper['updatedPaperNum']+1))
        elif(paper['updatedPaperNum']>=9 and paper['updatedPaperNum']<=98):
            createdPaperNum = year+month+"00"+str(int(paper['updatedPaperNum']+1))
        elif(paper['updatedPaperNum']>=99 and paper['updatedPaperNum']<=998):
            createdPaperNum = year+month+"0"+str(int(paper['updatedPaperNum']+1))
        elif(paper['updatedPaperNum']>=999 and paper['updatedPaperNum']<=9998):
            createdPaperNum = year+month+str(int(paper['updatedPaperNum']+1))
    elif(flag == 0):
        paperNumInfo.update({"name":"latestNum"}, {"$set": {"year":year,"month":month,"updatedPaperNum":0}})
        createdPaperNum = year+month+"000"+"1"
    return createdPaperNum

@app.route("/main_view_fix_journal")
def moveToSubPaper():
    userId = checkUserId()
    completePaperCollection = db.PaperInformation
    result = completePaperCollection.find({"complete":1}).sort("time", -1)
    return render_template('main_view_fix_journal.html', result = result, userId=userId)
@app.route("/main_enroll_for_check_journal")
def mainEnrollForCheckJournal():
    userId = checkUserId()
    if userId == "":
        loginFlag = 2
        return render_template('main_login.html', loginFlag=loginFlag)
    else:
        return render_template('main_enroll_for_check_journal.html', userId = userId)

@app.route('/enrollPaperComment', methods=['POST'])
def enrollPaperComment():
    if 'google_token' in session or 'userId' in session:
        if request.method == 'POST':
            paperInfo = db.PaperInformation
            userId = checkUserId()
            userName = getUserName()
            now = datetime.datetime.now()
            currentTime = str(now.strftime("%Y.%m.%d %H:%M"))
            commentContent = request.form['comment']
            objectId = request.form['objectId']
            data = paperInfo.find({"_id": ObjectId(objectId)})
            commentNum = 0
            adaptFlag = 0
            for document in data:
                if document['_id'] == ObjectId(objectId):
                    commentNum = document['commentNumber']
            commentDict = {'commentNum':commentNum+1, 'userId':userId,'userName':userName, 'Time':currentTime,
                           'comment':commentContent, 'adaptFlag': adaptFlag}
            paperInfo.update({"_id": ObjectId(objectId)},{"$push": {"commentDicts":commentDict}})
            paperInfo.update({"_id": ObjectId(objectId)},{"$set": {"commentNumber":commentNum+1}})
            data = paperInfo.find({"_id": ObjectId(objectId)})
            data2 = paperInfo.find_one({"_id": ObjectId(objectId)})
            enrollUserId = data2['user_id']
            complete = data2['complete']

            paperReferenceDic, paperContributorDic = extractPDF(objectId)

            state = checkSession()
            if state == 0:
                userCollection = db.Users
                userInfo = userCollection.find_one({"user_id":userId})
                userCollection.update({"user_id":userId}, {"$set": {"fame": userInfo['fame']+1}})
            elif state == 1:
                oauthCollection = db.Oauth_Users
                oauthUserInfo = oauthCollection.find_one({"user_id":userId})
                oauthCollection.update({"user_id":userId}, {"$set": {"fame": oauthUserInfo['fame']+1}})

            return render_template('main_view_journal.html',data = data, userId = userId, enrollUserId = enrollUserId,
                                    complete = complete, paperReferenceDic = paperReferenceDic, paperContributorDic = paperContributorDic)

        else:
            return "잘못된 데이터 요청 입니다."
    else:
        loginFlag = 2   #로그인 정보 없을 때 로그인이 필요하다는 flag전달
        return render_template('main_login.html', loginFlag=loginFlag)

def extractPDF(obId):
    paperInfo = db.PaperInformation
    paper = paperInfo.find_one({"_id":ObjectId(obId)})
    filepath = app.config['UPLOAD_FOLDER'] + paper['fileName']
    pdf_page = page_number_of_pdf(filepath)
    text = convert_pdf_to_txt(str(filepath), [pdf_page-3, pdf_page-2, pdf_page-1])
    contributor_number_list, contributor_name_list = extract_contributors_from_text(text)
    reference_number_list, reference_title_list = extract_reference_from_text(text)

    reference_dic = {
    reference_number_list : reference_title_list for reference_number_list, reference_title_list in zip(reference_number_list, reference_title_list)
    }

    contributor_dic = {
    contributor_number_list : contributor_name_list for contributor_number_list, contributor_name_list in zip(contributor_number_list, contributor_name_list)
    }

    return reference_dic, contributor_dic

@app.route("/main_view_journal", methods=['GET', 'POST'])
def viewPaper():
    id = request.args.get("id") #현재 보려고 하는 논문의 ObjectId 값 get
    userId = checkUserId()
    paperInfo = db.PaperInformation
    data = paperInfo.find({"_id": ObjectId(id)})
    data2 = paperInfo.find_one({"_id": ObjectId(id)})
    enrollUserId = data2['user_id']
    completeJournalNum = data2['paperNum']
    complete = int(data2['complete'])
    writer = data2['user_id']
    paperReferenceDic, paperContributorDic = extractPDF(id) #reference, contributor 추출

    journalNum = papernum()
    hit = data2['hits']
    paperInfo.update({"_id": ObjectId(id)},{"$set": {"hits":hit+1}})
    subFlag = 0
    subInfo = None
    subInfo = paperInfo.find_one({"_id":ObjectId(id), "subscribeArray":userId})
    if subInfo != None:
        subFlag = 1
    return render_template('main_view_journal.html', id = id , data = data, userId = userId, enrollUserId = enrollUserId, complete = complete,
                           paperReferenceDic = paperReferenceDic, journalNum = journalNum, paperContributorDic = paperContributorDic, completeJournalNum = completeJournalNum,
                           subFlag = subFlag, writer = writer)

@app.route("/main_view_reference_journal", methods=['GET', 'POST'])
def movoTorefenrenceJournal():
    journalNum = request.args.get("journalNum")
    return viewReferencePaper(str(journalNum))

def viewReferencePaper(journalNum):
    userId = checkUserId()
    paperInfo = db.PaperInformation
    obPaper = paperInfo.find_one({"paperNum":str(journalNum)}) #논문 번호를 이용하여, paper를 찾아줌
    id = obPaper['_id']
    data = paperInfo.find({"_id": ObjectId(id)})
    data2 = paperInfo.find_one({"_id": ObjectId(id)})
    enrollUserId = data2['user_id']
    completeJournalNum = data2['paperNum']
    complete = int(data2['complete'])
    writer = data2['user_id']
    paperReferenceDic, paperContributorDic = extractPDF(id)
    journalNum = papernum()
    hit = data2['hits']
    paperInfo.update({"_id": ObjectId(id)},{"$set": {"hits":hit+1}})
    subFlag = 0
    subInfo = None
    subInfo = paperInfo.find_one({"_id":ObjectId(id), "subscribeArray":userId})
    if subInfo != None:
        subFlag = 1
    return render_template('main_view_journal.html', id = id , data = data, userId = userId, enrollUserId = enrollUserId, complete = complete,
                           paperReferenceDic = paperReferenceDic, journalNum = journalNum, paperContributorDic = paperContributorDic, completeJournalNum = completeJournalNum,
                           subFlag = subFlag, writer = writer)

@app.route("/move_paper_update", methods=['GET', 'POST'])
def moveUpdatePaper():
    id = request.args.get("id")
    paperInfo = db.PaperInformation
    userId = checkUserId()
    data = paperInfo.find({"_id": ObjectId(id)})
    return render_template('main_journal_update.html', data = data, userId = userId)

@app.route("/version_update", methods=['GET', 'POST'])
def versionUpdate():
    if 'google_token' in session or 'userId' in session:
        if request.method == 'POST':
            userId = checkUserId()
            collection = db.PaperInformation
            writer = request.form['writerName']
            mainCategory = request.form['mainCat']
            subCategory = request.form['subCat']
            title = request.form['title']
            abstract = request.form['abstract']
            keyword = request.form['keyword']
            version = 1
            now = datetime.datetime.now()
            currentTime = str(now.strftime("%Y.%m.%d %H:%M"))
            id = request.form['objectId']
            data = collection.find_one({"_id": ObjectId(id)})
            version = data['version']
            fileName = upload_file()
            collection.update({"_id": ObjectId(id)}, {"$set": {"writer":writer, "mainCategory":mainCategory, "subCategory":subCategory,
                              "title":title, "abstract":abstract, "keyword": keyword, "version": version+1, "time": currentTime,
                              "fileName": fileName}})
            return mainEnroll()
    else:
        loginFlag = 2   #로그인 정보 없을 때 로그인이 필요하다는 flag전달
        return render_template('main_login.html', loginFlag=loginFlag)

def viewPaperafterAdapt(obId):
    id = obId
    userId = checkUserId()
    paperInfo = db.PaperInformation
    data = paperInfo.find({"_id": ObjectId(id)})
    data2 = paperInfo.find_one({"_id": ObjectId(id)})
    enrollUserId = data2['user_id']
    completeJournalNum = data2['paperNum']
    complete = int(data2['complete'])
    writer = data2['user_id']
    paperReferenceDic, paperContributorDic = extractPDF(id)
    journalNum = papernum()
    hit = data2['hits']
    paperInfo.update({"_id": ObjectId(id)},{"$set": {"hits":hit+1}})
    subFlag = 0
    subInfo = None
    subInfo = paperInfo.find_one({"_id":ObjectId(id), "subscribeArray":userId})
    if subInfo != None:
        subFlag = 1
    return render_template('main_view_journal.html', id = id , data = data, userId = userId, enrollUserId = enrollUserId, complete = complete,
                           paperReferenceDic = paperReferenceDic, journalNum = journalNum, paperContributorDic = paperContributorDic, completeJournalNum = completeJournalNum,
                           subFlag = subFlag, writer = writer)

@app.route("/adaptPaperComment") #댓글 채택시 명성 부여
def adaptPaperComment():
    data = request.args.get("data")
    list = data.split(',') # 0번째 댓글번호, 1번째 문서객체아이디, 2번째 댓글 작성자 아이디, 3번째 채택flag, 4번째 글 작성자 아이디
    id = list[1]
    paperCollection = db.PaperInformation
    userCollection = db.Users
    userId = checkUserId()
    cursor = userCollection.find({"user_id": list[2]}) #일반 유저인 경우
    for document in cursor:
        if document['user_id'] == list[2]:
            userCollection.update({"user_id":document['user_id']}, {"$set": {"fame": document['fame']+5}})
            paper = paperCollection.find_one({'_id': ObjectId(list[1])})
	    commentN = list[0]
            paperCollection.update({"_id": ObjectId(list[1]), "commentDicts.commentNum": int(commentN)},
            {"$set": {"commentDicts.$.adaptFlag": 1}}, True)
            data = paperCollection.find({"_id": ObjectId(list[1])})
            return viewPaperafterAdapt(id)
    oauthUserCollection = db.Oauth_Users
    oauthCursor = oauthUserCollection.find({"user_id": list[2]}) #구글 유저인 경우
    for doc in oauthCursor:
        if doc['user_id'] == list[2]:
            oauthUserCollection.update({"user_id":doc['user_id']}, {"$set": {"fame": doc['fame']+5}})
            writingPaper = writingCollection.find_one({'_id': ObjectId(list[1])})
            commentN = list[0]
            writingCollection.update({"_id": ObjectId(list[1]), "commentDicts.commentNum": int(commentN)},
            {"$set": {"commentDicts.$.adaptFlag": 1}}, True)
            data = writingCollection.find({"_id": ObjectId(list[1])})
            return viewPaperafterAdapt(id)

    loginFlag = 2   #로그인 정보 없을 때 로그인이 필요하다는 flag전달
    return render_template('main_login.html', loginFlag=loginFlag)
'''

'''


@app.route("/main_comunity_detail", methods=['GET', 'POST']) #커뮤니티 글 내용 불러오기 기능 구현
def getWriting():
    id = request.args.get("id")
    bulletin = db.Bulletin
    hit = 0
    userId = checkUserId()
    data = bulletin.find({"_id": ObjectId(id)})
    for document in data:
        if document['_id'] == ObjectId(id):
            hit = document['hits']
    bulletin.update({"_id": ObjectId(id)},{"$set": {"hits":hit+1}})
    data = bulletin.find({"_id": ObjectId(id)})
    oneData = bulletin.find_one({"_id":ObjectId(id)})
    writer = oneData['userId']
    return render_template('main_comunity_detail.html',data = data, userId = userId, writer = writer)

@app.route("/deleteCommunityWriting", methods=['GET', 'POST'])
def deleteCommunityWriting():
    id = request.args.get("id")
    bulletin = db.Bulletin
    bulletin.remove({"_id": ObjectId(id)})
    return mainComunity()

@app.route('/commentEnroll', methods=['POST']) #댓글기능 구현
def commentEnroll():
    if 'google_token' in session or 'userId' in session:
        if request.method == 'POST':
            bulletin = db.Bulletin
            userId = checkUserId()
            userName = getUserName()
            now = datetime.datetime.now()
            currentTime = str(now.strftime("%Y.%m.%d %H:%M"))
            commentContent = request.form['comment']
            objectId = request.form['objectId']
            data = bulletin.find({"_id": ObjectId(objectId)})
            commentNum = 0
            adaptFlag = 0
            for document in data:
                if document['_id'] == ObjectId(objectId):
                    commentNum = document['commentNumber']
            commentDict = {'commentNum':commentNum+1, 'userId':userId,'userName':userName, 'Time':currentTime,
            'comment':commentContent, 'adaptFlag': adaptFlag}
            bulletin.update({"_id": ObjectId(objectId)},{"$push": {"commentDicts":commentDict}})
            bulletin.update({"_id": ObjectId(objectId)},{"$set": {"commentNumber":commentNum+1}})
            data = bulletin.find({"_id": ObjectId(objectId)})


            state = checkSession()
            if state == 0:
                userCollection = db.Users
                userInfo = userCollection.find_one({"user_id":userId})
                userCollection.update({"user_id":userId}, {"$set": {"fame": userInfo['fame']+1}})
            elif state == 1:
                oauthCollection = db.Oauth_Users
                oauthUserInfo = oauthCollection.find_one({"user_id":userId})
                oauthCollection.update({"user_id":userId}, {"$set": {"fame": oauthUserInfo['fame']+1}})

            return render_template('main_comunity_detail.html',data = data, userId = userId)
        else:
            return "잘못된 데이터 요청 입니다."
    else:
        loginFlag = 2   #로그인 정보 없을 때 로그인이 필요하다는 flag전달
        return render_template('main_login.html', loginFlag=loginFlag)

@app.route("/adaptComment") #댓글 채택시 명성 부여
def adaptComment():
    data = request.args.get("data")
    list = data.split(',') # 0번째 댓글번호, 1번째 문서객체아이디, 2번째 댓글 작성자 아이디, 3번째 채택flag, 4번째 글 작성자 아이디
    writingCollection = db.Bulletin

    userId = checkUserId()

    if 'google_token' in session or 'userId' in session:
        userCollection = db.Users
        cursor = userCollection.find({"user_id": list[2]}) #댓글 작성자가 일반 유저인 경우 탐색
        for document in cursor:
            if document['user_id'] == list[2]:
                userCollection.update({"user_id":document['user_id']}, {"$set": {"fame": document['fame']+5}})
                writingPaper = writingCollection.find_one({'_id': ObjectId(list[1])})
                commentN = list[0]
                writingCollection.update({"_id": ObjectId(list[1]), "commentDicts.commentNum": int(commentN)},
                                     {"$set": {"commentDicts.$.adaptFlag": 1}}, True)
            data = writingCollection.find({"_id": ObjectId(list[1])})
            return render_template('main_comunity_detail.html',data = data, userId = userId)

        oauthUserCollection = db.Oauth_Users
        oauthCursor = oauthUserCollection.find({"user_id": list[2]})  #댓글 작성자가 구글 유저인 경우 탐색
        for doc in oauthCursor:
            if doc['user_id'] == list[2]:
                oauthUserCollection.update({"user_id":doc['user_id']}, {"$set": {"fame": doc['fame']+5}})
                writingPaper = writingCollection.find_one({'_id': ObjectId(list[1])})
                commentN = list[0]
                writingCollection.update({"_id":    ObjectId(list[1]), "commentDicts.commentNum": int(commentN)},
                                         {"$set": {"commentDicts.$.adaptFlag": 1}}, True)
                data = writingCollection.find({"_id": ObjectId(list[1])})
                return render_template('main_comunity_detail.html',data = data, userId = userId)
    else:
        loginFlag = 2   #로그인 정보 없을 때 로그인이 필요하다는 flag전달
        return render_template('main_login.html', loginFlag=loginFlag)

@app.route("/checkMyState", methods = ['POST'])
def checkMyState():
    userId = request.form['userId']
    user_id = str(userId.encode('utf-8'))
    user_id = user_id[1:len(user_id)-1]
    userCollection = db.Users
    user = userCollection.find_one({"user_id":user_id})
    journal_number = user['journal_number']
    dic = {'check_state': user['state'], 'journal_number':journal_number}
    return json.dumps(dic)

def page_number_of_pdf(path):
    pdfFileObj = open(path, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    return pdfReader.numPages

def convert_pdf_to_txt(path, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = file(path, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text

def extract_contributors_from_text(text):
    start = text.find("CONTRIBUTORS:")
    contributor_text = " ".join(text[start:].split("\n"))

    contributor_list = contributor_text.split("[")
    contributor_number_list = []
    contributor_name_list = []

    for contributor in contributor_list:
        is_valid = contributor.find("]")
        try:
            int(contributor[:is_valid])
        except:
            continue

        contributor = contributor[is_valid+1:]
        contributor_detail_list = contributor.split(",")
        is_openjournal_number = contributor_detail_list[0].strip()

        try:
            contributor_number_list.append(int(is_openjournal_number))
        except:
            continue

        contributor_name = contributor_detail_list[1].strip()
        contributor_name_list.append(contributor_name)

    return contributor_number_list, contributor_name_list

def extract_reference_from_text(text):
    start = text.find("REFERENCES:")
    last = text.find("CONTRIBUTORS:")
    reference_text = " ".join(text[start:last].split("\n"))

    reference_list = reference_text.split("[")
    reference_number_list = []
    reference_title_list = []

    for reference in reference_list:
        is_valid = reference.find("]")
        try:
            int(reference[:is_valid])
        except:
            continue

        reference = reference[is_valid+1:]
        reference_detail_list = reference.split(",")
        is_openjournal_number = reference_detail_list[0].strip()

        try:
            reference_number_list.append(int(is_openjournal_number))
        except:
            continue

        start_title = reference.find("“")
        end_title = reference.find("”")

        reference_title = reference[start_title+3:end_title].strip()
        reference_title_length = len(reference_title)

        if reference_title[reference_title_length-1] == ",":
            reference_title = reference_title[0:reference_title_length-1]
        reference_title_list.append(reference_title)

    return reference_number_list, reference_title_list

@app.route("/searchWord", methods=['POST'])
def searchWord():
    paperCollection = db.PaperInformation
    mainCategory = request.form['mainCat']
    subCategory = request.form['subCat']
    querySentence = request.form['querySentence'].lower()
    querySentence = querySentence.encode('utf-8').strip()
    querySentenceList = querySentence.split(" ")
    tempList = []
    paperCursor = None
    if mainCategory != "total":
    	if subCategory != "전체":
    	    paperCursor = paperCollection.find({"mainCategory":mainCategory, "subCategory":subCategory, "complete":0})
    	elif subCategory == "전체":
    	    paperCursor = paperCollection.find({"mainCategory":mainCategory, "complete":0})
    else:
        paperCursor = paperCollection.find({"complete":0})

    for paper in paperCursor:
        paperTitle = paper['title']
        real_sentences = nltkExtract(paperTitle)
        temp = " "+real_sentences.lower()+" "
        count = 0
        for queryWord in querySentenceList:
            if temp.find(queryWord) != -1:
                start = temp.find(queryWord)
                last = start + len(queryWord)
                if temp[start-1] != " " or temp[last] != " ":
                    continue
                count += 1
        if count != 0:
            paper['search_count'] = count
            paper['enroll_date'] = dateutil.parser.parse(paper['time'])
            tempList.append(paper)
    resultList = sorted(tempList, key=compSearch, reverse=True)
    return render_template('main_enroll.html', result = resultList)

@app.route("/searchCompleteWord", methods=['POST'])
def searchCompleteWord():
    paperCollection = db.PaperInformation
    mainCategory = request.form['mainCat']
    subCategory = request.form['subCat']
    querySentence = request.form['querySentence'].lower()
    querySentence = querySentence.encode('utf-8').strip()
    querySentenceList = querySentence.split(" ")
    tempList = []
    paperCursor = None
    if mainCategory != "total":
        print("mainCategory: "+ mainCategory)
    	if subCategory != "전체":
    	    paperCursor = paperCollection.find({"mainCategory":mainCategory, "subCategory":subCategory, "complete":1})
    	elif subCategory == "전체":
    	    paperCursor = paperCollection.find({"mainCategory":mainCategory, "complete":1})
    else:
        paperCursor = paperCollection.find({"complete":1})

    for paper in paperCursor:
        paperTitle = paper['title']
        real_sentences = nltkExtract(paperTitle)
        temp = " "+real_sentences.lower()+" "
        count = 0
        for queryWord in querySentenceList:
            if temp.find(queryWord) != -1:
                start = temp.find(queryWord)
                last = start + len(queryWord)
                if temp[start-1] != " " or temp[last] != " ":
                    continue
                count += 1
        if count != 0:
            paper['search_count'] = count
            paper['enroll_date'] = dateutil.parser.parse(paper['time'])
            tempList.append(paper)
    resultList = sorted(tempList, key=compSearch, reverse=True)
    return render_template('main_view_fix_journal.html', result = resultList)

def nltkExtract(sentence):
    sentence = sentence.encode('utf-8').strip()
    sentences = nltk.sent_tokenize(sentence)
    real_sentences = ""
    for i in sentences:
        for word,pos in nltk.pos_tag(nltk.word_tokenize(str(i))):
            if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS'
                or pos == 'VB' or pos == 'VBD' or pos == 'VBG' or pos == 'VBN'
                or pos == 'VBP' or pos == 'VBZ' or pos == 'CD'):
                real_sentences = real_sentences + " " + word
    return real_sentences

def compSearch(elem):
    return elem['search_count'], elem['enroll_date']
'''
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
