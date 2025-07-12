import chainlit as cl


@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...

    # Send a response back to the user
    await cl.Message(
        content=f"Received: {message.content}",
    ).send()


# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return '<html>Hello World!</html>'

# if __name__ == '__main__':
#     app.run()
