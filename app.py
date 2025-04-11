from aws_cdk import App
from peely.peely_stack import PeelyChatbotStack

app = App()

# Create the main Peely chatbot stack
PeelyChatbotStack(app, "PeelyChatbotStack")

app.synth()
