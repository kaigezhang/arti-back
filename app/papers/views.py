import os
from flask import Blueprint, request, jsonify
from flask_jwt import current_identity, jwt_required
from flask_apispec import use_kwargs, marshal_with
import pdfx
from sqlalchemy.exc import IntegrityError

from .models import Paper
from app.user.models import User
from .serializers import paper_schema, papers_schema
from services.pdf2html import pdf2html, extract_html_css
from marshmallow import fields
from app.exceptions import InvalidUsage
from app.config import PDF_DIR

blueprint = Blueprint('papers', __name__)


def check_if_exist(data):
    if data:
        if isinstance(data, list):
            return ', '.join(data)
        return data
    return None


def process_pdf(pdf_path):
    pdf = pdfx.PDFx(pdf_path)
    metadata = pdf.get_metadata()
    # print(type(metadata))
    # print(metadata['dc']['creator'])
    # print(type(metadata['dc']['creator']))
    # print(metadata['dc']['publisher'])
    # print(metadata['dc']['identifier'])
    # print(' '.join(metadata['dc']['subject']))
    args = dict()
    args['author'] = check_if_exist(metadata['dc']['creator'])
    args['publisher'] = check_if_exist(metadata['dc']['publisher'])
    args['doi'] = check_if_exist(metadata['dc']['identifier'])
    args['title'] = check_if_exist(metadata['dc']['title']['x-default'])
    args['subject'] = check_if_exist(metadata['dc']['subject'])
    args['pages'] = check_if_exist(metadata['Pages'])
    # print(type(args))
    return args


@blueprint.route('/api/papers', methods=['GET'])
# @jwt_required()
@use_kwargs({
    'owner': fields.Str(),
    'collected': fields.Str(),
    'limit': fields.Int(),
    'offset': fields.Int()
})
@marshal_with(papers_schema)
def get_papers(owner=None, collected=None, limit=20, offset=0):
    res = Paper.query

    if owner:
        # res = res.filter_by(owner=owner.profile)
        res = res.join(Paper.owner).join(User).filer(User.usernmae == owner)
    if collected:
        res = res.join(Paper.collectors).filter(User.username == collected)
    return res.offset(offset).limit(limit).all()


@blueprint.route('/api/papers', methods=['POST'])
@jwt_required()
# @marshal_with(papers_schema)
def upload_papers():
    if os.path.isdir(PDF_DIR):
        files = request.files.getlist('file')
        papers = []
        for file in files:
            try:
                filename = file.filename
                pdf_path = PDF_DIR + filename
                file.save(pdf_path)
                # 将存储好的pdf转换成html
                res = pdf2html(pdf_path)
                if res:
                    raise InvalidUsage.paper_not_processed()
                else:
                    args = process_pdf(pdf_path)
                    args['owner'] = current_identity.profile
                    args['filename'] = filename
                    paper = make_paper(owner=current_identity.profile)
                    papers.append(paper)
            except Exception:
                raise InvalidUsage.unknown_error()
    return papers


# @blueprint.route('/api/papers', methods=['POST'])
# @jwt_required()
# @blueprint.route('/api/papers/creates', methods=['POST'])
# @use_kwargs(paper_schema)
@marshal_with(paper_schema)
def make_paper():
    try:
        paper = Paper(
            owner=args['owner'],
            filename=args['filename'],
            author=args['author'],
            publisher=args['publisher'],
            doi=args['doi'],
            title=args['title'],
            subject=args['subject'],
            pages=args['pages']
        ).save()
    except IntegrityError:
        db.session.rollback()
        raise InvalidUsage.paper_not_saved()
    return paper


@blueprint.route('/api/papers/<id>', methods=['GET'])
# @jwt_required()
def get_paper(id):
    paper = Paper.query.get(id)
    if not paper:
        raise InvalidUsage.paper_not_found()
    res = extract_html_css(paper.filename)
    return jsonify({
        'res': res
    })


@blueprint.route('/api/papers/<id>', methods=['DELETE'])
@jwt_required()
def delete_paper(id):
    paper = Paper.query.filter_by(id=id, owner_id=current_identity.profile.id)
    if not paper:
        raise InvalidUsage.paper_not_found()
    paper.delete()
    return '', 200


@blueprint.route('/api/papers/<id>/collect', methods=['POST'])
@jwt_required()
@marshal_with(paper_schema)
def collect_paper(id, profile):
    paper = Paper.query.get(id)
    if not paper:
        raise InvalidUsage.paper_not_found()
    paper.collect(profile)
    paper.save()
    return paper


@blueprint.route('/api/papers/<id>/collect', methods=['DELETE'])
@jwt_required()
@marshal_with(paper_schema)
def uncollect_paper(id, profile):
    paper = Paper.query.get(id)
    if not paper:
        raise InvalidUsage.paper_not_found()
    paper.uncollect(profile)
    paper.save()
    return paper
