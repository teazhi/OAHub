from auth import generate_token

def generate_initial_tokens(count=5):
    tokens = [generate_token() for _ in range(count)]
    print("Generated tokens:", tokens)

if __name__ == "__main__":
    generate_initial_tokens()
