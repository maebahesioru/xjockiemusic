# キュー管理（JSON永続化）
import json
import os
import random
import time


class Queue:
    def __init__(self, path):
        self.path = path
        self.items = []
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                self.items = json.load(open(self.path, encoding='utf-8'))
            except Exception:
                self.items = []

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        json.dump(self.items, open(self.path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    def add(self, title, url, user):
        """末尾に追加"""
        item = {'title': title, 'url': url, 'user': user, 'added': time.time()}
        self.items.append(item)
        self.save()
        return len(self.items)

    def insert(self, title, url, user, pos=0):
        """指定位置に挿入（デフォルト=先頭・再生中の次）"""
        item = {'title': title, 'url': url, 'user': user, 'added': time.time()}
        self.items.insert(pos, item)
        self.save()
        return pos + 1

    def next(self):
        if not self.items:
            return None
        item = self.items.pop(0)
        self.save()
        return item

    def remove(self, idx):
        if 0 <= idx < len(self.items):
            item = self.items.pop(idx)
            self.save()
            return item
        return None

    def peek(self):
        return self.items[0] if self.items else None

    def list(self):
        return list(self.items)

    def clear(self):
        self.items = []
        self.save()

    def shuffle(self):
        random.shuffle(self.items)
        self.save()

    def reverse(self):
        self.items.reverse()
        self.save()

    def move(self, frm, to):
        """frm番目の曲をto番目へ移動（0始まり・範囲外はクランプ）"""
        if not (0 <= frm < len(self.items)):
            return None
        item = self.items.pop(frm)
        to = max(0, min(to, len(self.items)))
        self.items.insert(to, item)
        self.save()
        return item

    def swap(self, a, b):
        """a番目とb番目を入れ替え"""
        if not (0 <= a < len(self.items) and 0 <= b < len(self.items)):
            return None
        self.items[a], self.items[b] = self.items[b], self.items[a]
        self.save()
        return True

    def sort_by(self, key='title'):
        """キューを並べ替え（title / user / duration）"""
        if key == 'title':
            self.items.sort(key=lambda x: x.get('title', '').lower())
        elif key == 'user':
            self.items.sort(key=lambda x: x.get('user', '').lower())
        elif key == 'duration':
            self.items.sort(key=lambda x: x.get('duration', 0))
        self.save()
