#!/usr/bin/env python

from __future__ import unicode_literals
import fbchat
import re
import os, requests
from PIL import Image
import datetime
import traceback
import pprint
import sys
import random
import string

def formula_as_file(formula, file):
    # Takes a LaTeX formula saves a png in file loaction
    formula = formula.replace('\n', ' ')
    r = requests.get('http://latex.codecogs.com/png.latex?\\dpi{{300}} \\bg_white {formula}'.format(formula=formula))
    f = open(file, 'wb')
    f.write(r.content)
    f.close()

    old_im = Image.open(file)
    old_size = old_im.size
    new_size = map(lambda x: x+19, old_size)
    new_im = Image.new("RGBA", new_size, (255, 255, 255))
    new_im.paste(old_im, ((new_size[0]-old_size[0])/2,
                          (new_size[1]-old_size[1])/2))
    new_im.save(file, "PNG")

class FbLaTeX(fbchat.Client):
    def __init__(self, startmsg, adminID, *args, **kwargs):
        super(FbLaTeX, self).__init__(*args, **kwargs)

        # Username and password
        self.un = args[0]
        self.pw = args[1]

        # UID's of people trusted enough to send updates to code and turn the bot off
        self.adminusers = [adminID]
        # UID's of people who want to get spammed every time the bot breaks
        errorusers = [adminID]

        # Send each admin user a start message
        for uid in self.adminusers:
            try:
                self.sendMessage(startmsg, thread_id=uid, thread_type=fbchat.models.ThreadType.USER)
            except:
                print "Error sending message to {}".format(uid)

        self.turnoff = "".join(string.printable[random.randint(0, 61)] for i in range(16))
        self.turnoffable = False

    def onMessageError(self, exception, msg):
        try:
            error = traceback.format_exc()
        except:
            print "Error in onMessageError"
        else:
            errormsg = "```On message error:\n" + error + ("="*20) + "\nMessage data:\n" + pprint.pformat(msg) + "```"

            # Send each error user a traceback
            for uid in self.errorusers:
                try:
                    self.sendMessage(errormsg, thread_id=uid, thread_type=fbchat.models.ThreadType.USER)
                except:
                    print "Error sending message to {}".format(uid)

    def onMessage(self, author_id, message, thread_id, thread_type, message_object, metadata, msg, **kwargs):
        self.markAsDelivered(author_id, thread_id)
        self.markAsRead(author_id)

        if author_id != self.uid:
            # Update code
            if author_id in self.adminusers and thread_type == fbchat.models.ThreadType.USER and len(msg["delta"]["attachments"]) == 1:
                # Get and check filename
                msgfile = msg["delta"]["attachments"][0]
                if msgfile["filename"][-3:] == ".py":
                    # Get infor from page which redirects to the file location, no idea why fb does this
                    codewrapperurl = msgfile["mercury"]["blob_attachment"]["url"]
                    r = requests.get(codewrapperurl)

                    # Find the url it rediects to
                    actualurlre = re.search(r'document\.location\.replace\("([^"]+)"\)', r.content)
                    if actualurlre:
                        # Get this versions code and save in new file
                        f = open(__file__)
                        mycode = f.read()
                        f.close()

                        f = open("old/FbLaTeX"+str(datetime.datetime.now()).replace(" ", "_").replace(":", "_")+".py", "w")
                        f.write(mycode)
                        f.close()

                        # Rewrite this code with the new one
                        # url is string in js so / need to be parsed
                        r = requests.get(actualurlre.group(1).replace("\/", "/"))
                        f = open(__file__, "w")
                        f.write(r.content)
                        f.close()

                        # Tell the user its resarting and restart
                        self.sendMessage("Restarting", thread_id=thread_id, thread_type=thread_type)
                        self.stopListening()
                        self.logout()
                        os.execlp("python", "python", __file__, self.un, self.pw, self.adminusers[0])
                    else:
                        # Redirect page has probably changed
                        self.sendMessage("Oops, couldn't redirect to file\n{}".format(r.content), thread_id=thread_id, thread_type=thread_type)
                else:
                    self.sendMessage("Oops, not python", thread_id=thread_id, thread_type=thread_type)

            # Turn the bot off safely
            rematch = re.match(r'^goodnight$', message, re.I)
            if author_id in self.adminusers and rematch and thread_type == fbchat.models.ThreadType.USER:
                self.turnoff = "".join(string.printable[random.randint(0, 61)] for i in range(5))
                self.turnoffable = True

                self.sendMessage('Turn off string is "{}"'.format(self.turnoff), thread_id=thread_id, thread_type=thread_type)

            rematch = re.match("^{}$".format(self.turnoff), message)
            if author_id in self.adminusers and rematch and thread_type == fbchat.models.ThreadType.USER and self.turnoffable:
                self.sendMessage("Night!", thread_id=thread_id, thread_type=thread_type)
                self.stopListening()
                self.logout()

            # Check if bot is running
            rematch = re.match(r'^you ok\??$', message, re.I)
            if author_id in self.adminusers and rematch:
                self.sendMessage("I'm good ;)", thread_id=thread_id, thread_type=thread_type)

            rematch = re.match(r'^[fF]ormula ((.+\n?)+)$', message, re.M)
            if rematch:
                formula_as_file(rematch.group(1), "temp.png")
                self.sendLocalImage("temp.png", thread_id=thread_id, thread_type=thread_type)

            rematch = re.match(r'^\$((.+\n?)+)\$$', message, re.M)
            if rematch:
                formula_as_file(rematch.group(1), "temp.png")
                self.sendLocalImage("temp.png", thread_id=thread_id, thread_type=thread_type)

if __name__ == "__main__":
    if len(sys.argv) > 3:
        bot = FbLaTeX("Running", str(sys.argv[3]), sys.argv[1], sys.argv[2], False)
        bot.listen()
    else:
        print "Usage: python .\FbLaTeX.py\ [EMAIL OF BOT] [PASSWORD OF BOT] [ADMIN FB ID]"
