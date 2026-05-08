"""
Учёт Рабочих — Pure Kivy (без KivyMD)
Совместимо с Android 15
"""

import json
import os
from datetime import date, timedelta
import uuid

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock


# ═══════════════════════════════════════════════════════
#  ЦВЕТА
# ═══════════════════════════════════════════════════════

C_BG        = (0.08, 0.09, 0.11, 1)
C_CARD      = (0.13, 0.14, 0.18, 1)
C_CARD2     = (0.16, 0.17, 0.22, 1)
C_GREEN     = (0.10, 0.62, 0.28, 1)
C_RED       = (0.80, 0.12, 0.12, 1)
C_BLUE      = (0.15, 0.45, 0.85, 1)
C_PURPLE    = (0.45, 0.12, 0.72, 1)
C_GRAY      = (0.30, 0.30, 0.35, 1)
C_TEXT      = (0.95, 0.95, 0.95, 1)
C_SUBTEXT   = (0.60, 0.60, 0.65, 1)
C_YELLOW    = (0.95, 0.80, 0.10, 1)

DATA_FILE = 'data.json'


# ═══════════════════════════════════════════════════════
#  ДАННЫЕ
# ═══════════════════════════════════════════════════════

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"workers": [], "attendance": {}, "advances": {}}


def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Save error: {e}")


# ═══════════════════════════════════════════════════════
#  UI КОМПОНЕНТЫ
# ═══════════════════════════════════════════════════════

def make_btn(text, bg=C_BLUE, fg=C_TEXT, height=dp(56), font_size=16, **kwargs):
    btn = Button(
        text=text,
        size_hint_y=None,
        height=height,
        background_normal='',
        background_color=bg,
        color=fg,
        font_size=sp(font_size),
        bold=True,
        **kwargs
    )
    return btn


def make_label(text, color=C_TEXT, font_size=15, bold=False, halign='left', **kwargs):
    lbl = Label(
        text=text,
        color=color,
        font_size=sp(font_size),
        bold=bold,
        halign=halign,
        **kwargs
    )
    lbl.bind(size=lambda *a: setattr(lbl, 'text_size', (lbl.width, None)))
    return lbl


def sp(val):
    from kivy.metrics import sp as kivy_sp
    return kivy_sp(val)


def card_layout(height=dp(80), bg=C_CARD, radius=12, **kwargs):
    layout = BoxLayout(
        size_hint_y=None,
        height=height,
        padding=[dp(14), dp(10)],
        spacing=dp(8),
        **kwargs
    )
    with layout.canvas.before:
        Color(*bg)
        layout._rect = RoundedRectangle(
            pos=layout.pos,
            size=layout.size,
            radius=[dp(radius)]
        )
    layout.bind(
        pos=lambda *a: setattr(layout._rect, 'pos', layout.pos),
        size=lambda *a: setattr(layout._rect, 'size', layout.size)
    )
    return layout


def separator():
    w = Widget(size_hint_y=None, height=dp(8))
    return w


class TopBar(BoxLayout):
    def __init__(self, title, back_screen=None, **kwargs):
        super().__init__(
            size_hint_y=None,
            height=dp(58),
            padding=[dp(8), dp(6)],
            spacing=dp(8),
            **kwargs
        )
        with self.canvas.before:
            Color(0.05, 0.06, 0.09, 1)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=lambda *a: setattr(self._rect, 'pos', self.pos),
            size=lambda *a: setattr(self._rect, 'size', self.size)
        )
        if back_screen:
            back = Button(
                text='←',
                size_hint=(None, None),
                size=(dp(48), dp(44)),
                background_normal='',
                background_color=C_GRAY,
                font_size=sp(20),
                bold=True,
            )
            back.bind(on_release=lambda x: setattr(App.get_running_app().root, 'current', back_screen))
            self.add_widget(back)

        self.add_widget(Label(
            text=title,
            font_size=sp(18),
            bold=True,
            color=C_TEXT,
        ))


# ═══════════════════════════════════════════════════════
#  POPUP
# ═══════════════════════════════════════════════════════

