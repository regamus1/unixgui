from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp, QSize
from PyQt5.QtWidgets import (
        QWidget, QComboBox, QLineEdit, QLabel,QCheckBox, 
        QRadioButton, QSpacerItem, QSizePolicy, 
        QFrame, QButtonGroup, QToolButton
        )

from converter import utils
from converter import config


class AudioVideoTab(QWidget):
    def __init__(self, parent):
        super(AudioVideoTab, self).__init__(parent)
        self.parent = parent
        self.name = 'AudioVideo'

        self.defaultStr = self.tr('Default')
        self.DisableStream = self.tr('Disable')

        self.formats = config.video_formats
        frequency_values = [self.defaultStr] + config.video_frequency_values
        bitrate_values = [self.defaultStr] + config.video_bitrate_values

        rotation_options = [
                self.tr('None'),
                '90 ' + self.tr('clockwise'),
                '90 ' + self.tr('clockwise') + ' + ' + self.tr('vertical flip'),
                '90 ' + self.tr('counter clockwise'),
                '90 ' + self.tr('counter clockwise') +
                ' + ' + self.tr('vertical flip'),
                '180',
                self.tr('horizontal flip'),
                self.tr('vertical flip')
                ]

        digits_validator = QRegExpValidator(QRegExp(r'[1-9]\d*'), self)
        digits_validator_wzero = QRegExpValidator(QRegExp(r'\d*'), self)
        digits_validator_minus = QRegExpValidator(QRegExp(r'(-1|[1-9]\d*)'), self)
        time_validator = QRegExpValidator(
                QRegExp(r'\d{1,2}:\d{1,2}:\d{1,2}\.\d+'), self)

        converttoQL = QLabel(self.tr('Convert to:'))
        self.extQCB = QComboBox()
        self.extQCB.setMinimumWidth(100)
        vidcodecQL = QLabel('Video codec:')
        self.vidcodecQCB = QComboBox()
        self.vidcodecQCB.setMinimumWidth(110)
        audcodecQL = QLabel('Audio codec:')
        self.audcodecQCB = QComboBox()
        self.audcodecQCB.setMinimumWidth(110)

        hlayout1 = utils.add_to_layout(
                'h', converttoQL, self.extQCB, QSpacerItem(180, 20),
                vidcodecQL, self.vidcodecQCB, audcodecQL, self.audcodecQCB)

        commandQL = QLabel(self.tr('Command:'))
        self.commandQLE = QLineEdit()
        hlayout2 = utils.add_to_layout(
                'h', commandQL, self.commandQLE)
        self.widthQLE = utils.create_LineEdit(
                (70, 16777215), digits_validator_minus, 4)
        self.heightQLE = utils.create_LineEdit(
                (70, 16777215), digits_validator_minus, 4)
        self.aspect1QLE = utils.create_LineEdit(
                (50, 16777215), digits_validator, 2)
        self.aspect2QLE = utils.create_LineEdit(
                (50, 16777215), digits_validator, 2)
        self.frameQLE = utils.create_LineEdit(
                (120, 16777215), digits_validator, 4)
        self.bitrateQLE = utils.create_LineEdit(
                (130, 16777215), digits_validator, 6)


        self.preserveaspectQChB = QCheckBox(self.tr("Preserve aspect ratio"))
        self.preservesizeQChB = QCheckBox(self.tr("Preserve video size"))

        self.freqQCB = QComboBox()
        self.freqQCB.addItems(frequency_values)
        self.chan1QRB = QRadioButton('1')
        self.chan1QRB.setMaximumSize(QSize(51, 16777215))
        self.chan2QRB = QRadioButton('2')
        self.chan2QRB.setMaximumSize(QSize(51, 16777215))
        self.group = QButtonGroup()
        self.group.addButton(self.chan1QRB)
        self.group.addButton(self.chan2QRB)
        spcr1 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        spcr2 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.audbitrateQCB = QComboBox()
        self.audbitrateQCB.addItems(bitrate_values)
        self.threadsQLE = utils.create_LineEdit(
                (50, 16777215), digits_validator_wzero, 1)

        time_format = " (hh:mm:ss):"
        self.beginQLE = utils.create_LineEdit(None, time_validator, None)
        self.durationQLE = utils.create_LineEdit(None, time_validator, None)

        self.embedQLE = QLineEdit()
        self.embedQTB = QToolButton()
        self.embedQTB.setText("...")

        self.rotateQCB = QComboBox()
        self.rotateQCB.addItems(rotation_options)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        hlayout3 = utils.add_to_layout('h', line)

        final_layout = utils.add_to_layout(
                'v', hlayout1, hlayout2, hlayout3)
        self.setLayout(final_layout)

    def resize_parent(self):
        self.parent.setMinimumSize(self.parent.sizeHint())
        self.parent.resize(self.parent.sizeHint())

    def clear(self):
        lines = [
                self.commandQLE, self.widthQLE, self.heightQLE,
                self.aspect1QLE, self.aspect2QLE, self.frameQLE,
                self.bitrateQLE, self.threadsQLE, self.beginQLE,
                self.embedQLE, self.durationQLE
                ]
        for i in lines:
            i.clear()

        self.vidcodecQCB.setCurrentIndex(0)
        self.audcodecQCB.setCurrentIndex(0)
        self.freqQCB.setCurrentIndex(0)
        self.audbitrateQCB.setCurrentIndex(0)
        self.rotateQCB.setCurrentIndex(0)
        self.preserveaspectQChB.setChecked(False)
        self.preservesizeQChB.setChecked(False)
        self.group.setExclusive(False)
        self.chan1QRB.setChecked(False)
        self.chan2QRB.setChecked(False)
        self.group.setExclusive(True)


    def fill_video_comboboxes(self, vcodecs, acodecs, extraformats):
        self.vidcodecQCB.clear()
        self.audcodecQCB.clear()
        self.extQCB.clear()
        self.vidcodecQCB.addItems([self.defaultStr, self.DisableStream] + vcodecs)
        self.audcodecQCB.addItems([self.defaultStr, self.DisableStream] + acodecs)
        self.extQCB.addItems(sorted(self.formats + extraformats))

    def ok_to_continue(self):
        return True
        
    def set_default_command(self):
        self.clear()
        self.commandQLE.setText(self.parent.default_command)

