from pathlib import Path

from singleton import Singleton
import utilities
import settings

class Paths(Singleton):
    def __init__(self):
        self.base_path:Path = utilities.base_dir_path()
        self.script_path: Path = self.base_path / "scripts"
        self.userscript_path: Path = self.base_path / "userscripts"

        self.setting_model_path = (
            Path(settings.current.interrogator_model_dir)
            if settings.current.interrogator_model_dir
            else None
        )

        if self.setting_model_path is not None and not self.setting_model_path.is_dir():
            self.setting_model_path.mkdir(parents=True)

        self.models_path = (
            self.setting_model_path
            if self.setting_model_path is not None
            else utilities.base_dir_path() / "models"
        )

paths = Paths()