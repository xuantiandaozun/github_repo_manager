import aiohttp
import logging

logging.basicConfig(filename='../log.log', level=logging.DEBUG, filemode='w', encoding='utf-8')


class GithubApiManager:
    def __init__(self, username, token):
        self.token = token
        self.username = username

    async def search_repos(self, text):
        async with aiohttp.ClientSession(headers={'Authorization': f'token {self.token}'}) as session:
            async with session.get(
                    f'https://api.github.com/search/repositories?q={text}&per_page=100&sort=updated&order=desc') as response:
                if response.status != 200:
                    return None
                json = await response.json()
                logging.debug(f"请求返回json{json}")
                repos = json['items']
                return repos

    async def load_repos(self):
        async with aiohttp.ClientSession(headers={'Authorization': f'token {self.token}'}) as session:
            async with session.get(
                    'https://api.github.com/user/repos?per_page=100&sort=created&direction=desc') as response:
                if response.status != 200:
                    return None
                repos = await response.json()
                return repos

    async def create_repo(self, data):
        async with aiohttp.ClientSession(headers={'Authorization': f'token {self.token}'}) as session:
            async with session.post('https://api.github.com/user/repos', json=data) as response:
                if response.status != 201:
                    return None
                repos = await response.json()
                return repos

    async def delete_repo(self, repo_name):
        async with aiohttp.ClientSession(headers={'Authorization': f'token {self.token}'}) as session:
            async with session.delete(f'https://api.github.com/repos/{self.username}/{repo_name}') as response:
                if response.status != 204:
                    return None
                return response

    async def edit_repo(self, repo_name, data):
        async with aiohttp.ClientSession(headers={'Authorization': f'token {self.token}'}) as session:
            async with session.patch(f'https://api.github.com/repos/{self.username}/{repo_name}',
                                     json=data) as response:
                if response.status != 200:
                    return None
                return response
