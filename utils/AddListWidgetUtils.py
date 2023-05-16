from PyQt5.QtWidgets import (QWidget, QLabel, QListWidgetItem, QGridLayout,
                             QSizePolicy, QSpacerItem)
from datetime import datetime


class AddListWidgetUtils:

    @staticmethod
    def add_repo_to_list_widget(main_window, repos):
        for repo in repos:
            item = QListWidgetItem()
            widget = QWidget()
            layout = QGridLayout()

            #添加仓库名称
            name_label = QLabel(repo['name'], widget)
            name_label.setObjectName('name_label')
            layout.addWidget(name_label, 0, 0)

            # 添加仓库描述
            desc_label = QLabel(repo['description'], widget)
            desc_label.setObjectName('desc_label')
            desc_label.setMaximumWidth(main_window.listWidget.width())
            desc_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(desc_label, 1, 0, 2, 1)

            # 添加默认分支
            default_branch_label = QLabel(repo['default_branch'], widget)
            default_branch_label.setObjectName('default_branch_label')
            layout.addWidget(default_branch_label, 3, 0)

            # 添加是否为私有仓库
            private_label = QLabel(str(repo['private']), widget)
            private_label.setObjectName('private_label')
            layout.addWidget(private_label, 4, 0)

            #添加收藏者数量
            stargazers_count_label = QLabel(str(repo['stargazers_count']), widget)
            stargazers_count_label.setObjectName('stargazers_count_label')
            layout.addWidget(stargazers_count_label, 5, 0)

            # 添加观察者数量
            watchers_count_label = QLabel(str(repo['watchers_count']), widget)
            watchers_count_label.setObjectName('watchers_count_label')
            layout.addWidget(watchers_count_label, 6, 0)

            # 添加仓库创建时间
            created_at = datetime.strptime(repo['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            created_at_label = QLabel("创建时间"+created_at.strftime('%Y-%m-%d %H:%M:%S'), widget)
            created_at_label.setObjectName('created_at_label')
            layout.addWidget(created_at_label, 0, 1)

            # 添加spacer item
            spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            layout.addItem(spacer_item, 0, 2)

            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            main_window.listWidget.addItem(item)
            main_window.listWidget.setItemWidget(item, widget)