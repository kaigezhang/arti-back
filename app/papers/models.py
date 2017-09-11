import datetime as dt
from app.database import Column, Model, SurrogatePK, db, reference_col, relationship
from app.config import PDF_DIR, HTML_DIR
from app.profile.models import UserProfile

collector_assoc = db.Table(
    'collector_assoc',
    db.Column('collector', db.Integer, db.ForeignKey('userprofile.id')),
    db.Column('collected_papers', db.Integer, db.ForeignKey('papers.id'))
)


class Paper(SurrogatePK, Model):
    __tablename__ = 'papers'

    id = Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = reference_col('userprofile', nullable=True)
    owner = relationship(
        'UserProfile',
        backref=db.backref('papers')
    )
    collectors = relationship(
        'UserProfile',
        secondary=collector_assoc,
        backref='collects',
        lazy='dynamic'
    )
    filename = Column(db.String(100), unique=True, nullable=False)
    pages = Column(db.Integer, nullable=True)
    title = Column(db.String(200), nullable=True)
    author = Column(db.Text, nullable=True)
    doi = Column(db.String(30), nullable=True)
    publisher = Column(db.String(100), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, owner, filename, pages, title, author, doi, publisher, **kwargs):
        db.Model.__init__(
            self,
            owner=owner,
            filename=filename,
            pages=pages,
            title=title,
            author=author,
            doi=doi,
            publisher=publisher,
            **kwargs
        )

    def __repr__(self):
        return '<Paper({filename!r})'.format(filename=self.filename)

    def collect(self, profile):
        if not self.is_collect(profile):
            self.collectors.append(profile)
            return True
        return False

    def uncollect(self, profile):
        if self.is_collect(profile):
            self.collectors.remove(profile)
            return True
        return False

    def is_collect(self, profile):
        return bool(self.query.filter(collector_assoc.c.collector == profile.id).count())

    @property
    def pdf_path(self):
        return PDF_DIR + self.filename

    @property
    def html_path(self):
        return HTML_DIR + self.filename
