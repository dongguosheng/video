# -*- coding: gbk -*-

from handler import *
import tornado.ioloop
import tornado.web

settings = {
        'cookie_secret' : 'TD+7sroLRq+ebIThRP4hRlXctoK/iEMap8Zc4b2Cl3s=',
        # 'xsrf_cookies' : True,
        'login_url': '/'
        }

application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/user/login', LoginHandler),
    (r'/user/register', PhoneRegistHandler),
    (r'/activity/add', ActivityAddHandler),
    (r'/involve/add', InvolveAddHandler),
    (r'/upload', UploadHandler),
    (r'/advice/submit', AdviceSubmitHandler),
    (r'/advice/view', AdviceViewHandler),
    (r'/user/modifyProfile', ProfileModifyHandler),
    (r'/user/profile', ProfileViewHandler),
    (r'/user/score_to_vote', ScoreToVoteHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path' : './static/'})
], debug=True, **settings)

def main():
    application.listen(8082)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
