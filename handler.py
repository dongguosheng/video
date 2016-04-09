# -*- coding: gbk -*-

import tornado.ioloop
import tornado.web
from operator import itemgetter
from datetime import datetime
import time
from subprocess import Popen
from shutil import move
import os
import json
from utils import encode_md5
from models import *
from config import *

class BaseHandler(tornado.web.RequestHandler):
    @property
    def backend(self):
        return Backend.instance()
    def get_current_user(self):
        return self.get_secure_cookie('uname')

class MainHandler(BaseHandler):
    def get(self):
        self.render('login.html', title=u'Admin Demo')
        # self.write('Hello World.')

def to_dict(user_profile):
    rs_dict = {}
    rs_dict['uid'] = str(user_profile.uid)
    rs_dict['uname'] = user_profile.uname
    rs_dict['gender'] = str(user_profile.gender)
    rs_dict['age'] = str(user_profile.age)
    rs_dict['address'] = user_profile.address
    rs_dict['birthday'] = str(user_profile.birthday)
    rs_dict['city'] = user_profile.city
    rs_dict['score'] = str(user_profile.score)
    rs_dict['vote_max'] = str(user_profile.vote_max)
    rs_dict['is_admin'] = user_profile.is_admin
    return rs_dict

class LoginHandler(BaseHandler):
    def post(self):
        # receive args
        rs_type = self.get_argument('rs_type', 0)
        # print '======>' + str(rs_type)
        uname = self.get_argument('uname', '')
        upass = self.get_argument('upass', '')
        # init json result
        rs = {'code' : 1, 'msg' : '', 'result' : []}
        # args check
        if len(uname) == 0 or len(upass) == 0:
            rs['msg'] = INVALID_ARGS
            self.write(json.dumps(rs))
            return
        # db operations
        upass_md5 = encode_md5(upass)
        session = self.backend.get_session()
        user_profile_dict = {}
        try:
            # TODO:
            u = session.query(User).filter_by(uname=uname).first()
            # print 'upass: %s' % upass_md5
            # print 'u.upass: %s' % u.upass
            if u is not None and u.upass == upass_md5:
                rs['code'] = 0
                rs['result'].append( {'uname': u.uname, 'upass': upass} )
                user_profile = session.query(UserProfile).filter(UserProfile.uid == u.uid).first()
                user_profile_dict = to_dict(user_profile)
                # set cookies
                self.set_secure_cookie('uname', uname)
            else:
                rs['msg'] = EMPTY_RESULT
        except Exception, e:
            # pass
            rs['msg'] = str(e).encode('utf-8')
            # session.rollback()
        finally:
            # json string
            if rs_type > 0:
                self.write(json.dumps(rs))
            # render html for admin
            else:
                if len(user_profile_dict) > 0 and user_profile_dict['is_admin'] > 0:
                    self.render('admin_index.html', user_profile_dict=user_profile_dict)
                else:
                    self.render('login.html', error_msg=u'Login Failed')
            session.close()

    def get(self):
        self.render('login.html')

class ScoreToVoteHandler(BaseHandler):
    def post(self):
        # receive args
        uid = self.get_argument('uid', '')
        vote_num = self.get_argument('vote_num', 0)
        vote_num = int(vote_num)
        # init json result
        rs = {'code' : 1, 'msg' : ''}
        # args check
        if len(uid) == 0:
            rs['msg'] = INVALID_ARGS
            self.write(json.dumps(rs))
            return
        # db operations
        session = self.backend.get_session()
        try:
            print 'uid: ' + uid
            user_profile = session.query(UserProfile).filter(UserProfile.uid == uid).first()
            rs['code'] = 0
            # TODO: handle exception..
            user_profile.vote_max += vote_num
            user_profile.score -= vote_num * 100
            rs['user_profile'] = to_dict(user_profile)
            session.commit()
        except Exception, e:
            rs['msg'] = str(e).encode('utf-8')
            session.rollback()
        finally:
            self.write(json.dumps(rs))
            session.close()       

    def get(self):
        self.post()

