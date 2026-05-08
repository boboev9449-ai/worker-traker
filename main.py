"""
Учёт рабочих - посещаемость и зарплата
Worker Tracker App — Python + KivyMD
"""

import json
import os
from datetime import date, timedelta
import uuid

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock

from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard


# ═══════════════════════════════════════════════════════════════════
#  DATA MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

DATA_FILE = 'data.json'   # будет перезаписан в build() на user_data_dir


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"workers": [], "attendance": {}, "advances": {}}


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════
#  DIALOG CONTENT WIDGETS
# ═══════════════════════════════════════════════════════════════════

class AddWorkerContent(BoxLayout):
    """Форма добавления/редактирования рабочего."""

    def __init__(self, **kwargs):
        super().__init__(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(10), dp(4), dp(10), dp(4)],
            size_hint_y=None,
            height=dp(148),
            **kwargs
        )
        self.name_field = MDTextField(
            hint_text='Имя рабочего',
            mode='rectangle',
        )
        self.salary_field = MDTextField(
            hint_text='Зарплата в день (сум)',
            mode='rectangle',
            input_filter='float',
        )
        self.add_widget(self.name_field)
        self.add_widget(self.salary_field)


class AdvanceContent(BoxLayout):
    """Форма ввода аванса."""

    def __init__(self, worker_name, current_advance=0, **kwargs):
        super().__init__(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(10), dp(4), dp(10), dp(4)],
            size_hint_y=None,
            height=dp(110),
            **kwargs
        )
        self.add_widget(MDLabel(
            text=f'Рабочий: {worker_name}',
            theme_text_color='Secondary',
            size_hint_y=None,
            height=dp(40),
        ))
        self.field = MDTextField(
            hint_text='Сумма аванса',
            mode='rectangle',
            input_filter='float',
            text=str(int(current_advance)) if current_advance else '',
        )
        self.add_widget(self.field)


# ═══════════════════════════════════════════════════════════════════
#  SCREEN: HOME
# ═══════════════════════════════════════════════════════════════════

class HomeScreen(Screen):
    pass


# ═══════════════════════════════════════════════════════════════════
#  SCREEN: WORKERS
# ═══════════════════════════════════════════════════════════════════