def show_popup(title, content_widget, buttons):
    """buttons = list of (text, color, callback)"""
    box = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(14))
    box.add_widget(Label(
        text=title,
        font_size=sp(17),
        bold=True,
        color=C_TEXT,
        size_hint_y=None,
        height=dp(36),
    ))
    box.add_widget(content_widget)

    btn_row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
    popup = Popup(
        title='',
        content=box,
        size_hint=(0.92, None),
        height=dp(320),
        background_color=(0.10, 0.11, 0.15, 1),
        separator_height=0,
        title_size=0,
    )

    for (txt, clr, cb) in buttons:
        def make_cb(callback):
            def inner(x):
                popup.dismiss()
                if callback:
                    Clock.schedule_once(lambda dt: callback(), 0.1)
            return inner
        b = Button(
            text=txt,
            background_normal='',
            background_color=clr,
            color=C_TEXT,
            font_size=sp(14),
            bold=True,
        )
        b.bind(on_release=make_cb(cb))
        btn_row.add_widget(b)

    box.add_widget(btn_row)
    popup.open()
    return popup


# ═══════════════════════════════════════════════════════
#  ЭКРАН: ГЛАВНАЯ
# ═══════════════════════════════════════════════════════

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build()

    def _build(self):
        root = BoxLayout(orientation='vertical')
        with root.canvas.before:
            Color(*C_BG)
            root._rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda *a: setattr(root._rect, 'pos', root.pos),
            size=lambda *a: setattr(root._rect, 'size', root.size)
        )

        root.add_widget(TopBar('👷 Учёт Рабочих'))

        content = BoxLayout(
            orientation='vertical',
            padding=[dp(24), dp(30)],
            spacing=dp(16),
        )

        content.add_widget(Label(
            text='Выберите раздел',
            color=C_SUBTEXT,
            font_size=sp(15),
            size_hint_y=None,
            height=dp(36),
            halign='center',
        ))

        def nav_btn(text, color, screen):
            b = Button(
                text=text,
                size_hint_y=None,
                height=dp(68),
                background_normal='',
                background_color=color,
                color=C_TEXT,
                font_size=sp(18),
                bold=True,
            )
            b.bind(on_release=lambda x: setattr(self.manager, 'current', screen))
            return b

        content.add_widget(nav_btn('👷   Рабочие', C_BLUE, 'workers'))
        content.add_widget(nav_btn('📋   Посещаемость', C_GREEN, 'attendance'))
        content.add_widget(nav_btn('📊   Отчёт', C_PURPLE, 'report'))
        content.add_widget(Widget())

        root.add_widget(content)
        self.add_widget(root)


# ═══════════════════════════════════════════════════════
#  ЭКРАН: РАБОЧИЕ
# ═══════════════════════════════════════════════════════

class WorkersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._root = BoxLayout(orientation='vertical')
        with self._root.canvas.before:
            Color(*C_BG)
            r = Rectangle(pos=self._root.pos, size=self._root.size)
        self._root.bind(
            pos=lambda *a: setattr(r, 'pos', self._root.pos),
            size=lambda *a: setattr(r, 'size', self._root.size)
        )

        # TopBar
        bar = TopBar('👷 Рабочие', back_screen='home')
        add_btn = Button(
            text='+ Добавить',
            size_hint=(None, None),
            size=(dp(110), dp(44)),
            background_normal='',
            background_color=C_GREEN,
            color=C_TEXT,
            font_size=sp(14),
            bold=True,
        )
        add_btn.bind(on_release=lambda x: self.show_add())
        bar.add_widget(add_btn)
        self._root.add_widget(bar)

        self._scroll = ScrollView(do_scroll_x=False)
        self._list = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=[dp(12), dp(12)],
            size_hint_y=None,
        )
        self._list.bind(minimum_height=self._list.setter('height'))
        self._scroll.add_widget(self._list)
        self._root.add_widget(self._scroll)
        self.add_widget(self._root)

    def on_enter(self):
        self.refresh()

    def refresh(self):
        self._list.clear_widgets()
        app = App.get_running_app()
        workers = app.data['workers']

        if not workers:
            self._list.add_widget(Label(
                text='Нет рабочих.\nНажмите "+ Добавить"',
                color=C_SUBTEXT,
                font_size=sp(15),
                halign='center',
                size_hint_y=None,
                height=dp(100),
            ))
            return

        for w in workers:
            self._list.add_widget(self._make_card(w))

    def _make_card(self, w):
        card = card_layout(height=dp(80), bg=C_CARD, orientation='horizontal')

        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(
            text=w['name'],
            color=C_TEXT,
            font_size=sp(16),
            bold=True,
            halign='left',
            text_size=(None, None),
        ))
        info.add_widget(Label(
            text=f"{int(w['salary_per_day']):,} сум / день",
            color=C_SUBTEXT,
            font_size=sp(13),
            halign='left',
            text_size=(None, None),
        ))
        card.add_widget(info)

        edit = Button(
            text='✏️',
            size_hint=(None, 1),
            width=dp(50),
            background_normal='',
            background_color=C_BLUE,
            font_size=sp(18),
        )
        edit.bind(on_release=lambda x, worker=w: self.show_edit(worker))

        delete = Button(
            text='🗑',
            size_hint=(None, 1),
            width=dp(50),
            background_normal='',
            background_color=C_RED,
            font_size=sp(18),
        )
        delete.bind(on_release=lambda x, worker=w: self.confirm_delete(worker))

        card.add_widget(edit)
        card.add_widget(delete)
        return card

    def _form(self, name='', salary=''):
        box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(130))
        name_inp = TextInput(
            hint_text='Имя рабочего',
            text=name,
            size_hint_y=None,
            height=dp(52),
            background_color=(0.18, 0.19, 0.24, 1),
            foreground_color=C_TEXT,
            cursor_color=C_TEXT,
            font_size=sp(15),
            multiline=False,
        )
        sal_inp = TextInput(
            hint_text='Зарплата в день (сум)',
            text=salary,
            size_hint_y=None,
            height=dp(52),
            background_color=(0.18, 0.19, 0.24, 1),
            foreground_color=C_TEXT,
            cursor_color=C_TEXT,
            font_size=sp(15),
            multiline=False,
            input_filter='float',
        )
        box.add_widget(name_inp)
        box.add_widget(sal_inp)
        return box, name_inp, sal_inp

    def show_add(self):
        box, name_inp, sal_inp = self._form()

        def do_add():
            name = name_inp.text.strip()
            salary = sal_inp.text.strip()
            if not name or not salary:
                return
            app = App.get_running_app()
            app.data['workers'].append({
                'id': str(uuid.uuid4())[:8],
                'name': name,
                'salary_per_day': float(salary),
            })
            save_data(app.data)
            self.refresh()

        show_popup('Добавить рабочего', box, [
            ('Отмена', C_GRAY, None),
            ('Добавить', C_GREEN, do_add),
        ])

    def show_edit(self, worker):
        box, name_inp, sal_inp = self._form(
            worker['name'],
            str(int(worker['salary_per_day']))
        )

        def do_save():
            name = name_inp.text.strip()
            salary = sal_inp.text.strip()
            if not name or not salary:
                return
            app = App.get_running_app()
            for w in app.data['workers']:
                if w['id'] == worker['id']:
                    w['name'] = name
                    w['salary_per_day'] = float(salary)
                    break
            save_data(app.data)
            self.refresh()

        show_popup('Редактировать', box, [
            ('Отмена', C_GRAY, None),
            ('Сохранить', C_BLUE, do_save),
        ])

    def confirm_delete(self, worker):
        lbl = Label(
            text=f'Удалить «{worker["name"]}»?\nПосещаемость тоже удалится.',
            color=C_TEXT,
            font_size=sp(15),
            halign='center',
            size_hint_y=None,
            height=dp(80),
        )

        def do_delete():
            app = App.get_running_app()
            wid = worker['id']
            app.data['workers'] = [w for w in app.data['workers'] if w['id'] != wid]
            for day in app.data['attendance'].values():
                day.pop(wid, None)
            app.data['advances'].pop(wid, None)
            save_data(app.data)
            self.refresh()

        show_popup('Удалить?', lbl, [
            ('Отмена', C_GRAY, None),
            ('Удалить', C_RED, do_delete),
        ])


