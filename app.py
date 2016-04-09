# -*- coding: gbk -*-

from handler import *
import tornado.ioloop
import tornado.web

application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/user/login', LoginHandler),
    (r'/user/register', PhoneRegistHandler),
    (r'/activity/add', ActivityAddHandler),
    (r'/involve/add', InvolveAddHandler),
    (r'/upload', UploadHandler),
    (r'/advice/submit', AdviceSubmitHandler),
    (r'/user/modifyProfile', ProfileModifyHandler),
    (r'/user/profile', ProfileViewHandler),
    (r'/user/score_to_vote', ScoreToVoteHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path' : './static/'})
], debug=True)

def main():
    application.listen(8082)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
