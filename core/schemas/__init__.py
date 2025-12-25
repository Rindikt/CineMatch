from .actors import ActorBase, ActorRead, ActorCreate, ActorLight
from .movies import MovieCreate, MovieBase, MovieRead, MovieActorRead, MovieGenreRead, MovieLight, MovieProgressRead
from .genres import GenreBase, GenreRead

ActorBase.model_rebuild()
GenreBase.model_rebuild()
MovieBase.model_rebuild()
MovieRead.model_rebuild()
GenreRead.model_rebuild()
ActorLight.model_rebuild()
MovieActorRead.model_rebuild()
MovieGenreRead.model_rebuild()
ActorRead.model_rebuild()
MovieLight.model_rebuild()
MovieProgressRead.model_rebuild()
