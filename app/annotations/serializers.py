from marshmallow import Schema, fields, pre_load, post_dump
from app.profile.serializers import ProfileSchema
from app.papers.serializers import PaperSchema


class TagSchema(Schema):
    tagname = fields.Str()


class AnnotationSchema(Schema):
    id = fields.Int(dump_only=True)
    score = fields.Int()
    position = fields.Str()
    body = fields.Str()
    createdAt = fields.DateTime()
    updatedAt = fields.DateTime(dump_only=True)
    author = fields.Nested(ProfileSchema)
    paper = fields.Nested(PaperSchema)
    annotation = fields.Nested('self', exclude=('annotation',), default=True, load_only=True)
    tagList = fields.List(fields.Str())
    favoritesCount = fields.Int(dump_only=True)
    favorited = fields.Bool(dump_only=True)

    @pre_load
    def make_annotation(self, data):
        return data['annotation']

    @post_dump
    def dump_annotation(self, data):
        if 'author' in data:
            data['author'] = data['author']['profile']
        return {'annotation': data}

    class Meta:
        strict = True


class AnnotationsSchema(AnnotationSchema):

    @post_dump
    def dump_annotation(self, data):
        if 'author' in data:
            data['author'] = data['author']['profile']
        return data

    @post_dump(pass_many=True)
    def dump_annotations(self, data, many):
        return {
            'annotations': data,
            'annotationsCount': len(data)
        }


class CommentSchema(Schema):
    createdAt = fields.DateTime()
    body = fields.Str()
    updatedAt = fields.DateTime(dump_only=True)
    author = fields.Nested(ProfileSchema)
    id = fields.Int()

    comment = fields.Nested('self', exclude=('comment',), default=True, load_only=True)

    @pre_load
    def make_comment(self, data):
        return data['comment']

    @post_dump
    def dump_comment(self, data):
        return {'comment': data}

    class Meta:
        strict = True


class CommentsSchema(CommentSchema):

    @post_dump
    def dump_comment(self, data):
        return data

    @post_dump(pass_many=True)
    def make_comment(self, data, many):
        return {
            'comments': data
        }


annotation_schema = AnnotationSchema()
annotations_schema = AnnotationsSchema(many=True)
comment_schema = CommentSchema()
comments_schema = CommentsSchema(many=True)
