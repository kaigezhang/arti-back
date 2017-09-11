import datetime as dt

from flask import Blueprint, jsonify
from flask_apispec import use_kwargs, marshal_with
from flask_jwt import jwt_required, current_identity
from marshmallow import fields

from .models import Annotation, Tags, Comment
from .serializers import (annotation_schema, annotations_schema, comments_schema, comment_schema)
from app.exceptions import InvalidUsage
from app.extensions import cors
from app.user.models import User
from app.papers.models import Paper
from app.utils import jwt_optional

blueprint = Blueprint('annotations', __name__)


@blueprint.route('/api/annotations', methods=['GET'])
@jwt_optional()
@use_kwargs({
    'tag': fields.Str(),
    'author': fields.Str(),
    'paper': fields.Str(),
    'favorited': fields.Str(),
    'limit': fields.Int(),
    'offset': fields.Int()
})
@marshal_with(annotations_schema)
def get_annotations(tag=None, author=None, paper=None, favorited=None, limit=20, offset=0):
    res = Annotation.query
    # 需要补充了解，join在orm中的应用
    if tag:
        res = res.filter(Annotation.tagList.any(Tags.tagname == tag))
    if author:
        res = res.join(Annotation.author).join(User).filter(User.username == author)
    if paper:
        res = res.join(Annotation.paper).join(Paper).filter(Paper.id == paper.id)
    if favorited:
        res = res.join(Annotation.favoriters).filter(User.username == favorited)
    return res.offset(offset).limit(limit).all()


@blueprint.route('/api/annotations', methods=['POST'])
@jwt_required()
@use_kwargs(annotation_schema)
@marshal_with(annotation_schema)
def make_annotation(body, tagList, paper):
    annotation = Annotation(paper=paper, body=body, tagList=tagList, author=current_identity.profile)
    if tagList is not None:
        for tag in tagList:
            mtag = Tags.query.filter_by(tagname=tag).first()
            if not mtag:
                mtag = Tags(tag)
                mtag.save()
            annotation.add_tag(mtag)
    annotation.save()
    return annotation


@blueprint.route('/api/annotations/<id>', methods=['PUT'])
@jwt_required()
@use_kwargs(annotation_schema)
@marshal_with(annotation_schema)
def update_annotation(id, **kwargs):
    annotation = Annotation.query.filter_by(id=id, author_id=current_identity.profile.id).first()
    if not annotation:
        raise InvalidUsage.annotation_not_found()
    annotation.update(updatedAt=dt.datetime.utcnow, **kwargs)
    annotation.save()
    return annotation


@blueprint.route('/api/annotations/<id>', methods=['DELETE'])
@jwt_required()
def delete_annotation(id):
    annotation = Annotation.query.filter_by(id=id, author_id=current_identity.profile.id).first()
    if not annotation:
        raise InvalidUsage.annotation_not_found()
    annotation.delete()
    return '', 200


@blueprint.route('/api/annotations/<id>', methods=['GET'])
@jwt_optional()
@marshal_with(annotation_schema)
def get_annotation(id):
    annotation = Annotation.query.get(id)
    if not annotation:
        raise InvalidUsage.annotation_not_found()
    return annotation


@blueprint.route('/api/annotations/<id>/favorite', methods=['POST'])
@jwt_required()
@marshal_with(annotation_schema)
def favorite_an_annotation(id):
    profile = current_identity.profile
    annotation = Annotation.query.get(id)
    if not annotation:
        raise InvalidUsage.annotation_not_found()
    annotation.favorite(profile)
    annotation.save()
    return annotation


@blueprint.route('/api/annotations/<id>/favorite', methods=['DELETE'])
@jwt_required()
@marshal_with(annotation_schema)
def unfavorite_an_annotation(id):
    profile = current_identity.profile
    annotation = Annotation.query.get(id)
    if not annotation:
        raise InvalidUsage.annotation_not_found()
    annotation.unfavorite(profile)
    annotation.save()
    return annotation


@blueprint.route('/api/annotations/feed', methods=['GET'])
@jwt_required()
@use_kwargs({
    'limit': 20,
    'offset': 0
})
@marshal_with(annotations_schema)
def annotations_feed(limit=20, offset=0):
    return Annotation.query.join(current_identity.profile.follows).order_by(Annotation.createdAt.desc()).offset(offset).limit(limit).all()

# @blueprint.route('/api/annotations', methods=['GET'])

# tags


@blueprint.route('/api/tags', methods=['GET'])
def get_tags():
    return jsonify({
        'tags': [
            tag.tagname for tag in Tags.query.all()
        ]
    })


# comment
@blueprint.route('/api/annotations/<id>/comments', methods=['GET'])
@marshal_with(comments_schema)
def get_comments(id):
    annotation = Annotation.query.get(id)
    if not annotation:
        raise InvalidUsage.annotation_not_found()
    return annotation.comments


@blueprint.route('/api/annotations/<id>/comments', methods=['POST'])
@jwt_required()
@use_kwargs(comment_schema)
@marshal_with(comment_schema)
def make_comment_on_annotation(id, body, **kwargs):
    annotation = Annotation.query.get(id)
    if not annotation:
        raise InvalidUsage.annotation_not_found()
    comment = Comment(annotation, current_identity.profile, body, **kwargs)
    comment.save()
    return comment


@blueprint.route('/api/annotations/<id>/comments/<cid>', methods=['DELETE'])
@jwt_required()
def delete_comment_on_annotation(id, cid):
    annotation = Annotation.query.get(id)
    if not annotation:
        raise InvalidUsage.annotation_not_found()
    comment = annotation.comments.filter_by(id=cid, author=current_identity.profile).first()
    comment.delete()
    return '', 200