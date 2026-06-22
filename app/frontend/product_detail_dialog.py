"""Read-only product detail popup with product image and company logo.

Opened by double-clicking a row in the inventory table. Images are matched on
disk by barcode (product image) and company name (company logo) from two folders
configured in ``.env`` (see :mod:`app.backend.config`).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

from app.backend.models import INVENTORY_FIELDS, Product
from app.frontend.i18n import fa
from app.frontend.utils_fa import display
from app.frontend.widgets.common import find_image

_IMAGE_BOX = 160


class ProductDetailDialog(QDialog):
    """Show every field of a product plus its image and company logo."""

    def __init__(
        self,
        parent=None,
        *,
        product: Product,
        product_images_dir: Path | str | None = None,
        company_logos_dir: Path | str | None = None,
        writable: bool = False,
    ):
        super().__init__(parent)
        self._product = product
        self._product_images_dir = product_images_dir
        self._company_logos_dir = company_logos_dir
        self._writable = writable
        self._edit_requested = False
        self.setWindowTitle(fa.TITLE_PRODUCT_DETAIL)
        self.setMinimumWidth(560)
        self._build()

    @property
    def edit_requested(self) -> bool:
        return self._edit_requested

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setSpacing(14)

        top = QHBoxLayout()
        top.setSpacing(18)

        # Field grid (right side in RTL).
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignRight | Qt.AlignTop)
        for field in INVENTORY_FIELDS:
            value = QLabel(display(getattr(self._product, field)))
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            form.addRow(fa.COLUMN_LABELS[field], value)
        top.addLayout(form, 1)

        # Images column.
        images = QVBoxLayout()
        images.setSpacing(12)
        images.addWidget(
            self._image_block(
                fa.LBL_PRODUCT_IMAGE,
                find_image(self._product_images_dir, self._product.barcode),
            )
        )
        images.addWidget(
            self._image_block(
                fa.LBL_COMPANY_LOGO,
                find_image(self._company_logos_dir, self._product.company),
            )
        )
        images.addStretch(1)
        top.addLayout(images)

        outer.addLayout(top)

        buttons = QDialogButtonBox()
        if self._writable:
            edit = buttons.addButton(fa.BTN_EDIT, QDialogButtonBox.ActionRole)
            edit.clicked.connect(self._on_edit)
        close = buttons.addButton(fa.BTN_CLOSE, QDialogButtonBox.RejectRole)
        close.clicked.connect(self.reject)
        outer.addWidget(buttons)

    def _image_block(self, caption: str, path: Path | None) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(6)

        title = QLabel(caption)
        title.setObjectName("subtitle")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        pic = QLabel()
        pic.setAlignment(Qt.AlignCenter)
        pic.setFixedSize(_IMAGE_BOX, _IMAGE_BOX)
        pixmap = QPixmap(str(path)) if path else QPixmap()
        if not pixmap.isNull():
            pic.setPixmap(
                pixmap.scaled(
                    _IMAGE_BOX,
                    _IMAGE_BOX,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            pic.setText(fa.MSG_NO_IMAGE)
            pic.setStyleSheet("color: #90a4ae; border: 1px dashed #cfd8dc;")
        lay.addWidget(pic)
        return frame

    def _on_edit(self) -> None:
        self._edit_requested = True
        self.accept()
