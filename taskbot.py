#!/usr/bin/env python3

import json
import requests
import time
import urllib
import sqlalchemy

from datetime import datetime
from token_telegram import *

import db
from db import Task

TOKEN = getToken()
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

HELP = """
 /new NOME
 /todo ID
 /doing ID
 /done ID
 /delete ID
 /list
 /rename ID NOME
 /dependson ID ID...
 /duplicate ID
 /priority ID PRIORITY{low, medium, high}
 /help
 /duedate ID DATE{YYYY-MM-DD}
"""

"""Emojis"""
TODO_EMOJI = "\U0001F195"
DOING_EMOJI = "\U000023FA"
DONE_EMOJI = "\U00002611"
LIST_EMOJI = "\U0001F4CB"
STATUS_EMOJI = "\U0001F4DD"


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))

    return max(update_ids)

def deps_text(task, chat, preceed=''):
    text = ''

    for i in range(len(task.dependencies.split(',')[:-1])):
        line = preceed
        dep = Task.find_by(id=int(task.dependencies.split(',')[:-1][i]), chat=chat)

        icon = TODO_EMOJI
        if dep.status == 'DOING':
            icon = DOING_EMOJI
        elif dep.status == 'DONE':
            icon = DONE_EMOJI

        if i + 1 == len(task.dependencies.split(',')[:-1]):
            line += '└── [[{}]] {} {}\n'.format(dep.id, icon, dep.name)
            line += deps_text(dep, chat, preceed + '    ')
        else:
            line += '├── [[{}]] {} {}\n'.format(dep.id, icon, dep.name)
            line += deps_text(dep, chat, preceed + '│   ')

        text += line

    return text


