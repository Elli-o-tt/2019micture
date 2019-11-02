from flask import Flask, flash, render_template, request, redirect, url_for, session, make_response, jsonify, send_from_directory
from flask_oauthlib.client import OAuth
from werkzeug import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import Config
from PIL import Image
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
import bitarray
import base64
import ipfshttpclient

#import jinja2
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#SENT_DETECTOR = nltk.data.load('tokenizers/punkt/english.pickle')
app = Flask(__name__, static_url_path='', static_folder=r'C:\Users\sehoon\Desktop\project\blockchainsns\static')

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
UPLOAD_FOLDER = r'C:\Users\sehoon\Desktop\project\blockchainsns\static\upload'
TEMP_FOLDER = r'C:\Users\sehoon\Desktop\project\blockchainsns\static\temp'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif','PNG','PDF','JPG','JPEG','GIF','bmp','BMP'])

app.debug = True
app.secret_key = 'development'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

client = MongoClient('localhost', 27017,connect=False)
db = client["Micture"]
fs = gridfs.GridFS(db)

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

@app.route("/pages-profile") #프로필
def myProfile():
    userID = checkUserId()
    userName=getUserName()
    return render_template('pages-profile.html',userName = userName, userID = userID)

@app.route("/pages-gallery") #내 갤러리로 이동
def myGallery():
    count=0
    userId = checkUserId()
    userName=getUserName()
    collection = db.PhotoInformation
    rows = collection.find({"user_id": userId}).sort("time",-1)
    return render_template('pages-gallery.html', data=rows,userName = userName,count=count)

@app.route("/form-search") #구글 이미지 검색
def searchImage():
    userId = checkUserId()
    userName=getUserName()

    return render_template('form-search.html')


@app.route("/pages-gallery_detail", methods=['GET', 'POST']) #사진 불러오기 기능 구현
def getWriting():
    id = request.args.get("id")
    collection = db.PhotoInformation
    hit = 0
    userId = checkUserId()
    userName=getUserName()
    data = collection.find_one({"_id": ObjectId(id)})
    hit = data['hits']
    photoUserId=data['user_id']
    collection.update_one({"_id": ObjectId(id)},{"$set": {"hits":hit+1}})
    data = collection.find_one({"_id": ObjectId(id)})

    likeFlag=0
    likes=data['likes']

    if likes>0:
        likeDictionary=data['likeDicts']

        for i in likeDictionary:
            if i.get('user_id') == userId:
                count=1
    
        if count==1:
            likeFlag=1

    if userId==photoUserId :
        return render_template('pages-gallery_detail_my.html',data = data, userName = userName,id=id)
    else :
        return render_template('pages-gallery_detail_other.html',data = data, userName = userName,id=id,userid=userId,likeFlag=likeFlag)

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

@app.route('/likePhoto', methods=['POST']) 
def like():
    userId = checkUserId()
    userName=getUserName()


    collection = db.PhotoInformation
    memCollection = db.Members


    now = datetime.datetime.now()
    currentTime = str(now.strftime("%Y.%m.%d %H:%M"))

    objectId = request.form['objectId']
    data = collection.find_one({"_id": ObjectId(objectId)})
    photoUserId=data['user_id']

    likes=data['likes']

    if likes==0:
        likeDict = {'user_id':userId}
        collection.update({"_id": ObjectId(objectId)},{"$push": {"likeDicts":likeDict}})
        collection.update({"_id": ObjectId(objectId)},{"$set": {"likes":likes+1}})

        likeDict = {'photo_id':ObjectId(objectId),'Time':currentTime}
        memCollection.update({"user_id": userId},{"$push": {"likeDicts":likeDict}})
    
    else:
        likeDictionary=data['likeDicts']
        count=0
        for i in likeDictionary:
            if i.get('user_id') == userId:
                count=1
    
        if count==1:
            collection.update({"_id": ObjectId(objectId)}, {"$pull": {"likeDicts":{"user_id":userId}}})
            collection.update({"_id": ObjectId(objectId)},{"$set": {"likes":likes-1}})
            memCollection.update({"user_id": userId},{"$pull": {"likeDicts":{'photo_id':ObjectId(objectId)}}})

        else :
            likeDict = {'user_id':userId}
            collection.update({"_id": ObjectId(objectId)},{"$push": {"likeDicts":likeDict}})
            collection.update({"_id": ObjectId(objectId)},{"$set": {"likes":likes+1}})

            likeDict = {'photo_id':ObjectId(objectId),'Time':currentTime}
            memCollection.update({"user_id": userId},{"$push": {"likeDicts":likeDict}})

    data = collection.find_one({"_id": ObjectId(objectId)})

    likeFlag=0
    likeDictionary=data['likeDicts']

    for i in likeDictionary:
        if i.get('user_id') == userId:
            likeFlag=1
        
    data = collection.find_one({"_id": ObjectId(objectId)})

    if userId==photoUserId :
        return render_template('pages-gallery_detail_my.html',data = data, userName = userName,id=id)
    else :
        return render_template('pages-gallery_detail_other.html',data = data, userName = userName,id=id,likeFlag=likeFlag)


