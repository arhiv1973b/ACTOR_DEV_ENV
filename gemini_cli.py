import os
import sys
from google import genai
from google.genai import errors

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Ошибка: Переменная окружения GEMINI_API_KEY не установлена.")
        sys.exit(1)
    client = genai.Client(api_key=api_key)
    default_model = "gemini-3.1-flash-lite"
    args = sys.argv[1:]
    if not args or args[0] == "interactive":
        print(f"--- Gemini CLI (Interactive) - Model: {default_model} ---")
        print("Введите 'exit' или 'quit' для выхода.\n")
        chat = client.chats.create(model=default_model)
        while True:
            try:
                user_input = input("Вы: ").strip()
                if not user_input: continue
                if user_input.lower() in ['exit', 'quit']:
                    print("Сессия завершена.")
                    break
                response = chat.send_message(user_input)
                print(f"Gemini: {response.text}\n")
            except errors.APIError as e:
                print(f"\nОшибка API ({e.code}): {e.message}\n")
            except (KeyboardInterrupt, EOFError):
                print("\nСессия прервана.")
                break
            except Exception as e:
                print(f"\nОшибка: {e}\n")
    else:
        model = default_model
        prompt = None
        if "-m" in args:
            try: model = args[args.index("-m") + 1]
            except IndexError: pass
        if "--model" in args:
            try: model = args[args.index("--model") + 1]
            except IndexError: pass
        if "-p" in args:
            try: prompt = args[args.index("-p") + 1]
            except IndexError: pass
        if "--prompt" in args:
            try: prompt = args[args.index("--prompt") + 1]
            except IndexError: pass
        if not prompt and args and not args[0].startswith("-"):
            prompt = " ".join(args)
        if not prompt:
            print("Использование: gemini -m <model> -p <prompt> или просто gemini")
            sys.exit(1)
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            print(response.text)
        except errors.APIError as e:
            print(f"Ошибка API ({e.code}): {e.message}")
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
