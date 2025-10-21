from encode_str import encode_str, decode_str, comma_replacement

def test_encode_str():
	assert encode_str("asdf,123") == f"asdf{comma_replacement}123"
	assert encode_str(",asdf") == f"{comma_replacement}asdf"

def test_decode_str():
	strings = [
		"asdflkm,,23423423",
		"asdfmn3.234,l.",
		"jn...,,,234",
		",,fasdf,34,5l3"
	]
	for string in strings:
		assert decode_str(encode_str(string)) == string