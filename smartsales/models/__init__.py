from sqlalchemy.orm import registry

# Este é o único e centralizado table_registry
table_registry = registry()

# Importe seus modelos aqui para que eles sejam registrados no table_registry.
# Isso garante que table_registry.metadata conheça todas as suas tabelas.
from smartsales.models import auth # noqa: E402
from smartsales.models import clients  # noqa: E402
from smartsales.models import products  # noqa: E402
from smartsales.models import orders  # noqa: E402