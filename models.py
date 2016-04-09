# -*- coding: gbk -*-

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship

from config import options

Base = declarative_base()

engine = create_engine('mysql://{0}:{1}@{2}/{3}?charset=utf8'.format(options['mysql_user'], options['mysql_password'], options['mysql_host'], options['mysql_db']), 
                        pool_size=options['mysql_poolsize'],
                        pool_recycle=3600,
                        echo=options['debug'],
                        echo_pool=options['debug'])

Base.metadata.create_all(engine)

class User(Base):
    '''
    For Login.
    '''
    __tablename__ = 'users'
    uid = Column(Integer, primary_key=True)
    uname = Column(String(80), nullable=False)
    upass = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(80), nullable=True)

    def __repr__(self):
        return 'uid: %s, uname: %s, upass: %s, phone: %s, email: %s' % (self.uid, self.uname, self.upass, self.phone, self.email)

class UserProfile(Base):
    '''
    For Show.
    '''
    __tablename__ = 'user_profile'
    profile_id = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey('users.uid'))
    uname = Column(String(80))
    gender = Column(Integer)
    age = Column(Integer)
    address = Column(String(80))
    birthday = Column(Date)
    city = Column(String(50))
    score = Column(Integer)
    vote_max = Column(Integer)
    is_admin = Column(Integer)
    user = relationship(User)

    def __repr__(self):
        return 'uid: %s, uname: %s, gender: %d, age: %d, address: %s, birthday: %s, city: %s, score: %d, vote_max: %d' % (self.uid, self.uname, self.gender, self.age, self.address, str(self.birthday), self.city, self.score, self.vote_max)

class Activity(Base):
    '''
    Match or Contest.
    '''
    __tablename__ = 'activity'
    act_id = Column(Integer, primary_key=True)
    act_name = Column(String(80), nullable=False)
    desc = Column(String(200))
    uid = Column(Integer, ForeignKey('users.uid'))
    user = relationship(User)
    class_name = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)

    def __repr__(self):
        return 'act_id: %s, act_name: %s, desc: %s, uid: %s, class_name: %s, start_time: %s, end_time: %s' \
                    % (self.act_id, self.act_name, self.desc, self.uid, self.class_name, self.start_time, self.end_time)

class Involvement(Base):
    '''
    User's involvement in a contest.
    '''
    __tablename__ = 'involvement'
    id = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey('users.uid'))
    involve_type = Column(Integer, nullable=False)
    user = relationship(User)
    act_id = Column(Integer, ForeignKey('activity.act_id'))
    activity = relationship(Activity)
    desc = Column(String(200))
    publish_time = Column(DateTime, nullable=False)
    uri = Column(String(80), nullable=False)

    def __repr__(self):
        return 'work_id: %s, uid: %s, act_id: %s, desc: %s, publish_time: %s, work_content: %s' \
                    % (self.id, self.uid, self.act_id, self.desc, str(self.publish_time), self.uri)

class Advice(Base):
    __tablename__ = 'advice'
    advice_id = Column(Integer, primary_key=True)
    uid = Column(Integer, nullable=False)
    content = Column(String(200), nullable=False)
    contact = Column(String(80), nullable=False)

    def __repr__(self):
        return 'uid: %s, content: %s, contact: %s' % (self.uid, self.content, self.contact)

class Backend(object):
    def __init__(self):
        self._session = sessionmaker(bind=engine)
    
    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
    
    def get_session(self):
        return self._session()


