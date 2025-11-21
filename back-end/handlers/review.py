from fastapi import APIRouter
from http import HTTPStatus

from db.models.UserReview import UserReview

review_router = APIRouter(prefix = "/review")


###############################################################################
# 
# The types that will be used by this router are defined below.
#



###############################################################################
# 
# The request handlers are defined below.
#

