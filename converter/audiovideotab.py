from PyQt5.QtWidgets import (
        QWidget, QComboBox, QLineEdit, QLabel,
        QSpacerItem, QFrame, QToolButton
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
        converttoQL = QLabel(self.tr('Convert to:'))
        self.extQCB = QComboBox()
        self.extQCB.setMinimumWidth(100)

        hlayout1 = utils.add_to_layout('h', converttoQL, self.extQCB, QSpacerItem(180, 20))

        self.commandQLE = QLineEdit()

        self.embedQLE = QLineEdit()
        self.embedQTB = QToolButton()
        self.embedQTB.setText("...")

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        hlayout3 = utils.add_to_layout('h', line)

        final_layout = utils.add_to_layout(
                'v', hlayout1, hlayout3)
        self.setLayout(final_layout)

    def clear(self):
        lines = [self.commandQLE, self.embedQLE]
        for i in lines:
            i.clear()

    def fill_video_comboboxes(self, extraformats):
        self.extQCB.clear()
        self.extQCB.addItems(sorted(self.formats + extraformats))

    def ok_to_continue(self):
        return True
        
    def set_default_command(self):
        self.clear()
        self.commandQLE.setText(self.parent.default_command)

