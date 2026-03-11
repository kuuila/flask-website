from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from flask_socketio import SocketIO
from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
# 初始化扩展，但不绑定 app (解决循环引用)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///universe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-for-my-universe'

# --- 配置 ---
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'flashmud'
app.config['BASIC_AUTH_FORCE'] = False

db = SQLAlchemy(app)
basic_auth = BasicAuth(app)
socketio = SocketIO(app,cors_allowed_origins="*")