@app.route('/enrollComment', methods=['POST']) #댓글기능 구현
def enrollComment():
    userId = checkUserId()
    userName=getUserName()
    collection = db.PhotoInformation
    now = datetime.datetime.now()
    currentTime = str(now.strftime("%Y.%m.%d %H:%M"))

    commentContent = request.form['comment']
    objectId = request.form['objectId']

    data = collection.find_one({"_id": ObjectId(objectId)})
    commentNum = data['commentNumber']
    commentCount=data['commentCount']

    photoUserId=data['user_id']
            
            
    commentDict = {'commentNum':commentNum+1, 'userId':userId,'userName':userName, 'Time':currentTime,'comment':commentContent}
    collection.update({"_id": ObjectId(objectId)},{"$push": {"commentDicts":commentDict}})
    collection.update({"_id": ObjectId(objectId)},{"$set": {"commentNumber":commentNum+1}})
    collection.update({"_id": ObjectId(objectId)},{"$set": {"commentCount":commentCount+1}})


    data = collection.find_one({"_id": ObjectId(objectId)})
    if userId==photoUserId :
        return render_template('pages-gallery_detail_my.html',data = data, userName = userName,id=id)
    else :
        return render_template('pages-gallery_detail_other.html',data = data, userName = userName,id=id)

@app.route('/deleteComment', methods=['POST']) 
def deleteComment():
    userId = checkUserId()
    userName=getUserName()
    collection = db.PhotoInformation

    objectId = request.form['objectId']
    deleteCommentNum = request.form['commentNum']

    data = collection.find_one({"_id": ObjectId(objectId)})
    commentCount = data['commentCount']
    photoUserId=data['user_id']


    collection.update({"_id": ObjectId(objectId)}, {"$pull": {"commentDicts":{"commentNum":int(deleteCommentNum)}}})

    collection.update({"_id": ObjectId(objectId)},{"$set": {"commentCount":commentCount-1}})

    data = collection.find_one({"_id": ObjectId(objectId)})
    if userId==photoUserId :
        return render_template('pages-gallery_detail_my.html',data = data, userName = userName,id=id)
    else :
        return render_template('pages-gallery_detail_other.html',data = data, userName = userName,id=id)


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
        enrollPhotoNum = 0
        tokenNum = 0
        doc = {'user_id'    : userId,   'user_name'     : userName, 'password':newPassWord,
                'fame'    : fame,       'enrollPhotoNum': enrollPhotoNum, 
                'tokenNum': tokenNum,   'state' : 0,           'photo_number':0 #사진저장시 사용하는 번호
                }
        collection = db.Members
        cursor = collection.find({"user_id": userId})
        enrollFlag = 0
        
        for document in cursor:                   #회원 등록 확인
            if document['user_id'] == userId:
                enrollFlag = 1
                flash('이미 가입된 Email 입니다!')
                return render_template('pages-register.html', enrollFlag=enrollFlag)
        collection.insert_one(doc)                   #아이디 검사 완료시 회원정보 데이터베이스 삽입
        return render_template("pages-waitView.html")
    else:
        return "잘못된 데이터 요청 입니다."

@app.route("/pages-token")
def tokenExchange():
    userId=checkUserId()
    userName = getUserName()
    return render_template('pages-token.html', userName=userName)

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
    return delete_file(filename,app.config['UPLOAD_FOLDER'])

def delete_file(filename,path):
    #os.remove(os.path.join(path,filename))
    #flash('사진이 삭제되었습니다')
    return mainEnroll()

