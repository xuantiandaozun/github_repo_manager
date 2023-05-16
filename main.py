import sys
import logging
import asyncio
import configparser

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QCheckBox,
                             QListWidget, QFrame, QAbstractItemView,
                             QMessageBox, QInputDialog)
from PyQt5.QtGui import QIcon
from manager.RepoManager import RepoManager
from manager.GithubApiManager import GithubApiManager
from utils.AddListWidgetUtils import AddListWidgetUtils

logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='w', encoding='utf-8')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置主窗口标题和图标
        self.setWindowTitle('GitHub 仓库管理器')
        self.setWindowIcon(QIcon('icon.png'))

        # 设置主窗口大小和样式
        self.setFixedSize(1000, 600)
        self.setStyleSheet('''
            QPushButton { font-size: 16px; padding: 5px 10px; }
            QLabel { font-size: 16px; }
            QLineEdit { font-size: 16px; }
            QTableView { font-size: 16px; }
        ''')
        # 读取配置文件
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.username = self.config.get('github', 'username')
        self.token = self.config.get('github', 'token')

        self.set_token()

        # 设置界面组件
        self.create_repo_button = QPushButton('新建仓库', self)
        self.delete_repo_button = QPushButton('删除仓库', self)
        self.edit_repo_button = QPushButton('编辑仓库', self)
        self.token_button = QPushButton('设置账户信息', self)
        self.token_label = QLabel('未设置账户信息', self)

        # 创建搜索框和按钮
        self.searchBox = QLineEdit()
        self.searchButton = QPushButton('查询')
        self.searchButton.clicked.connect(self.search_repos)
        # 创建复选框
        self.onlyMineCheckBox = QCheckBox('只查询本人仓库')
        self.onlyMineCheckBox.setChecked(True)  # 将默认值设置为“是”
        self.onlyMineCheckBox.stateChanged.connect(self.search_repos)
        # 列表  
        self.listWidget = QListWidget(self)
        self.listWidget.setFrameShape(QFrame.NoFrame)
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # 设置布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.create_repo_button)
        button_layout.addWidget(self.delete_repo_button)
        button_layout.addWidget(self.edit_repo_button)
        button_layout.addStretch()
        button_layout.addWidget(self.token_button)
        button_layout.addWidget(self.token_label)

        search_layout = QVBoxLayout()
        search_layout.addWidget(self.searchBox)
        search_layout.addWidget(self.searchButton)
        search_layout.addWidget(self.onlyMineCheckBox)

        top_layout = QHBoxLayout()
        top_layout.addLayout(search_layout)
        top_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.listWidget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.repoManager = RepoManager(self)

        # 设置信号和槽
        self.create_repo_button.clicked.connect(lambda: asyncio.run(self.repoManager.create_repo()))
        self.delete_repo_button.clicked.connect(lambda: asyncio.run(self.repoManager.delete_repo()))
        self.edit_repo_button.clicked.connect(lambda: asyncio.run(self.repoManager.edit_repo()))
        self.token_button.clicked.connect(self.set_token)

        self.github_api_manager = GithubApiManager(self.username, self.token)

        # 加载仓库列表
        asyncio.run(self.repoManager.load_repos())

    def set_token(self):
        if not self.username:
            self.username, ok = QInputDialog.getText(self, '设置用户名', '请输入GitHub用户名')
            if ok:
                self.config.set('github', 'username', self.username)
        if not self.token:
            self.token, ok = QInputDialog.getText(self, '设置访问令牌', '请输入 GitHub 访问令牌')
            if ok:
                self.config.set('github', 'token', self.token)

    def search_repos(self):
        if not self.token:
            return
        text = self.searchBox.text()
        if self.onlyMineCheckBox.isChecked():
            if not text:
                # 搜索内容为空就直接刷新页面
                asyncio.run(self.repoManager.load_repos())
                return
            repos = asyncio.run(self.github_api_manager.load_repos());
            filtered_repos = [];
            for repo in repos:
                if self.searchBox.text().lower() in repo['name'].lower():
                    filtered_repos.append(repo)
            repos = filtered_repos;
            self.listWidget.clear()
            AddListWidgetUtils.add_repo_to_list_widget(self, repos);

            return
        else:
            if not text:
                QMessageBox.warning(self, '警告', '搜索github仓库，搜索内容不能为空')
                return
            repos = asyncio.run(self.github_api_manager.search_repos(text));
            self.listWidget.clear()
            AddListWidgetUtils.add_repo_to_list_widget(self, repos);
            return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
