from utils import fix_encoding

def test():
    garbled = "ilustraИ›ie"
    expected = "ilustrație"
    result = fix_encoding(garbled)
    print(f"Input: {garbled}")
    print(f"Output: {result}")
    assert result == expected, f"Failed! Expected {expected}, got {result}"
    print("Test passed!")

if __name__ == "__main__":
    test()
