from auth import generate_token, TOKEN_FILE
import json

def generate_initial_tokens(count=5):
    tokens = [generate_token() for _ in range(count)]
    print("Generated tokens:")
    for token in tokens:
        print(token)
    
    with open(TOKEN_FILE, "r") as file:
        saved_tokens = json.load(file)
        print("\nTokens currently saved in tokens.json:", saved_tokens)

if __name__ == "__main__":
    generate_initial_tokens()