@app.route('/enrollPhoto', methods=['POST']) #사진게시 버튼 클릭 시 처리 함수
def enrollPhoto():
    if 'userId' in session:
        if request.method == 'POST':
            #latestPhotoNum = db.latestPhotoNum
            collection = db.PhotoInformation
            userCollection=db.Members
            userId = checkUserId()
            userInfo=userCollection.find_one({"user_id": userId})
            userName = getUserName()
            userPhotoNum=userInfo['photo_number']
            userPhotoNum+=1
            
            title = request.form['title']
            content = request.form['content']
            date = request.form['date']
            place = request.form['place']
            camera = request.form['camera']
            hashtag = request.form['hashtag']

            hashtag_list = hashtag.split("#")
            del hashtag_list[0]

            j=0

            hashDict=list()
            for i in hashtag_list:
                j+=1
                hashDict.append({'hashNum':j,'hashTag':i})

            
            hits = 0
            version = 1
            complete = 0
            commentNum = 0
            commentCount=0
            likes=0
            photoNum = userPhotoNum
            now = datetime.datetime.now()
            currentTime = str(now.strftime("%Y.%m.%d %H:%M"))
            
            fileName,first_hashValue,second_hashValue = upload_file()

            if fileName=="error" or first_hashValue=="error"or second_hashValue=="error":
                return render_template('pages-error-503.html')

            doc = {'user_id'     : userId,       
                   'hits'        : hits,         'content'     : content,
                   'version'     : version,      'complete'   : complete,
                   'title'       : title,        'hashTags'    : hashDict,
                   'photoNum'    : photoNum,     'first_hashValue' : first_hashValue,
                   'second_hashValue':second_hashValue, 'date':date,
                   'place':place, 'camera':camera,
                   'likes':likes,
                   'time'        : currentTime,  'commentNumber' : commentNum,
                   'fileName'    : fileName,     'userName'   : userName, 
                   'commentCount': commentCount
                   }
            collection.insert_one(doc)
            sessionState = checkSession()
            userCollection = db.Members
            userInfo = userCollection.find_one({"user_id": userId})
            enrollPhotoNum = userInfo['enrollPhotoNum']
            photo_number = userInfo['photo_number']
            userCollection.update({"user_id": userId}, {"$set":{"enrollPhotoNum":enrollPhotoNum+1}})
            userCollection.update({"user_id": userId}, {"$set":{"photo_number":photo_number+1}})


            

            #해쉬태그 doc push 하기 
        return render_template('pages-photo-waitView.html', hashValue=second_hashValue)
    else:
        loginFlag = 2   #로그인 정보 없을 때 로그인이 필요하다는 flag전달
        return render_template('pages-login.html', loginFlag=loginFlag)

@app.route('/mainEnroll', methods=['GET','POST']) #사진게시 버튼 클릭 시 처리 함수
def mainEnroll():
    userId=checkUserId()
    collection = db.PhotoInformation
    rows = collection.find({"user_id": userId}).sort("time",-1)
    userName = getUserName()
    return render_template('pages-gallery.html', data=rows, userName=userName)

def ipfs(filepath):
    client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')

    imagepath=os.path.join(app.config['TEMP_FOLDER'],filepath)
    res = client.add(imagepath)
    lst=list(res.values())
    client.close()
    return lst[1]

def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        userId=checkUserId()
        userCollection = db.Members
        userInfo = userCollection.find_one({"user_id": userId})
        userPhotoNum=userInfo['photo_number']
        userObid=userInfo['_id']

        if file.filename == '':
            #flash('선택된 사진이 없습니다.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            #flash('사진이 성공적으로 등록되었습니다.')
            filename = file.filename



            photoname=str(userObid)+'_'+str(userPhotoNum)+'_'+str(filename)
            file.save(os.path.join(app.config['TEMP_FOLDER'],photoname))
            #임시저장하고 파일의 타당성을 검사하고 업로드해야함
        

        image_path=os.path.join(app.config['TEMP_FOLDER'],photoname)
        #해쉬값 검사
        message=extractInfo(image_path)
        WMessage=message[0:46]
        print("추출된 해쉬값:"+WMessage)

        photoCollection = db.PhotoInformation
        count = photoCollection.count_documents({"first_hashValue":WMessage})
        
        if count==0:
            hashValue=ipfs(image_path)
            print("ipfs업로드 후 만들어진 hash value:"+hashValue)
            newimage=digitalWM(image_path,hashValue)
            newimagepath=os.path.join(app.config['UPLOAD_FOLDER'],photoname)
            
            
            save_image(newimage,newimagepath)

            second_hashValue=ipfs(newimagepath)
            #upload 폴더의 사진 지우고
            #db에 두번째 해쉬값 넣기

            #첫번째 해쉬값 : 디지털 워터마크 비교
            #두번째 해쉬값 : iframe 사진 띄우기용

            os.remove(os.path.join(app.config['TEMP_FOLDER'],photoname))
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'],photoname))
            return str(photoname),hashValue,second_hashValue

        else:
            os.remove(os.path.join(app.config['TEMP_FOLDER'],photoname))
            message1="error"
            message2="error"
            message3="error"
            return message1,message2,message3


