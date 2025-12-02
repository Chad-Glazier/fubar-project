from db.loose_compare import loose_compare

def test_loose_compare():
    assert loose_compare("Hello World", "hello") == True
    assert loose_compare("Hello World", "world") == True
    assert loose_compare("HELLO WORLD", "hello world") == True
    
    assert loose_compare("The quick brown fox", "fox quick") == True
    assert loose_compare("Python is great", "great python") == True
    
    assert loose_compare("partially matching", "art match") == True
    assert loose_compare("understanding", "under stand") == True
    
    assert loose_compare("Hello, World!", "world") == True
    assert loose_compare("Test-string", "test string") == True
    assert loose_compare("Multiple   spaces", "spaces") == True
    
    assert loose_compare("", "") == True
    assert loose_compare("Anything", "") == True
    assert loose_compare("", "something") == False
    
    assert loose_compare("Hello World", "hello there") == False
    assert loose_compare("Python", "java") == False
    
    assert loose_compare("MiXeD CaSe", "mixed case") == True
    
    assert loose_compare("Version 2.0", "version 2") == True