# ═══════════════════════════════════════════════════════
#  ЭКРАН: ПОСЕЩАЕМОСТЬ
# ═══════════════════════════════════════════════════════

class AttendanceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_date = date.today().isoformat()
        self._root = BoxLayout(orientation='vertical')
        with self._root.canvas.before:
            Color(*C_BG)
            r = Rectangle(pos=self._root.pos, size=self._root.size)
        self._root.bind(
            pos=lambda *a: setattr(r, 'pos', self._root.pos),
            size=lambda *a: setattr(r, 'size', self._root.size)
        )
        self._root.add_widget(TopBar('📋 Посещаемость', back_screen='home'))

        # Date nav
        nav = BoxLayout(size_hint_y=None, height=dp(56), padding=[dp(8), dp(6)], spacing=dp(6))
        prev = Button(text='◀', size_hint=(None, None), size=(dp(50), dp(44)),
                      background_normal='', background_color=C_GRAY, font_size=sp(18))
        prev.bind(on_release=lambda x: self.change_day(-1))

        self._date_btn = Button(
            text=self.current_date,
            size_hint=(1, None), height=dp(44),
            background_normal='', background_color=(0.18, 0.22, 0.30, 1),
            color=C_TEXT, font_size=sp(14), bold=True,
        )
        self._date_btn.bind(on_release=lambda x: self.go_today())

        nxt = Button(text='▶', size_hint=(None, None), size=(dp(50), dp(44)),
                     background_normal='', background_color=C_GRAY, font_size=sp(18))
        nxt.bind(on_release=lambda x: self.change_day(1))

        nav.add_widget(prev)
        nav.add_widget(self._date_btn)
        nav.add_widget(nxt)
        self._root.add_widget(nav)

        self._summary = Label(
            text='', color=C_SUBTEXT, font_size=sp(13),
            size_hint_y=None, height=dp(26), halign='center',
        )
        self._root.add_widget(self._summary)

        self._scroll = ScrollView(do_scroll_x=False)
        self._list = GridLayout(cols=1, spacing=dp(10),
                                padding=[dp(12), dp(6)], size_hint_y=None)
        self._list.bind(minimum_height=self._list.setter('height'))
        self._scroll.add_widget(self._list)
        self._root.add_widget(self._scroll)
        self.add_widget(self._root)

    def on_enter(self):
        self.refresh()

    def change_day(self, delta):
        d = date.fromisoformat(self.current_date)
        self.current_date = (d + timedelta(days=delta)).isoformat()
        self.refresh()

    def go_today(self):
        self.current_date = date.today().isoformat()
        self.refresh()

    def refresh(self):
        self._date_btn.text = f'  📅  {self.current_date}  '
        self._list.clear_widgets()
        app = App.get_running_app()
        workers = app.data['workers']

        if not workers:
            self._list.add_widget(Label(
                text='Нет рабочих.\nДобавьте в разделе "Рабочие".',
                color=C_SUBTEXT, font_size=sp(15),
                halign='center', size_hint_y=None, height=dp(100),
            ))
            self._summary.text = ''
            return

        day_data = app.data['attendance'].get(self.current_date, {})
        came = sum(1 for v in day_data.values() if v is True)
        self._summary.text = f'✅ {came} из {len(workers)} пришли'

        for w in workers:
            status = day_data.get(w['id'])
            self._list.add_widget(self._make_card(w, status))

    def _make_card(self, w, status):
        if status is True:
            bg = (0.05, 0.22, 0.09, 1)
        elif status is False:
            bg = (0.22, 0.05, 0.05, 1)
        else:
            bg = C_CARD

        card = card_layout(height=dp(130), bg=bg, orientation='vertical', spacing=dp(8))

        # Name row
        name_row = BoxLayout(size_hint_y=None, height=dp(34))
        name_row.add_widget(Label(
            text=w['name'], color=C_TEXT, font_size=sp(16), bold=True, halign='left',
        ))
        status_text = '✅ Пришёл' if status is True else ('❌ Не пришёл' if status is False else '— не отмечен')
        status_color = C_GREEN if status is True else (C_RED if status is False else C_SUBTEXT)
        name_row.add_widget(Label(
            text=status_text, color=status_color, font_size=sp(13), halign='right',
        ))
        card.add_widget(name_row)

        # Buttons
        btn_row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))

        came_btn = Button(
            text='✅  ПРИШЁЛ',
            background_normal='', background_color=C_GREEN,
            color=C_TEXT, font_size=sp(15), bold=True,
        )
        came_btn.bind(on_release=lambda x, worker=w: self.mark(worker, True))

        absent_btn = Button(
            text='❌  НЕ ПРИШЁЛ',
            background_normal='', background_color=C_RED,
            color=C_TEXT, font_size=sp(15), bold=True,
        )
        absent_btn.bind(on_release=lambda x, worker=w: self.mark(worker, False))

        btn_row.add_widget(came_btn)
        btn_row.add_widget(absent_btn)
        card.add_widget(btn_row)
        return card

    def mark(self, worker, present):
        app = App.get_running_app()
        att = app.data['attendance']
        if self.current_date not in att:
            att[self.current_date] = {}
        att[self.current_date][worker['id']] = present
        save_data(app.data)
        self.refresh()


