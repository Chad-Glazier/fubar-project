from models._encode_str import _encode_str, _decode_str, _comma_replacement

def test_encode_str():
	assert _encode_str("asdf,123") == f"asdf{_comma_replacement}123"
	assert _encode_str(",asdf") == f"{_comma_replacement}asdf"

def test_decode_str():
	strings = [
		"asdflkm,,23423423",
		"asdfmn3.234,l.",
		"jn...,,,234",
		",,fasdf,34,5l3"
	]
	for string in strings:
		assert _decode_str(_encode_str(string)) == string
