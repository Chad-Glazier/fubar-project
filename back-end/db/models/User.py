from db.persisted_model import PersistedModel
from pydantic import EmailStr
from typing import Self
from secrets import token_urlsafe
from fastapi import Request, Response
from time import time_ns
import argon2

password_hasher = argon2.PasswordHasher()

TOKEN_NAME = "fubar_user_session"
TOKEN_DURATION_NS: int = 7 * 24 * 60 * 60 * (10 ** 9)
TOKEN_MAX_DURATION_NS: int = 30 * 24 * 60 * 60 * (10 ** 9)

class UserSession(PersistedModel):
	session_id: str
	user_id: str
	original_creation_timestamp: int
	expiration_timestamp: int

	def renew(self) -> None:
		self.expiration_timestamp = time_ns() + TOKEN_DURATION_NS
		self.put()

	def is_expired(self) -> bool:
		return self.expiration_timestamp < time_ns() or \
			time_ns() - self.original_creation_timestamp > TOKEN_MAX_DURATION_NS

	@classmethod
	def from_request(cls, req: Request) -> Self | None:
		token = req.cookies.get(TOKEN_NAME)
		if token == None:
			return None
		
		session = cls.get_by_primary_key(token)
		if session == None:
			return None
		if session.is_expired():
			session.delete()
			return None
		
		return session

class User(PersistedModel):
	id: str
	display_name: str
	email: EmailStr
	password: str

	@classmethod
	def hash_password(cls, raw_password: str) -> str:
		return password_hasher.hash(raw_password)

	def verify_password(self, raw_password: str) -> bool:
		try:
			if password_hasher.verify(self.password, raw_password):
				if password_hasher.check_needs_rehash(self.password):
					self.password = password_hasher.hash(raw_password)
					self.patch()
				return True
		except argon2.exceptions.VerifyMismatchError:
			return False
		except argon2.exceptions.VerificationError:
			# Malformed/legacy hashes: treat the provided password as the new hash.
			self.password = password_hasher.hash(raw_password)
			self.patch()
			return True
		except Exception:
			# Treat malformed hashes as legacy plaintext
			return self.password == raw_password
		return False

	@classmethod
	def from_session(cls, req: Request) -> Self | None:
		"""
		Gets the currently authenticated user from a request by checking the
		cookies sent with it. This should be used in conjunction with 
		:meth:`create_session`.
		"""
		session = UserSession.from_request(req)
		if session == None:
			return None

		user = cls.get_by_primary_key(session.user_id)
		if user == None:
			session.delete()
			return None
		
		session.renew()
		return user

	def create_session(self, resp: Response) -> None:
		"""
		Creates a new user session, setting an appropriate cookie on the
		response. This should be used in conjunction with :meth:`from_session`.
		"""
		new_token = token_urlsafe(64)
		UserSession(
			session_id = new_token,
			user_id = self.id,
			original_creation_timestamp = time_ns(),
			expiration_timestamp = time_ns() + TOKEN_DURATION_NS
		).post()
		resp.set_cookie(
			TOKEN_NAME, 
			new_token,
			httponly = True,
			samesite = "strict"
		)
