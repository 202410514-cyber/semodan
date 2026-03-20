from flask import Flask, request, redirect, url_for, render_template_string, session
from datetime import date
import random

app = Flask(__name__)
app.secret_key = "semodan-secret-key"

# ---------------- 데이터 ----------------
user_words = {}     # 사용자별 단어장
records = {}        # 사용자별 학습 기록
current_quiz = {}   # 사용자별 현재 퀴즈

# ---------------- HTML ----------------
HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>세상의 모든 단어</title>
<style>
* {
  box-sizing: border-box;
}
body {
  margin: 0;
  font-family: Arial;
  background: #f4f6fb;
}
header {
  background: #3f51b5;
  color: white;
  padding: 18px;
  text-align: center;
  font-size: 24px;
}
.container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 10px;
}
.row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.col {
  flex: 1;
  min-width: 320px;
}
.card {
  background: white;
  border-radius: 14px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}
.word {
  font-size: 48px;
  text-align: center;
  font-weight: bold;
  margin: 20px 0;
}
input, button {
  width: 100%;
  padding: 12px;
  margin-top: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
}
button {
  background: #3f51b5;
  color: white;
  font-weight: bold;
  border: none;
  cursor: pointer;
}
.right { color: green; font-weight: bold; }
.wrong { color: red; font-weight: bold; }
.small { color: #666; font-size: 14px; }
.word-list {
  line-height: 1.8;
}
.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
</head>

<body>
<header>📘 세상의 모든 단어</header>

<div class="container">

{% if not user %}
  <div class="card">
    <h2>🔑 로그인</h2>
    <form method="post" action="/login">
      <input name="user" placeholder="아이디 입력" required>
      <button>시작하기</button>
    </form>
  </div>
{% else %}

  <div class="card top">
    <b>👤 {{ user }}</b>
    <a href="/logout">로그아웃</a>
  </div>

  <div class="row">

    <!-- 단어장 -->
    <div class="col">
      <div class="card">
        <h2>📚 단어장</h2>
        <div class="word-list">
          {% for w in words %}
            {{ w.en }} - {{ w.ko }}<br>
          {% else %}
            단어 없음
          {% endfor %}
        </div>
      </div>

      <div class="card">
        <h2>➕ 단어 추가</h2>
        <form method="post" action="/add">
          <input name="en" placeholder="영어 단어" required>
          <input name="ko" placeholder="뜻 (한글)" required>
          <button>추가</button>
        </form>
      </div>
    </div>

    <!-- 퀴즈 -->
    <div class="col">
      <div class="card">
        <h2>🧠 단어 퀴즈</h2>

        {% if quiz %}
          <div class="word">{{ quiz.en }}</div>
          <form method="post" action="/quiz">
            <input name="answer" placeholder="뜻을 입력하세요">
            <button>확인</button>
          </form>
        {% endif %}

        {% if result %}
          <p class="{{ 'right' if result.ok else 'wrong' }}">
            {{ result.msg }}
          </p>
        {% endif %}
      </div>

      <div class="card">
        <h2>📅 오늘 학습 기록</h2>
        {% for d, ws in records.items() %}
          <b>{{ d }}</b><br>
          <span class="small">{{ ", ".join(ws) }}</span><br><br>
        {% else %}
          기록 없음
        {% endfor %}
      </div>
    </div>

  </div>

{% endif %}
</div>
</body>
</html>
"""

# ---------------- 기능 ----------------
def next_quiz(user):
    words = user_words.get(user, [])
    if words:
        current_quiz[user] = random.choice(words)

@app.route("/")
def home():
    user = session.get("user")
    if user:
        user_words.setdefault(user, [])
        records.setdefault(user, {})
        if user not in current_quiz:
            next_quiz(user)

    return render_template_string(
        HTML,
        user=user,
        words=user_words.get(user, []),
        quiz=current_quiz.get(user),
        records=records.get(user, {}),
        result=None
    )

@app.route("/login", methods=["POST"])
def login():
    user = request.form["user"]
    session["user"] = user
    user_words.setdefault(user, [])
    records.setdefault(user, {})
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/add", methods=["POST"])
def add():
    user = session["user"]
    user_words[user].append({
        "en": request.form["en"],
        "ko": request.form["ko"]
    })
    next_quiz(user)
    return redirect(url_for("home"))

@app.route("/quiz", methods=["POST"])
def quiz():
    user = session["user"]
    quiz = current_quiz[user]
    answer = request.form["answer"].strip()

    today = str(date.today())
    records[user].setdefault(today, [])

    if quiz["en"] not in records[user][today]:
        records[user][today].append(quiz["en"])

    ok = answer == quiz["ko"]
    result = {
        "ok": ok,
        "msg": "⭕ 정답!" if ok else f"❌ 오답 (정답: {quiz['ko']})"
    }

    next_quiz(user)

    return render_template_string(
        HTML,
        user=user,
        words=user_words[user],
        quiz=current_quiz.get(user),
        records=records[user],
        result=result
    )

if __name__ == "__main__":
    app.run(debug=True)