def handle_updates(updates):
    for update in updates["result"]:
        if 'message' in update:
            message = update['message']
        elif 'edited_message' in update:
            message = update['edited_message']
        else:
            print('Can\'t process! {}'.format(update))
            return

        command = message["text"].split(" ", 1)[0]
        msg = ''
        if len(message["text"].split(" ", 1)) > 1:
            msg = message["text"].split(" ", 1)[1].strip()

        chat = message["chat"]["id"]

        print(command, msg, chat)

        if command == '/new':
            if msg == '':
                send_message("A task must have a name", chat)
            else:
                task = Task.create(chat=chat, name=msg, status='TODO', dependencies='', parents='', priority='')
                send_message("New task *TODO* [[{}]] {}".format(task.id, task.name), chat)

        elif command == '/rename':
            text = ''
            if msg != '':
                if len(msg.split(' ', 1)) > 1:
                    text = msg.split(' ', 1)[1]
                msg = msg.split(' ', 1)[0]

            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                try:
                    task = Task.find_by(id=task_id, chat=chat)
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return

                if text == '':
                    send_message("You want to modify task {}, but you didn't provide any new text".format(task_id), chat)
                    return

                old_text = task.name
                task.name = text
                task.save()
                send_message("Task {} redefined from {} to {}".format(task_id, old_text, text), chat)

        elif command == '/duedate':

            message_params = msg.split(' ', 1)
            task_id = message_params[0]

            if not task_id.isdigit():
                send_message("You must inform for the task id", chat)
                return

            try:
                duedate = message_params[1]
            except IndexError:
                send_message("You want to set a due date to the task {}, but you didn't provide a due date".format(task_id), chat)
                return

            task_id = int(task_id)
            try:
                task = Task.find_by(id=task_id, chat=chat)
            except sqlalchemy.orm.exc.NoResultFound:
                send_message("_404_ Task {} not found x.x".format(task_id), chat)
                return

            try:
                task.duedate = datetime.strptime(duedate, "%Y-%m-%d").date()
            except ValueError:
                send_message("You must inform the due date in the following format: YYYY-MM-DD", chat)
                return

            task.save()
            send_message("Task {} due date was set to {}".format(task_id, duedate), chat)

        elif command == '/duplicate':
            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                try:
                    task = Task.find_by(id=task_id, chat=chat)
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return

                dtask = Task.create(chat=task.chat, name=task.name, status=task.status, dependencies=task.dependencies,
                             parents=task.parents, priority=task.priority, duedate=task.duedate)

                for t in task.dependencies.split(',')[:-1]:
                    t = Task.find_by(id=int(t), chat=chat)
                    t.parents += '{},'.format(dtask.id)

                task.save()
                send_message("New task *TODO* [[{}]] {}".format(dtask.id, dtask.name), chat)

        elif command == '/delete':
            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                try:
                    task = Task.find_by(id=task_id, chat=chat)
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return
                for t in task.dependencies.split(',')[:-1]:
                    t = Task.find_by(id=int(t), chat=chat)
                    t.parents = t.parents.replace('{},'.format(task.id), '')
                task.delete()
                send_message("Task [[{}]] deleted".format(task_id), chat)

        elif command == '/todo':
            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                try:
                    task = Task.find_by(id=task_id, chat=chat)
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return
                task.status = 'TODO'
                task.save()
                send_message("*TODO* task [[{}]] {}".format(task.id, task.name), chat)

        elif command == '/doing':
            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                try:
                    task = Task.find_by(id=task_id, chat=chat)
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return
                task.status = 'DOING'
                task.save()
                send_message("*DOING* task [[{}]] {}".format(task.id, task.name), chat)

        elif command == '/done':
            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                try:
                    task = Task.find_by(id=task_id, chat=chat)
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return
                task.status = 'DONE'
                task.save()
                send_message("*DONE* task [[{}]] {}".format(task.id, task.name), chat)

        elif command == '/list':
            a = ''

            a += '{} Task List\n'.format(LIST_EMOJI)
            tasks = Task.filter_by(parents='', chat=chat).order_by(Task.id)
            for task in tasks.all():
                icon = TODO_EMOJI
                if task.status == 'DOING':
                    icon = DOING_EMOJI
                elif task.status == 'DONE':
                    icon = DONE_EMOJI

                if not task.duedate:
                    a += '[[{}]] {} {} {}\n'.format(task.id, icon, task.name, task.priority)
                    a += deps_text(task, chat)
                else:
                    a += '[[{}]] {} {} {} {}\n'.format(task.id, icon, task.name, task.priority, task.duedate)
                    a += deps_text(task, chat)

            send_message(a, chat)
            a = ''

            a += '{} _Status_\n'.format(STATUS_EMOJI)
            tasks = Task.filter_by(status='TODO', chat=chat).order_by(Task.id)
            a += '\n{} *TODO*\n'.format(TODO_EMOJI)
            for task in tasks.all():
                a += '[[{}]] {}\n'.format(task.id, task.name)
            tasks = Task.filter_by(status='DOING', chat=chat).order_by(Task.id)
            a += '\n{} *DOING*\n'.format(DOING_EMOJI)
            for task in tasks.all():
                a += '[[{}]] {}\n'.format(task.id, task.name)
            tasks = Task.filter_by(status='DONE', chat=chat).order_by(Task.id)
            a += '\n\{} *DONE*\n'.format(DONE_EMOJI)
            for task in tasks.all():
                a += '[[{}]] {}\n'.format(task.id, task.name)

            send_message(a, chat)
        elif command == '/dependson':
            text = ''
            if msg != '':
                if len(msg.split(' ', 1)) > 1:
                    text = msg.split(' ', 1)[1]
                msg = msg.split(' ', 1)[0]

            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                try:
                    task = Task.find_by(id=task_id, chat=chat)
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return

                if text == '':
                    for i in task.dependencies.split(',')[:-1]:
                        i = int(i)
                        t = Task.find_by(id=i, chat=chat)
                        t.parents = t.parents.replace('{},'.format(task.id), '')

                    task.dependencies = ''
                    send_message("Dependencies removed from task {}".format(task_id), chat)
                else:
                    for depid in text.split(' '):
                        if not depid.isdigit():
                            send_message("All dependencies ids must be numeric, and not {}".format(depid), chat)
                        else:
                            depid = int(depid)
                            try:
                                taskdep = Task.find_by(id=depid, chat=chat)
                                taskdep.parents += str(task.id) + ','
                            except sqlalchemy.orm.exc.NoResultFound:
                                send_message("_404_ Task {} not found x.x".format(depid), chat)
                                continue

                            deplist = task.dependencies.split(',')
                            if str(depid) not in deplist:
                                task.dependencies += str(depid) + ','

                task.save()
                send_message("Task {} dependencies up to date".format(task_id), chat)

        elif command == '/priority':
            text = ''
            if msg != '':
                if len(msg.split(' ', 1)) > 1:
                    text = msg.split(' ', 1)[1]
                msg = msg.split(' ', 1)[0]

            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                try:
                    task = Task.find_by(id=task_id, chat=chat)
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return

                if text == '':
                    task.priority = ''
                    send_message("_Cleared_ all priorities from task {}".format(task_id), chat)
                else:
                    if text.lower() not in ['high', 'medium', 'low']:
                        send_message("The priority *must be* one of the following: high, medium, low", chat)
                    else:
                        task.priority = text.lower()
                        send_message("*Task {}* priority has priority *{}*".format(task_id, task.priority), chat)
                task.save()


        elif command == '/start':
            send_message("Welcome! Here is a list of things you can do.", chat)
            send_message(HELP, chat)
        elif command == '/help':
            send_message("Here is a list of things you can do.", chat)
            send_message(HELP, chat)
        else:
            send_message("I'm sorry dave. I'm afraid I can't do that.", chat)


def main():
    last_update_id = None

    while True:
        print("Updates")
        updates = get_updates(last_update_id)

        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)

        time.sleep(0.5)


if __name__ == '__main__':
    main()
