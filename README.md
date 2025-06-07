pip install haconiwa

haconiwa core init

haconiwa world create local-dev

haconiwa agent spawn boss
haconiwa agent spawn worker-a

# タスク作成
haconiwa task new feature-login

# エージェントにタスク割り当て
haconiwa task assign feature-login worker-a

# 進捗監視
haconiwa watch tail worker-a

git clone https://github.com/yourusername/haconiwa.git
cd haconiwa
python -m venv venv
source venv/bin/activate
pip install -e .[dev];