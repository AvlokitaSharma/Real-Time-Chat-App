import flet as ft

class Message():
    def __init__(self, user: str, text: str, message_type: str):
        self.user = user
        self.text = text
        self.message_type = message_type
        self.reactions = {'thumbs_up': 0, 'heart': 0, 'smile': 0}

def main(page: ft.Page):
    chat = ft.Column()
    new_message = ft.TextField()

    def on_message(message: Message):
        if message.message_type == "chat_message":
            chat.controls.append(ChatMessage(message))
        elif message.message_type == "login_message":
            chat.controls.append(ft.Text(message.text, italic=True, color=ft.colors.BLACK45, size=12))
        page.update()

    page.pubsub.subscribe(on_message)

    def send_click(e):
        page.pubsub.send_all(Message(user=page.session.get('user_name'), text=new_message.value, message_type="chat_message"))
        new_message.value = ""
        page.update()

    def unsend_click(e):
        if chat.controls:
            last_message = chat.controls[-1]
            if isinstance(last_message, ChatMessage) and last_message.message.user == page.session.get('user_name'):
                chat.controls.pop()
                page.update()

    user_name = ft.TextField(label="Enter your name")

    def join_click(e):
        if not user_name.value:
            user_name.error_text = "Name cannot be blank!"
            user_name.update()
        else:
            page.session.set("user_name", user_name.value)
            page.dialog.open = False
            page.pubsub.send_all(Message(user=user_name.value, text=f"{user_name.value} has joined the chat.", message_type="login_message"))
            page.update()

    page.dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Welcome!"),
        content=ft.Column([user_name], tight=True),
        actions=[ft.ElevatedButton(text="Join chat", on_click=join_click)],
        actions_alignment="end",
    )

    page.add(
        chat, 
        ft.Row([
            new_message, 
            ft.ElevatedButton("Send", on_click=send_click),
            ft.ElevatedButton("Unsend", on_click=unsend_click),
        ])
    )

class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = "start"
        self.controls = [
            ft.Text(f"{message.user}: {message.text}"),
            ReactionBar(message),
        ]

class ReactionBar(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.controls = [
            ReactionButton(message, 'thumbs_up', '👍'),
            ReactionButton(message, 'heart', '❤️'),
            ReactionButton(message, 'smile', '😊'),
        ]

class ReactionButton(ft.IconButton):
    def __init__(self, message: Message, reaction_type: str, icon: str):
        super().__init__(icon=icon, on_click=lambda e: self.react_to_message(message, reaction_type))

    def react_to_message(self, message: Message, reaction_type: str):
        message.reactions[reaction_type] += 1
        self.icon = f'{self.icon} {message.reactions[reaction_type]}'
        self.update()

ft.app(target=main, view=ft.WEB_BROWSER)
