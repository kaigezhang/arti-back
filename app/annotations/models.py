import datetime as dt
from flask_jwt import current_identity

from app.database import (Model, SurrogatePK, db, Column, reference_col, relationship)
from app.profile.models import UserProfile

favoriter_assoc = db.Table(
    'favoriter_assoc',
    db.Column('favoriter', db.Integer, db.ForeignKey('userprofile.id')),
    db.Column('favorited_annotation', db.Integer, db.ForeignKey('annotation.id'))
)

tag_assoc = db.Table(
    'tag_assoc',
    db.Column('tag', db.Integer, db.ForeignKey('tags.id')),
    db.Column('annotation', db.Integer, db.ForeignKey('annotation.id'))
)


class Tags(Model):
    __tablename__='tags'
    id = db.Column(db.Integer, primary_key=True)
    tagname = db.Column(db.String(100))

    def __init__(self, tagname):
        db.Model.__init__(self, tagname=tagname)

    def __repr__(self):
        return self.tagname


class Comment(Model, SurrogatePK):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    body = Column(db.Text)
    createAt = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updatedAt = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    author_id = reference_col('userprofile', nullable=False)
    author = relationship(
        'UserProfile',
        backref=db.backref('comments')
    )
    annotation_id = reference_col('annotation', nullable=True)

    def __int__(self, annotation, author, body, **kwargs):
        db.Model.__init__(self, annotation=annotation, author=author, body=body, **kwargs)


class Annotation(Model, SurrogatePK):
    __tablename__ = 'annotation'
    # 转换成uuid的形式
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    position = db.Column(db.String(100))
    body = Column(db.Text)
    public = Column(db.Boolean, default=True)
    createdAt = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updatedAt = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    author_id = reference_col('userprofile', nullable=False)
    author = relationship(
        'UserProfile',
        backref=db.backref('annotations')
    )
    paper_id = reference_col('papers', nullable=True)
    paper = relationship(
        'Paper',
        backref=db.backref('annotations')
    )

    favoriters = relationship(
        'UserProfile',
        secondary=favoriter_assoc,
        backref='favorites',
        lazy='dynamic'
    )
    tagList = relationship(
        'Tags',
        secondary=tag_assoc,
        backref='annotations'
    )
    comments = relationship(
        'Comment',
        backref=db.backref('annotation'),
        lazy='dynamic'
    )

    def __init__(self, author, body, position, paper, **kwargs):
        db.Model.__init__(self, author=author, paper=paper, body=body, position=position, **kwargs)

    def favorite(self, profile):
        if not self.is_favorite(profile):
            self.favoriters.append(profile)
            return True
        return False

    def unfavorite(self, profile):
        if self.is_favorite(profile):
            self.favoriters.remove(profile)
            return True
        return False

    def is_favorite(self, profile):
        return bool(
            self.query.filter(favoriter_assoc.c.favoriter == profile.id).count()
        )

    def add_tag(self, tag):
        if tag not in self.tagList:
            self.tagList.append(tag)
            return True
        return False

    def remove_tag(self, tag):
        if tag in self.tagList:
            self.tagList.remove(tag)
            return True
        return False

    @property
    def favoritesCounts(self):
        return len(self.favoriters)

    @property
    def favorited(self):
        if current_identity:
            profile = current_identity.profile
            return self.query.join(Annotation.favoriters).filter(UserProfile.id == profile.id).count() == 1
        return False

