"""Constantes d'environnement pour l'application."""

from enum import Enum, auto


class Environment(Enum):
    """Environnements possibles pour l'application."""

    TEST = auto()
    DEVELOPMENT = auto()
    STAGING = auto()
    PRODUCTION = auto()

    @classmethod
    def from_string(cls, env_str: str) -> "Environment":
        """
        Convertit une chaîne en environnement.

        Args:
            env_str: Chaîne à convertir (dev, staging, prod)

        Returns:
            Environment correspondant

        Raises:
            ValueError: Si la chaîne n'est pas valide
        """
        env_map = {
            "dev": cls.DEVELOPMENT,
            "development": cls.DEVELOPMENT,
            "staging": cls.STAGING,
            "prod": cls.PRODUCTION,
            "production": cls.PRODUCTION,
        }

        env_str = env_str.lower()
        if env_str not in env_map:
            raise ValueError(
                f"Invalid environment: {env_str}. "
                f"Must be one of: {', '.join(env_map.keys())}"
            )

        return env_map[env_str]

    def __str__(self) -> str:
        """Retourne une représentation string de l'environnement."""
        return self.name.lower()

    @property
    def is_development(self) -> bool:
        """Retourne True si l'environnement est development."""
        return self == self.DEVELOPMENT

    @property
    def is_staging(self) -> bool:
        """Retourne True si l'environnement est staging."""
        return self == self.STAGING

    @property
    def is_production(self) -> bool:
        """Retourne True si l'environnement est production."""
        return self == self.PRODUCTION
