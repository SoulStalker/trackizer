from flask import Flask, render_template

apple = Flask(__name__)

@apple.route('/')
def index():
    return 'Life of coder'

if __name__ == '__main__':
    apple.run(debug=True)


