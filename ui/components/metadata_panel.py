import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QTextEdit, QCheckBox, QPushButton, QGroupBox
)
from core.variant_models import MetadataConfig

class MetadataPanel(QGroupBox):
    def __init__(self, title: str = "Metadata Editor", parent=None):
        super().__init__(title, parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(10)

        grid = QGridLayout()
        grid.setSpacing(8)

        # Title
        grid.addWidget(QLabel("Title:"), 0, 0)
        self.input_title = QLineEdit(self)
        self.input_title.setPlaceholderText("e.g. Summer Vacation Montage")
        grid.addWidget(self.input_title, 0, 1)

        # Author / Artist
        grid.addWidget(QLabel("Author / Artist:"), 0, 2)
        self.input_author = QLineEdit(self)
        self.input_author.setPlaceholderText("e.g. John Doe")
        grid.addWidget(self.input_author, 0, 3)

        # Creator
        grid.addWidget(QLabel("Creator / Studio:"), 1, 0)
        self.input_creator = QLineEdit(self)
        self.input_creator.setPlaceholderText("e.g. Acme Productions")
        grid.addWidget(self.input_creator, 1, 1)

        # Copyright
        grid.addWidget(QLabel("Copyright Notice:"), 1, 2)
        self.input_copyright = QLineEdit(self)
        self.input_copyright.setPlaceholderText("e.g. © 2026 Acme Studios. All Rights Reserved.")
        grid.addWidget(self.input_copyright, 1, 3)

        # Software / Encoder
        grid.addWidget(QLabel("Software / Encoder:"), 2, 0)
        self.input_software = QLineEdit(self)
        self.input_software.setText("Media Variant & Metadata Studio")
        grid.addWidget(self.input_software, 2, 1)

        # Creation Date with Now button
        grid.addWidget(QLabel("Creation Date:"), 2, 2)
        row_date = QHBoxLayout()
        self.input_date = QLineEdit(self)
        self.input_date.setPlaceholderText("YYYY-MM-DD HH:MM:SS")
        self.btn_date_now = QPushButton("Set Now", self)
        self.btn_date_now.clicked.connect(self.set_current_date)
        row_date.addWidget(self.input_date)
        row_date.addWidget(self.btn_date_now)
        grid.addLayout(row_date, 2, 3)

        # Keywords / Tags
        grid.addWidget(QLabel("Keywords / Tags:"), 3, 0)
        self.input_keywords = QLineEdit(self)
        self.input_keywords.setPlaceholderText("e.g. 4k, travel, cinematic, nature")
        grid.addWidget(self.input_keywords, 3, 1, 1, 3)

        layout.addLayout(grid)

        # Description / Comment
        lbl_desc = QLabel("Description / Comments:")
        self.input_description = QTextEdit(self)
        self.input_description.setPlaceholderText("Detailed description or workflow notes...")
        self.input_description.setMaximumHeight(70)
        layout.addWidget(lbl_desc)
        layout.addWidget(self.input_description)

        # Options
        row_opts = QHBoxLayout()
        self.chk_strip = QCheckBox("Strip all pre-existing metadata tags before embedding", self)
        self.chk_strip.setChecked(False)
        row_opts.addWidget(self.chk_strip)
        row_opts.addStretch()

        self.btn_clear = QPushButton("Clear Fields", self)
        self.btn_clear.clicked.connect(self.clear_fields)
        row_opts.addWidget(self.btn_clear)

        layout.addLayout(row_opts)

    def set_current_date(self):
        self.input_date.setText(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def clear_fields(self):
        self.input_title.clear()
        self.input_author.clear()
        self.input_creator.clear()
        self.input_copyright.clear()
        self.input_software.setText("Media Variant & Metadata Studio")
        self.input_date.clear()
        self.input_keywords.clear()
        self.input_description.clear()
        self.chk_strip.setChecked(False)

    def get_metadata_config(self) -> MetadataConfig:
        return MetadataConfig(
            title=self.input_title.text().strip(),
            author=self.input_author.text().strip(),
            creator=self.input_creator.text().strip(),
            description=self.input_description.toPlainText().strip(),
            copyright=self.input_copyright.text().strip(),
            software=self.input_software.text().strip(),
            creation_date=self.input_date.text().strip(),
            keywords=self.input_keywords.text().strip(),
            comment=self.input_description.toPlainText().strip(),
            strip_all_first=self.chk_strip.isChecked()
        )

    def set_metadata_config(self, meta: MetadataConfig):
        self.input_title.setText(meta.title)
        self.input_author.setText(meta.author)
        self.input_creator.setText(meta.creator)
        self.input_description.setPlainText(meta.description)
        self.input_copyright.setText(meta.copyright)
        self.input_software.setText(meta.software)
        self.input_date.setText(meta.creation_date)
        self.input_keywords.setText(meta.keywords)
        self.chk_strip.setChecked(meta.strip_all_first)
