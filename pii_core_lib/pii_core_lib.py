"""Composition root: ``PiiCoreLib(CoreLib)``.

Exposes one attribute — ``self.service`` — that is a ready-to-use
:class:`PiiService` instance. The service is stateless so a single
process-wide instance is fine and there is nothing else this class
needs to own. Host apps that prefer dependency injection can ignore
the composition root and instantiate :class:`PiiService` directly.

Reads two optional knobs from ``core_lib.pii``:

* ``strict_default`` — bool; default-applied to every call when the
  caller doesn't pass ``strict`` explicitly. **Currently informational
  only** — `:meth:`PiiService.scrub` / `:meth:`PiiService.validate`
  default ``strict=False`` at the API level. A future change can wire
  this through if a host app needs a global override.
* ``default_context`` — string; reserved for a future "ambient
  context" feature.
"""
from __future__ import annotations

from typing import Any, Optional

from omegaconf import DictConfig

from core_lib.core_lib import CoreLib

from pii_core_lib.data_layers.service.pii_service import PiiService


class PiiCoreLib(CoreLib):
    """Hosts a single :class:`PiiService` instance.

    Args:
        conf: Optional Hydra ``DictConfig``. The package reads
            ``core_lib.pii.*`` knobs at construction time but the
            service itself is stateless and takes no per-instance
            config today.
    """

    def __init__(self, conf: Optional[DictConfig] = None):
        super().__init__()
        self.config = conf
        self.service = PiiService()
