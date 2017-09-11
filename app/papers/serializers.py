from marshmallow import Schema, fields, pre_load, post_dump
from app.profile.serializers import ProfileSchema


class PaperSchema(Schema):
    id = fields.Int(dump_only=True)
    filename = fields.Str()
    pages = fields.Int()
    title = fields.Str()
    author = fields.Str()
    doi = fields.Str()
    publisher = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime(dump_only=True)
    owner = fields.Nested(ProfileSchema)
    # pdf_path = fields.Str(dump_only=True)
    # html_path = fields.Str(dump_only=True)

    @pre_load
    def make_paper(self, data):
        print(data)
        # data = data
        return data

    @post_dump
    def dump_paper(self, data):
        return {
            'paper': data
        }

    class Meta:
        strict = True


class PapersSchema(PaperSchema):
    @post_dump
    def dump_paper(self, data):
        return data

    @post_dump(pass_many=True)
    def dump_papers(self, data, many):
        return {
            'papers': data
        }


paper_schema = PaperSchema()
papers_schema = PapersSchema(many=True)
