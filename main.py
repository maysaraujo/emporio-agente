"""CLI entry point: a simple chat loop with the Empório da Música agent."""

from agent.memory import Conversation


def main():
    print("Empório da Música — atendimento virtual")
    print("(digite 'sair' para encerrar)\n")

    conversation = Conversation()

    while True:
        user_message = input("Você: ").strip()

        if user_message.lower() in ("sair", "exit", "quit"):
            print("\nAté logo!")
            break

        if not user_message:
            continue

        answer = conversation.ask(user_message)
        print(f"\nAtendente: {answer}\n")


if __name__ == "__main__":
    main()
