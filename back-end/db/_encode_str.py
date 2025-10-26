_comma_replacement = "%2C" # Same as the URI encoding replacement.

def _encode_str(string: str) -> str:
	"""
	We store strings in CSV files, so it's essential that the stored strings
	are encoded to avoid including actual commas. This function does that, and
	the correspoding `decode_str` function converts it back to its original
	form.
	"""
	return string.replace(",", _comma_replacement)

def _decode_str(encoded_string: str) -> str:
	"""
	Take a string that was originally encoded by `encode_str` and restore it
	to its original content (i.e., including commas).
	"""
	return encoded_string.replace(_comma_replacement, ",")