class WorkersScreen(Screen):

    def on_enter(self):
        self.refresh()

    def refresh(self):
        app = MDApp.get_running_app()
        lst = self.ids.workers_list
        lst.clear_widgets()

        if not app.data['workers']:
            lst.add_widget(MDLabel(
                text='Нет рабочих.\nНажмите  +  чтобы добавить.',
                halign='center',
                theme_text_color='Secondary',
                size_hint_y=None,
                height=dp(80),
            ))
            return

        for w in app.data['workers']:
            lst.add_widget(self._make_card(w))

    # ── Card ──────────────────────────────────────────────────────

    def _make_card(self, worker):
        card = MDCard(
            orientation='horizontal',
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(8),
            size_hint_y=None,
            height=dp(78),
            radius=[dp(10)],
            elevation=3,
        )

        info = BoxLayout(orientation='vertical')
        info.add_widget(MDLabel(
            text=worker['name'],
            font_style='H6',
        ))
        info.add_widget(MDLabel(
            text=f"{int(worker['salary_per_day']):,} сум / день",
            font_style='Caption',
            theme_text_color='Secondary',
        ))

        btns = BoxLayout(size_hint_x=None, width=dp(100), spacing=dp(2))
        edit_btn = MDIconButton(
            icon='pencil-outline',
            theme_text_color='Custom',
            text_color=(0.4, 0.7, 1.0, 1),
        )
        edit_btn.bind(on_release=lambda x, w=worker: self.edit_worker(w))

        del_btn = MDIconButton(
            icon='delete-outline',
            theme_text_color='Custom',
            text_color=(1.0, 0.35, 0.35, 1),
        )
        del_btn.bind(on_release=lambda x, w=worker: self.delete_worker(w))

        btns.add_widget(edit_btn)
        btns.add_widget(del_btn)

        card.add_widget(info)
        card.add_widget(btns)
        return card

    # ── Add ───────────────────────────────────────────────────────

    def show_add_dialog(self):
        content = AddWorkerContent()
        self._dlg = MDDialog(
            title='Добавить рабочего',
            type='custom',
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text='ОТМЕНА',
                    on_release=lambda x: self._dlg.dismiss(),
                ),
                MDRaisedButton(
                    text='ДОБАВИТЬ',
                    on_release=lambda x: self._add_worker(content),
                ),
            ],
        )
        self._dlg.open()

    def _add_worker(self, content):
        name = content.name_field.text.strip()
        salary = content.salary_field.text.strip()
        if not name or not salary:
            return
        app = MDApp.get_running_app()
        app.data['workers'].append({
            'id': str(uuid.uuid4())[:8],
            'name': name,
            'salary_per_day': float(salary),
        })
        save_data(app.data)
        self._dlg.dismiss()
        Clock.schedule_once(lambda dt: self.refresh(), 0.1)

    # ── Edit ──────────────────────────────────────────────────────

    def edit_worker(self, worker):
        content = AddWorkerContent()
        content.name_field.text = worker['name']
        content.salary_field.text = str(int(worker['salary_per_day']))
        self._dlg = MDDialog(
            title='Редактировать рабочего',
            type='custom',
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text='ОТМЕНА',
                    on_release=lambda x: self._dlg.dismiss(),
                ),
                MDRaisedButton(
                    text='СОХРАНИТЬ',
                    on_release=lambda x: self._save_edit(worker, content),
                ),
            ],
        )
        self._dlg.open()

    def _save_edit(self, worker, content):
        name = content.name_field.text.strip()
        salary = content.salary_field.text.strip()
        if not name or not salary:
            return
        app = MDApp.get_running_app()
        for w in app.data['workers']:
            if w['id'] == worker['id']:
                w['name'] = name
                w['salary_per_day'] = float(salary)
                break
        save_data(app.data)
        self._dlg.dismiss()
        Clock.schedule_once(lambda dt: self.refresh(), 0.1)

    # ── Delete ────────────────────────────────────────────────────

    def delete_worker(self, worker):
        self._cdlg = MDDialog(
            title='Удалить рабочего?',
            text=f'Удалить «{worker["name"]}»?\nВсе записи посещаемости будут удалены.',
            buttons=[
                MDFlatButton(
                    text='ОТМЕНА',
                    on_release=lambda x: self._cdlg.dismiss(),
                ),
                MDRaisedButton(
                    text='УДАЛИТЬ',
                    md_bg_color=(0.85, 0.15, 0.15, 1),
                    on_release=lambda x: self._do_delete(worker),
                ),
            ],
        )
        self._cdlg.open()

    def _do_delete(self, worker):
        app = MDApp.get_running_app()
        wid = worker['id']
        app.data['workers'] = [w for w in app.data['workers'] if w['id'] != wid]
        for day_data in app.data['attendance'].values():
            day_data.pop(wid, None)
        app.data['advances'].pop(wid, None)
        save_data(app.data)
        self._cdlg.dismiss()
        Clock.schedule_once(lambda dt: self.refresh(), 0.1)


# ═══════════════════════════════════════════════════════════════════
#  SCREEN: ATTENDANCE
# ═══════════════════════════════════════════════════════════════════

class AttendanceScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_date = date.today().isoformat()

    def on_enter(self):
        self.refresh()

    def refresh(self):
        app = MDApp.get_running_app()
        self.ids.date_btn.text = f'  📅  {self.current_date}  '
        lst = self.ids.att_list
        lst.clear_widgets()

        if not app.data['workers']:
            lst.add_widget(MDLabel(
                text='Нет рабочих.\nДобавьте их в разделе "Рабочие".',
                halign='center',
                theme_text_color='Secondary',
                size_hint_y=None,
                height=dp(80),
            ))
            return

        day_data = app.data['attendance'].get(self.current_date, {})
        came = sum(1 for v in day_data.values() if v is True)
        total = len(app.data['workers'])
        self.ids.summary_lbl.text = f'✅ {came} из {total} пришли'

        for w in app.data['workers']:
            status = day_data.get(w['id'])
            lst.add_widget(self._make_card(w, status))

    def _make_card(self, worker, status):
        if status is True:
            bg = (0.05, 0.45, 0.18, 0.35)
            status_txt = '✅ Пришёл'
            status_clr = (0.2, 0.9, 0.45, 1)
        elif status is False:
            bg = (0.55, 0.08, 0.08, 0.35)
            status_txt = '❌ Не пришёл'
            status_clr = (1.0, 0.35, 0.35, 1)
        else:
            bg = (0.13, 0.13, 0.16, 1)
            status_txt = '— не отмечен'
            status_clr = (0.55, 0.55, 0.55, 1)

        card = MDCard(
            orientation='vertical',
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(8),
            size_hint_y=None,
            height=dp(136),
            md_bg_color=bg,
            radius=[dp(12)],
            elevation=2,
        )

        # Name + status
        hdr = BoxLayout(size_hint_y=None, height=dp(38))
        hdr.add_widget(MDLabel(text=worker['name'], font_style='H6'))
        hdr.add_widget(MDLabel(
            text=status_txt,
            halign='right',
            theme_text_color='Custom',
            text_color=status_clr,
        ))
        card.add_widget(hdr)

        # Buttons
        btns = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(52))

        came_btn = MDRaisedButton(
            text='✅  ПРИШЁЛ',
            md_bg_color=(0.1, 0.62, 0.28, 1),
            size_hint_x=1,
            font_size='15sp',
        )
        came_btn.bind(on_release=lambda x, w=worker: self.mark(w, True))

        absent_btn = MDRaisedButton(
            text='❌  НЕ ПРИШЁЛ',
            md_bg_color=(0.82, 0.12, 0.12, 1),
            size_hint_x=1,
            font_size='15sp',
        )
        absent_btn.bind(on_release=lambda x, w=worker: self.mark(w, False))

        btns.add_widget(came_btn)
        btns.add_widget(absent_btn)
        card.add_widget(btns)
        return card

    def mark(self, worker, present):
        app = MDApp.get_running_app()
        att = app.data['attendance']
        if self.current_date not in att:
            att[self.current_date] = {}
        att[self.current_date][worker['id']] = present
        save_data(app.data)
        self.refresh()

    def prev_day(self):
        d = date.fromisoformat(self.current_date)
        self.current_date = (d - timedelta(days=1)).isoformat()
        self.refresh()

    def next_day(self):
        d = date.fromisoformat(self.current_date)
        self.current_date = (d + timedelta(days=1)).isoformat()
        self.refresh()

    def go_today(self):
        self.current_date = date.today().isoformat()
        self.refresh()


# ═══════════════════════════════════════════════════════════════════
#  SCREEN: REPORT
# ═══════════════════════════════════════════════════════════════════

class ReportScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.period_days = 30

    def on_enter(self):
        self.refresh()

    def set_period(self, days):
        self.period_days = days
        self.ids.period_lbl.text = f'Период: {days} дн.'
        self.refresh()

    def refresh(self):
        app = MDApp.get_running_app()
        lst = self.ids.report_list
        lst.clear_widgets()

        end = date.today()
        start = end - timedelta(days=self.period_days - 1)

        # All dates in period
        dates = []
        d = start
        while d <= end:
            dates.append(d.isoformat())
            d += timedelta(days=1)

        grand_total = 0

        for w in app.data['workers']:
            days_w = sum(
                1 for day in dates
                if app.data['attendance'].get(day, {}).get(w['id']) is True
            )
            earned = days_w * w['salary_per_day']
            advance = float(app.data['advances'].get(w['id'], 0))
            balance = earned - advance
            grand_total += balance
            lst.add_widget(self._make_card(w, days_w, earned, advance, balance))

        if not app.data['workers']:
            lst.add_widget(MDLabel(
                text='Нет рабочих для отчёта.',
                halign='center',
                theme_text_color='Secondary',
                size_hint_y=None,
                height=dp(80),
            ))
            return

        # Grand total card
        tc = MDCard(
            orientation='vertical',
            padding=[dp(16), dp(14), dp(16), dp(14)],
            spacing=dp(4),
            size_hint_y=None,
            height=dp(90),
            md_bg_color=(0.08, 0.10, 0.14, 1),
            radius=[dp(12)],
            elevation=5,
        )
        tc.add_widget(MDLabel(
            text='ИТОГО К ВЫПЛАТЕ',
            font_style='Caption',
            theme_text_color='Secondary',
        ))
        tc.add_widget(MDLabel(
            text=f'{int(grand_total):,} сум',
            font_style='H4',
            theme_text_color='Custom',
            text_color=(0.2, 1.0, 0.5, 1),
        ))
        lst.add_widget(tc)

    def _make_card(self, worker, days_w, earned, advance, balance):
        bal_color = (0.2, 0.88, 0.45, 1) if balance >= 0 else (1.0, 0.35, 0.35, 1)
        bal_icon = '→' if balance >= 0 else '⚠'

        card = MDCard(
            orientation='vertical',
            padding=[dp(14), dp(12), dp(14), dp(12)],
            spacing=dp(6),
            size_hint_y=None,
            height=dp(172),
            radius=[dp(12)],
            elevation=2,
        )

        # Header: name + advance button
        hdr = BoxLayout(size_hint_y=None, height=dp(38))
        hdr.add_widget(MDLabel(text=worker['name'], font_style='H6'))
        adv_btn = MDFlatButton(
            text='Аванс',
            size_hint=(None, None),
            size=(dp(82), dp(36)),
        )
        adv_btn.bind(on_release=lambda x, w=worker: self.show_advance(w))
        hdr.add_widget(adv_btn)
        card.add_widget(hdr)

        def info_row(left, right, clr=None):
            r = BoxLayout(size_hint_y=None, height=dp(26))
            r.add_widget(MDLabel(
                text=left,
                font_style='Caption',
                theme_text_color='Secondary' if not clr else 'Custom',
                text_color=clr or (1, 1, 1, 1),
            ))
            r.add_widget(MDLabel(
                text=right,
                halign='right',
                font_style='Caption',
                theme_text_color='Secondary' if not clr else 'Custom',
                text_color=clr or (1, 1, 1, 1),
            ))
            return r

        card.add_widget(info_row('Ставка:', f"{int(worker['salary_per_day']):,} сум/день"))
        card.add_widget(info_row('Дней отработано:', str(days_w)))
        card.add_widget(info_row('Заработано:', f'{int(earned):,} сум'))
        card.add_widget(info_row('Аванс:', f'{int(advance):,} сум'))

        # Balance
        bal = MDLabel(
            text=f'{bal_icon}  К выплате: {int(balance):,} сум',
            font_style='Subtitle1',
            theme_text_color='Custom',
            text_color=bal_color,
            size_hint_y=None,
            height=dp(32),
        )
        card.add_widget(bal)
        return card

    def show_advance(self, worker):
        app = MDApp.get_running_app()
        cur = float(app.data['advances'].get(worker['id'], 0))
        content = AdvanceContent(worker['name'], cur)
        self._adlg = MDDialog(
            title='Управление авансом',
            type='custom',
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text='СБРОСИТЬ',
                    theme_text_color='Custom',
                    text_color=(1, 0.4, 0.4, 1),
                    on_release=lambda x: self._reset_adv(worker),
                ),
                MDRaisedButton(
                    text='СОХРАНИТЬ',
                    on_release=lambda x: self._save_adv(worker, content),
                ),
            ],
        )
        self._adlg.open()

    def _save_adv(self, worker, content):
        val = content.field.text.strip()
        if not val:
            return
        app = MDApp.get_running_app()
        app.data['advances'][worker['id']] = float(val)
        save_data(app.data)
        self._adlg.dismiss()
        Clock.schedule_once(lambda dt: self.refresh(), 0.1)

    def _reset_adv(self, worker):
        app = MDApp.get_running_app()
        app.data['advances'].pop(worker['id'], None)
        save_data(app.data)
        self._adlg.dismiss()
        Clock.schedule_once(lambda dt: self.refresh(), 0.1)


# ═══════════════════════════════════════════════════════════════════
#  APP
# ═══════════════════════════════════════════════════════════════════

class WorkerTrackerApp(MDApp):

    def build(self):
        global DATA_FILE
        # На Android — user_data_dir (внутренняя папка приложения)
        DATA_FILE = os.path.join(self.user_data_dir, 'data.json')
        self.data = load_data()

        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.theme_style = 'Dark'
        self.title = 'Учёт Рабочих'

        return Builder.load_file('ui.kv')


if __name__ == '__main__':
    WorkerTrackerApp().run()