class PhoneRegistHandler(BaseHandler):
    def post(self):
        # receive args
        phone = self.get_argument('phone', '')
        upass = self.get_argument('upass', '')
        # init json result
        rs = {'code' : 1, 'msg' : ''}
        # args check
        if len(phone) == 0 or len(upass) == 0:
            rs['msg'] = INVALID_ARGS
            self.write(json.dumps(rs))
            return
        # db operations
        upass_md5 = encode_md5(upass)
        session = self.backend.get_session()
        try:
            user = User(uname=phone, phone=phone, upass=upass_md5)
            print 'uid: %s' % user.uid
            session.add(user)
            session.commit()
            rs['code'] = 0
        except Exception, e:
            rs['msg'] = str(e).encode('utf-8')
            session.rollback()
        finally:
            self.write(json.dumps(rs))
            session.close()
            
    def get(self):
        self.post()

class ProfileViewHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # receive args
        uid = self.get_argument('uid', '')
        # init json result
        rs = {'code' : 1, 'msg' : ''}
        # args check
        if len(uid) == 0:
            rs['msg'] = INVALID_ARGS
            self.write(json.dumps(rs))
            return
        # db operations
        session = self.backend.get_session()
        try:
            print 'uid: ' + uid
            user_profile = session.query(UserProfile).filter(UserProfile.uid == uid).first()
            rs['code'] = 0
            rs['user_profile'] = to_dict(user_profile)
        except Exception, e:
            rs['msg'] = str(e).encode('utf-8')
            session.rollback()
        finally:
            self.write(json.dumps(rs))
            session.close()

    def post(self):
        self.get()

class ProfileModifyHandler(BaseHandler):
    def post(self):
        # receive args
        uid = self.get_argument('uid', '')
        uname = self.get_argument('uname', '')
        gender = self.get_argument('gender', '')
        birthday = self.get_argument('birthday', '')
        email = self.get_argument('email', '')
        city = self.get_argument('city', '')
        # init json result
        rs = {'code' : 1, 'msg' : ''}
        # args check
        if len(uid) == 0 or len(uname) + len(gender) + len(str(birthday)) + len(email) + len(city) == 0:
            rs['msg'] = INVALID_ARGS
            self.write(json.dumps(rs))
            return
        try:
            birthday = datetime.strptime(birthday, '%Y-%m-%d').date() 
        except ValueError, e:
            rs['msg'] = str(e).encode('utf-8')
            self.write(json.dumps(rs))
            return
        # db operations
        session = self.backend.get_session()
        try:
            session.query(UserProfile).filter(UserProfile.uid==uid).update({'uname' : uname, 'gender' : gender, 'birthday' : birthday, 'city' : city})
            session.commit()
            rs['code'] = 0
        except Exception, e:
            rs['msg'] = str(e).encode('utf-8')
            session.rollback()
        finally:
            self.write(json.dumps(rs))
            session.close()

    def get(self):
        self.post()

class ActivityAddHandler(BaseHandler):
    def post(self):
        # receive args
        uid = self.get_argument('uid', '')
        act_name = self.get_argument('act_name', '')
        desc = self.get_argument('desc', '')
        class_name = self.get_argument('class_name', '')
        start_time = self.get_argument('start_time', '')
        end_time = self.get_argument('end_time', '')
        # init json result
        rs = {'code' : 1, 'msg' : ''}
        # args check
        if len(uid) == 0 or len(act_name) == 0 or len(class_name) == 0 or len(start_time) == 0:
            rs['msg'] = INVALID_ARGS
            self.write(json.dumps(rs))
            return
        # db operations
        try:
            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        except ValueError, e:
            rs['msg'] = str(e).encode('utf-8')
            self.write(json.dumps(rs))
            return
        if len(end_time) != 0:
            try:
                end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            except ValueError, e:
                rs['msg'] = str(e).encode('utf-8')
                self.write(json.dumps(rs))
                return
        session = self.backend.get_session()
        try:
            activity = Activity(uid=uid, act_name=act_name, desc=desc, class_name=class_name, start_time=start_time, end_time=end_time)
            session.add(activity)
            session.commit()
            rs['code'] = 0
            # print 'act_id: %s' % activity.act_id
            rs['activity_id'] = activity.act_id
        except Exception, e:
            rs['msg'] = str(e).encode('utf-8')
            session.rollback()
        finally:
            self.write(json.dumps(rs))
            session.close()

    def get(self):
        self.post()

