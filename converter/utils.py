import os
import re
import sys

from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtWidgets import (
        QAction, QLayout, QLineEdit, QListWidget, QListWidgetItem, QMenu,
        QSpacerItem, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout
        )


def duration_in_seconds(duration):
    duration = duration.split('.')[0] # get rid of milliseconds
    hours, mins, secs = [int(i) for i in duration.split(':')]
    return secs + (hours * 3600) + (mins * 60)

def is_installed(program):
    program = os.path.expanduser(program)
    for path in os.getenv('PATH').split(os.pathsep):
        fpath = os.path.join(path, program)
        if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
            return fpath
    return ''

def find_presets_file(fname, lookup_dirs, lookup_virtenv):
    possible_dirs = os.environ.get(
            "XDG_DATA_DIRS", ":".join(lookup_dirs)
            ).split(":")
    # for virtualenv installations
    posdir = os.path.realpath(
            os.path.join(os.path.dirname(sys.argv[0]), '..', lookup_virtenv))
    if not posdir in possible_dirs:
        possible_dirs.append(posdir)

    for _dir in possible_dirs:
        _file = os.path.join(_dir, 'ffmulticonverter/' + fname)
        if os.path.exists(_file):
            return _file

    # when program is not installed or running from test_dialogs.py
    return os.path.dirname(os.path.realpath(__file__)) + '/../share/' + fname

def create_paths_list(
        files_list, ext_to, prefix, suffix, output):
    assert ext_to.startswith('.'), 'ext_to must start with a dot (.)'

    conversion_list = []
    dummy = []

    for _file in files_list:
        _dir, name = os.path.split(_file)
        y = prefix + os.path.splitext(name)[0] + suffix + ext_to
        y = output + '/' + y
        while os.path.exists(y) or y in dummy:
            _dir2, _name2 = os.path.split(y)
            y = _dir2 + '/~' + _name2

        dummy.append(y)
        # Add quotations to paths in order to avoid error in special
        # cases such as spaces or special characters.
        _file = '"' + _file + '"'
        y = '"' + y + '"'

        _dict = {}
        _dict[_file] = y
        conversion_list.append(_dict)

    return conversion_list

def update_cmdline_text(command, _filter, regex, add, gindex1, gindex2):
    """
    Update and return the command line text by adding, removing or edditing a
    ffmpeg filter based on the given regular expression.

    Keyword arguments:
    command  -- initial command text (string)
    _filter  -- ffmpeg filter to add or edit in command (string)
    regex    -- regex to search in command
    add      -- if True, add filter to command, else filter must be removed
    gindex1  -- group index of the first group before filter group in regex
    gindex2  -- group index of the first group after filter group in regex
    """
    regex2 = r'(-vf "[^"]*)"'
    regex3 = r'-vf +([^ ]+)'

    search = re.search(regex, command)
    if search:
        if add:
            command = re.sub(
                    regex,
                    r'\{0}{1}\{2}'.format(gindex1+1, _filter, gindex2+1),
                    command
                    )
        else:
            group1 = search.groups()[gindex1].strip()
            group2 = search.groups()[gindex2].strip()
            if group1 and group2:
                # the filter is between 2 other filters
                # remove it and leave a comma
                command = re.sub(regex, ',', command)
            else:
                # remove filter
                command = re.sub(regex, _filter, command)
                # add a space between -vf and filter if needed
                command = re.sub(r'-vf([^ ])', r'-vf \1', command)
                if not group1 and not group2:
                    # remove -vf option
                    command = re.sub(r'-vf *("\s*"){0,1}', '', command)
    elif re.search(regex2, command):
        command = re.sub(regex2, r'\1,{0}"'.format(_filter), command)
    elif re.search(regex3, command):
        command = re.sub(regex3, r'-vf "\1,{0}"'.format(_filter), command)
    elif _filter:
        command += ' -vf "' + _filter + '"'

    return re.sub(' +', ' ', command).strip()


def add_to_layout(layout, *items):
    if isinstance(layout, str):
        if layout == "v":
            layout = QVBoxLayout()
        elif layout == "h":
            layout = QHBoxLayout()
        else:
            raise TypeError("Invalid layout!")

    for item in items:
        if isinstance(item, QWidget):
            layout.addWidget(item)
        elif isinstance(item, QLayout):
            layout.addLayout(item)
        elif isinstance(item, QSpacerItem):
            layout.addItem(item)
        elif item is None:
            layout.addStretch()
        else:
            raise TypeError("Argument of wrong type!")
    return layout

def add_to_grid(*items):
    layout = QGridLayout()
    for x, _list in enumerate(items):
        for y, item in enumerate(_list):
            if isinstance(item, QWidget):
                layout.addWidget(item, x, y)
            elif isinstance(item, QLayout):
                layout.addLayout(item, x, y)
            elif isinstance(item, QSpacerItem):
                layout.addItem(item, x, y)
            elif item is None:
                pass
            else:
                raise TypeError("Argument of wrong type!")
    return layout

def create_action(parent, text, shortcut=None, icon=None, tip=None,
                  triggered=None, toggled=None, context=Qt.WindowShortcut):
    action = QAction(text, parent)
    if triggered is not None:
        action.triggered.connect(triggered)
    if toggled is not None:
        action.toggled.connect(toggled)
        action.setCheckable(True)
    if icon is not None:
        action.setIcon( icon )
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    action.setShortcutContext(context)
    return action

def add_actions(target, actions, insert_before=None):
    previous_action = None
    target_actions = list(target.actions())
    if target_actions:
        previous_action = target_actions[-1]
        if previous_action.isSeparator():
            previous_action = None
    for action in actions:
        if (action is None) and (previous_action is not None):
            if insert_before is None:
                target.addSeparator()
            else:
                target.insertSeparator(insert_before)
        elif isinstance(action, QMenu):
            if insert_before is None:
                target.addMenu(action)
            else:
                target.insertMenu(insert_before, action)
        elif isinstance(action, QAction):
            if insert_before is None:
                target.addAction(action)
            else:
                target.insertAction(insert_before, action)
        previous_action = action

def create_LineEdit(maxsize, validator, maxlength):
    lineEdit = QLineEdit()
    if maxsize is not None:
        lineEdit.setMaximumSize(QSize(maxsize[0], maxsize[1]))
    if validator is not None:
        lineEdit.setValidator(validator)
    if maxlength is not None:
        lineEdit.setMaxLength(maxlength)
    return lineEdit


class XmlListItem(QListWidgetItem):
    def __init__(self, text, xml_element, parent=None):
        super(XmlListItem, self).__init__(text, parent)
        self.xml_element = xml_element


class FilesList(QListWidget):
    dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super(FilesList, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(url.toLocalFile())
            self.dropped.emit(links)
        else:
            event.ignore()