def open_image(path):
    newimage=Image.open(path)
    return newimage

# Save Image
def save_image(image, path):
  image.save(path, 'png')

def digitalWM(path,hashValue):
    image=open_image(path)
    width,height=image.size

    #new=create_image(width,height)
    pixels=image.load()
    
    message = hashValue
    encoded_message=bytes(message,'utf-8')
    
    #ba=" ".join(f"{ord(i):08b}" for i in message)

    ba = bitarray.bitarray()
    ba.frombytes(encoded_message)
    bit_array = [int(i) for i in ba]
    #ba.frombytes(encoded_message.encode('utf-8'))
    #ba.frombytes(encoded_message)

    i = 0    
    
    for x in range(0,width):
        if len(pixels[x,0])==4:
            a,r,g,b=pixels[x,0]
        elif len(pixels[x,0])==3:
            r,g,b=pixels[x,0]
        else:
            return render_template('pages-error-500.html')

        #Default values in case no bit has to be modified
        new_bit_red_pixel = 255
        new_bit_green_pixel = 255
        new_bit_blue_pixel = 255

        if i<len(bit_array):
            #Red pixel
            r_bit = bin(r)
            r_last_bit = int(r_bit[-1])
            r_new_last_bit =  bit_array[i]
            new_bit_red_pixel = int(r_bit[:-1]+str(r_new_last_bit),2)
            i += 1

        if i<len(bit_array):
            #Green pixel
            g_bit = bin(g)
            g_last_bit = int(g_bit[-1])
            g_new_last_bit =  bit_array[i]
            new_bit_green_pixel = int(g_bit[:-1]+str(g_new_last_bit),2)
            i += 1

        if i<len(bit_array):
            #Blue pixel
            b_bit = bin(b)
            b_last_bit = int(b_bit[-1])
            b_new_last_bit =  bit_array[i]
            new_bit_blue_pixel = int(b_bit[:-1]+str(b_new_last_bit),2)
            i += 1
        if i>len(bit_array):
            break

        pixels[x,0] = (new_bit_red_pixel,new_bit_green_pixel,new_bit_blue_pixel)
    return image

def extractInfo(path):
    image = Image.open(path)

    extracted = ''

    pixels = image.load()
    # Iterate over pixels of the first row
    for x in range(0,image.width):
        if len(pixels[x,0])==4:
            a,r,g,b=pixels[x,0]
        elif len(pixels[x,0])==3:
            r,g,b=pixels[x,0]
        else:
            return render_template('pages-error-500.html')
        # Store LSB of each color channel of each pixel
        extracted += bin(r)[-1]
        extracted += bin(g)[-1]
        extracted += bin(b)[-1]

    chars = []
    for i in range(len(extracted)//8):
        byte = extracted[i*8:(i+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    # Don't forget that the message was base64-encoded
    flag = ''.join(chars)
    return flag

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

    print(querySentence)
    print(type(querySentence))

    querySentenceList = querySentence.split(b" ")
    tempList = []
    photoCursor = None
    photoCursor = photoCollection.find({"complete":0})

    for photo in photoCursor:
        photoTitle = photo['title']
        real_sentences = nltkExtract(photoTitle)#이부분 nltkExtract 따라서 찾기
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

def nltkExtract(sentence):#검색 서비스 
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
    return send_from_directory(os.path.join(root_dir ,'blockchainsns','static', 'js'), filename)
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)