class InvolveAddHandler(BaseHandler):
    def post(self):
        # receive args
        uid = self.get_argument('uid', '')
        act_id = self.get_argument('act_id', '')
        desc = self.get_argument('desc', '')
        involve_type = self.get_argument('type', '')
        # init json result
        rs = {'code' : 1, 'msg' : ''}
        # args check
        if len(uid) == 0 or len(act_id) == 0 or len(type) == 0:
            rs['msg'] = INVALID_ARGS
            self.write(json.dumps(rs))
            return
        try:
            involve_type = int(involve_type)
            if involve_type > 3:
                rs['msg'] = INVALID_ARGS
                self.write(json.dumps(rs))
                return
        except Exception, e:
            rs['msg'] = INVALID_ARGS
            self.write(json.dumps(rs))
            return
        # db operations
        session = self.backend.get_session()
        try:
            involvement  = Involvement(uid=uid, act_id=act_id, desc=desc, involve_type=involve_type, publish_time=datetime.now())
            session.add(involvement)
            session.commit()
            rs['code'] = 0
        except Exception, e:
            rs['msg'] = str(e).encode('utf-8')
            session.rollback()
        finally:
            self.write(json.dumps(rs))
            session.close()

    def get(self):
        self.post()


class AdviceSubmitHandler(BaseHandler):
    def post(self):
        # receive args
        uid = self.get_argument('uid', '')
        content = self.get_argument('content', '')
        contact = self.get_argument('contact', '')
        # init json result
        rs = {'code' : 1, 'msg' : ''}
        # args check
        if len(uid) == 0 or len(content) == 0 or len(contact) == 0:
            rs['msg'] = INVALID_ARGS
            self.write(json.dumps(rs))
            return
        # db operations
        session = self.backend.get_session()
        try:
            print 'uid: %s, content: %s, contact: %s' % (uid, content, contact)
            advice = Advice(uid=uid, content=content.encode('utf-8'), contact=contact.encode('utf-8'))
            session.add(advice)
            session.commit()
            rs['code'] = 0
        except Exception, e:
            # pass
            rs['msg'] = str(e).encode('utf-8')
            session.rollback()
        finally:
            self.write(json.dumps(rs))
            session.close()

    def get(self):
        self.post()

class AdviceViewHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        page = self.get_argument('page', '')
        rs_type = self.get_argument('rs_type', 0)
        if len(page) == 0:
            page = 1
        else:
            page = int(page)
        # db operations
        session = self.backend.get_session()
        advice_list = []
        try:
            advice_list = session.query(Advice).order_by(Advice.advice_id).slice(0, 30)
            print "advice list len: %d" % len(advice_list)
        except Exception, e:
            print e
        finally:
            if rs_type == 0:
                self.render('advice.html', advice_list=advice_list)

    def post(self):
        self.get()

class UploadHandler(tornado.web.RequestHandler):
    def initialize(self):
        global total_count
        total_count += 1
        print '(' + str(total_count) + ')request from ' + self.request.remote_ip + ', ' + str(datetime.now())

    def format_str(self, s):
        s = strB2Q(s.strip())
        return s.encode('gbk')
    
    def get(self):
        self.post()

    def post(self):
        root_dir = UPLOAD_ROOT
        uri = 'static/upload/'
        filename = self.get_argument('v.name')
        path = self.get_argument('v.path')
        # print "filename: " + filename
        # print "path: " + path
        file_new = root_dir + uri + filename
        # print "new file name: " + file_new
        try:
            move(path, file_new)
        except IOError:
            print 'shutil move ioerror.'
            self.redirect('/')
        os.chmod(file_new, 444)
        uri = uri + filename[: filename.rfind(r'.')] + '.mp4'
        output = root_dir + uri
        # print output
        if not filename.endswith('.mp4'):
            try:
                shell_cmd = 'ffmpeg -i {input} -y {output}'.format(input=file_new, output=output)
                print 'Shell cmg: ' + shell_cmd
                p = Popen(shell_cmd.split(), shell=True)
                rs_code = p.wait()
                print 'rs_code: ' + str(rs_code)
            except OSError:
                print 'ffmpeg oserror.'
        
        # self.finish("file uploaded!")
        # self.write('sucess')
        self.render('play.html', title=u'Video Demo', name=uri)

total_count = 0