# ═══════════════════════════════════════════════════════
#  ЭКРАН: ОТЧЁТ
# ═══════════════════════════════════════════════════════

class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.period_days = 30
        self._root = BoxLayout(orientation='vertical')
        with self._root.canvas.before:
            Color(*C_BG)
            r = Rectangle(pos=self._root.pos, size=self._root.size)
        self._root.bind(
            pos=lambda *a: setattr(r, 'pos', self._root.pos),
            size=lambda *a: setattr(r, 'size', self._root.size)
        )
        self._root.add_widget(TopBar('📊 Отчёт', back_screen='home'))

        # Period bar
        pbar = BoxLayout(size_hint_y=None, height=dp(54), padding=[dp(8), dp(6)], spacing=dp(6))
        self._period_lbl = Label(
            text='30 дней', color=C_SUBTEXT, font_size=sp(13),
            size_hint_x=0.28,
        )
        pbar.add_widget(self._period_lbl)

        for days, label in [(7, '7 дн'), (14, '14 дн'), (30, '30 дн')]:
            b = Button(
                text=label,
                background_normal='', background_color=C_BLUE,
                color=C_TEXT, font_size=sp(13), bold=True,
            )
            b.bind(on_release=lambda x, d=days: self.set_period(d))
            pbar.add_widget(b)

        reset = Button(
            text='Сброс',
            background_normal='', background_color=C_GRAY,
            color=C_TEXT, font_size=sp(12),
        )
        reset.bind(on_release=lambda x: self.set_period(30))
        pbar.add_widget(reset)
        self._root.add_widget(pbar)

        self._scroll = ScrollView(do_scroll_x=False)
        self._list = GridLayout(cols=1, spacing=dp(10),
                                padding=[dp(12), dp(8)], size_hint_y=None)
        self._list.bind(minimum_height=self._list.setter('height'))
        self._scroll.add_widget(self._list)
        self._root.add_widget(self._scroll)
        self.add_widget(self._root)

    def on_enter(self):
        self.refresh()

    def set_period(self, days):
        self.period_days = days
        self._period_lbl.text = f'{days} дней'
        self.refresh()

    def refresh(self):
        self._list.clear_widgets()
        app = App.get_running_app()
        workers = app.data['workers']

        if not workers:
            self._list.add_widget(Label(
                text='Нет рабочих для отчёта.',
                color=C_SUBTEXT, font_size=sp(15),
                halign='center', size_hint_y=None, height=dp(100),
            ))
            return

        end = date.today()
        start = end - timedelta(days=self.period_days - 1)
        dates = []
        d = start
        while d <= end:
            dates.append(d.isoformat())
            d += timedelta(days=1)

        grand_total = 0

        for w in workers:
            days_w = sum(
                1 for day in dates
                if app.data['attendance'].get(day, {}).get(w['id']) is True
            )
            earned = days_w * w['salary_per_day']
            advance = float(app.data['advances'].get(w['id'], 0))
            balance = earned - advance
            grand_total += balance
            self._list.add_widget(self._make_card(w, days_w, earned, advance, balance))

        # Итого
        total_card = card_layout(height=dp(88), bg=(0.06, 0.08, 0.12, 1), orientation='vertical')
        total_card.add_widget(Label(
            text='ИТОГО К ВЫПЛАТЕ',
            color=C_SUBTEXT, font_size=sp(12),
            size_hint_y=None, height=dp(22),
        ))
        total_card.add_widget(Label(
            text=f'{int(grand_total):,} сум',
            color=C_GREEN if grand_total >= 0 else C_RED,
            font_size=sp(26), bold=True,
        ))
        self._list.add_widget(total_card)

    def _make_card(self, w, days_w, earned, advance, balance):
        bal_color = C_GREEN if balance >= 0 else C_RED
        card = card_layout(height=dp(190), bg=C_CARD, orientation='vertical', spacing=dp(4))

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(38))
        hdr.add_widget(Label(
            text=w['name'], color=C_TEXT, font_size=sp(16), bold=True, halign='left',
        ))
        adv_btn = Button(
            text='💰 Аванс',
            size_hint=(None, None), size=(dp(90), dp(34)),
            background_normal='', background_color=C_GRAY,
            color=C_TEXT, font_size=sp(12),
        )
        adv_btn.bind(on_release=lambda x, worker=w: self.show_advance(worker))
        hdr.add_widget(adv_btn)
        card.add_widget(hdr)

        def row(left, right, right_color=C_SUBTEXT):
            r = BoxLayout(size_hint_y=None, height=dp(28))
            r.add_widget(Label(text=left, color=C_SUBTEXT, font_size=sp(13), halign='left'))
            r.add_widget(Label(text=right, color=right_color, font_size=sp(13), halign='right'))
            return r

        card.add_widget(row('Ставка:', f"{int(w['salary_per_day']):,} сум/день"))
        card.add_widget(row('Отработано дней:', str(days_w)))
        card.add_widget(row('Заработано:', f'{int(earned):,} сум', C_TEXT))
        card.add_widget(row('Аванс:', f'{int(advance):,} сум', C_YELLOW))

        bal_row = BoxLayout(size_hint_y=None, height=dp(34))
        bal_row.add_widget(Label(
            text=f'К выплате: {int(balance):,} сум',
            color=bal_color, font_size=sp(15), bold=True, halign='left',
        ))
        card.add_widget(bal_row)
        return card

    def show_advance(self, worker):
        app = App.get_running_app()
        cur = float(app.data['advances'].get(worker['id'], 0))

        box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(100))
        box.add_widget(Label(
            text=f'Рабочий: {worker["name"]}',
            color=C_SUBTEXT, font_size=sp(14),
            size_hint_y=None, height=dp(30),
        ))
        inp = TextInput(
            hint_text='Сумма аванса',
            text=str(int(cur)) if cur else '',
            size_hint_y=None, height=dp(52),
            background_color=(0.18, 0.19, 0.24, 1),
            foreground_color=C_TEXT,
            font_size=sp(15),
            multiline=False,
            input_filter='float',
        )
        box.add_widget(inp)

        def do_save():
            val = inp.text.strip()
            if val:
                app.data['advances'][worker['id']] = float(val)
                save_data(app.data)
                self.refresh()

        def do_reset():
            app.data['advances'].pop(worker['id'], None)
            save_data(app.data)
            self.refresh()

        show_popup(f'Аванс — {worker["name"]}', box, [
            ('Сброс', C_RED, do_reset),
            ('Сохранить', C_GREEN, do_save),
        ])


# ═══════════════════════════════════════════════════════
#  APP
# ═══════════════════════════════════════════════════════

class WorkerTrackerApp(App):
    def build(self):
        global DATA_FILE
        DATA_FILE = os.path.join(self.user_data_dir, 'data.json')
        self.data = load_data()

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(WorkersScreen(name='workers'))
        sm.add_widget(AttendanceScreen(name='attendance'))
        sm.add_widget(ReportScreen(name='report'))
        return sm


if __name__ == '__main__':
    WorkerTrackerApp().run()
