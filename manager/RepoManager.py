from PyQt5.QtWidgets import (QLabel, QProgressDialog,
                             QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt
from manager.GithubApiManager import GithubApiManager
from utils.AddListWidgetUtils import AddListWidgetUtils

import logging

logging.basicConfig(filename='../log.log', level=logging.DEBUG, filemode='w', encoding='utf-8')


class RepoManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.github_api_manager = GithubApiManager(self.main_window.username, self.main_window.token)

    async def load_repos(self, lang='en'):
        if not self.main_window.token:
            self.main_window.token_label.setText('未设置账户信息')
            self.main_window.listWidget.clear()
            return
        self.main_window.token_label.setText('已设置账户信息')

        repos = await self.github_api_manager.load_repos()
        if not repos:
            self.main_window.listWidget.clear()
            return
        self.main_window.listWidget.clear();
        AddListWidgetUtils.add_repo_to_list_widget(self.main_window, repos);

    async def create_repo(self):
        if not self.main_window.token:
            QMessageBox.warning(self.main_window, '警告', '请先设置账户信息！')
            return

        # 弹出对话框获取仓库名称
        repo_name, ok = QInputDialog.getText(self.main_window, '新建仓库', '请输入仓库名称')
        if not ok or not repo_name:
            return

        repos = await self.github_api_manager.create_repo({'name': repo_name});
        logging.debug(f'请求返回参数"{repos}"')

        if repos is not None:
            QMessageBox.information(self.main_window, '提示', '仓库创建成功！')
            await self.load_repos()
        else:
            QMessageBox.warning(self.main_window, '警告', '仓库创建失败！')

    async def edit_repo(self):
        if not self.main_window.token:
            QMessageBox.warning(self.main_window, '警告', '请先设置账户信息！')
            return

        # 获取选中的仓库名称
        selected_items = self.main_window.listWidget.selectedItems();
        if not selected_items:
            return
        widget = self.main_window.listWidget.itemWidget(selected_items[0])
        name_label = widget.findChild(QLabel, 'name_label')
        repo_name = name_label.text();

        desc_label = widget.findChild(QLabel, 'desc_label')
        des_str = desc_label.text();

        # 弹出对话框获取新的仓库名称和描述
        new_name, ok = QInputDialog.getText(self.main_window, '编辑仓库', '请输入新的仓库名称', text=repo_name)
        if not ok or not new_name:
            return
        new_description, ok = QInputDialog.getText(self.main_window, '编辑仓库', '请输入新的仓库描述', text=des_str)
        if not ok:
            return

        # 更新仓库
        response = await self.github_api_manager.edit_repo(repo_name,
                                                           {'name': new_name, 'description': new_description});

        if response is not None:
            QMessageBox.information(self.main_window, '提示', '仓库更新成功！')
            await self.load_repos()
        else:
            QMessageBox.warning(self.main_window, '警告', '仓库更新失败！')

    async def delete_repo(self):
        if not self.main_window.token:
            QMessageBox.warning(self.main_window, '警告', '请先设置账户信息！')
            return
        selected_items = self.main_window.listWidget.selectedItems();

        if not selected_items:
            return

        repo_names = []
        for selected_item in selected_items:
            if selected_item is None:
                return
            widget = self.main_window.listWidget.itemWidget(selected_item)
            name_label = widget.findChild(QLabel, 'name_label')
            repo_names.append(name_label.text())
        merged_repo_names = ', '.join(repo_names)

        # 弹出确认对话框
        reply = QMessageBox.question(self.main_window, '删除仓库', f'确定要删除仓库 {merged_repo_names} 吗？',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        total_count = len(selected_items)
        progress_dialog = QProgressDialog("删除仓库...", "取消", 0, total_count)
        progress_dialog.setWindowTitle("进度条")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setAutoClose(True)
        progress_dialog.setAutoReset(False)

        progress = 0

        for selected_item in selected_items:
            if selected_item is None:
                return
            if progress_dialog.wasCanceled():
                break
            widget = self.main_window.listWidget.itemWidget(selected_item)
            name_label = widget.findChild(QLabel, 'name_label')
            repo_name = name_label.text();
            repos = await self.github_api_manager.delete_repo(repo_name);
            if repos is None:
                QMessageBox.warning(self.main_window, '警告', '仓库删除失败！')
                return
            else:
                progress += 1
                progress_dialog.setLabelText(f"删除仓库 {repo_name}...")
                progress_dialog.setValue(progress)

        progress_dialog.close()
        QMessageBox.information(self.main_window, '提示', '仓库删除成功！')
        await self.load_repos()
