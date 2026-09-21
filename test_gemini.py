from dotenv import load_dotenv
from google import genai


def main() -> None:
    load_dotenv()

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Say hello in one short sentence.",
    )

    print(response.text)


if __name__ == "__main__":
    main()
