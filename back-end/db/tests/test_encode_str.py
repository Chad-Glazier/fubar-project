from db.encode_str import encode_str, decode_str

def test_encode_str():
	assert encode_str("asdf,123") == f"asdf%2C123"
	assert encode_str(",asdf") == f"%2Casdf"

def test_decode_str():
	strings = [
		"asdflkm,,23423423",
		"asdfmn3.234,l.",
		"jn...,,,234",
		",,fasdf,34,5l3"
	]
	for string in strings:
		assert decode_str(encode_str(string)) == string
