from src.pql.handlers.rest_api_handler import RestApiHandler


class Config:
    DEBUG = False
    TESTING = False

    PQL_HANDLERS = {"http.get": RestApiHandler, "http.post": RestApiHandler}

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
