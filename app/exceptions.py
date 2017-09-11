from flask import jsonify


def template(data, code=500):
    return {'message': {'errors': {'body': data}}, 'status_code': code}


USER_NOT_FOUND = template(['User not found'], code=404)
USER_ALREADY_REGISTERED = template(['User already registered'], code=422)
UNKNOWN_ERROR = template([], code=500)
ARTICLE_NOT_FOUND = template(['Article not found'], code=404)
COMMENT_NOT_OWNED = template(['Not your article'], code=422)
ANNOTATION_NOT_FOUND = template(['Annotation not found'], code=404)
PAPER_NOT_PROCESSED = template(['Paper cannot be processed'], code=500)
PAPER_NOT_FOUND = template(['Paper not found'], code=404)
PAPER_NOT_OPEN = template(['Paper cannot open'], code=404)
PAPER_NOT_SAVED = template(['Paper cannot be saved in database'], code=422)


class InvalidUsage(Exception):
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_json(self):
        rv = self.message
        return jsonify(rv)

    @classmethod
    def user_not_found(cls):
        return cls(**USER_NOT_FOUND)

    @classmethod
    def user_already_registered(cls):
        return cls(**USER_ALREADY_REGISTERED)

    @classmethod
    def unknown_error(cls):
        return cls(**UNKNOWN_ERROR)

    @classmethod
    def article_not_found(cls):
        return cls(**ARTICLE_NOT_FOUND)

    @classmethod
    def comment_not_owned(cls):
        return cls(**COMMENT_NOT_OWNED)

    @classmethod
    def annotation_not_found(cls):
        return cls(**ANNOTATION_NOT_FOUND)

    @classmethod
    def paper_not_found(cls):
        return cls(**PAPER_NOT_FOUND)

    @classmethod
    def paper_not_processed(cls):
        return cls(**PAPER_NOT_PROCESSED)

    @classmethod
    def paper_not_open(cls):
        return cls(**PAPER_NOT_OPEN)

    @classmethod
    def paper_not_saved(cls):
        return cls(**PAPER_NOT_SAVED)
